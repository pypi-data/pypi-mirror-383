import torch
import torch.nn as nn
from typing import Callable, Dict, List, Optional, Tuple


class HydrologicalModel(nn.Module):
    """
    仅包含水文模型运行引擎，不依赖 SymPy。由外部提供编译后的
    flux_calculator 与 state_updater 以及元数据（名称、边界等）。
    """

    def __init__(
        self,
        *,
        hru_num: int,
        state_names: List[str],
        forcing_names: List[str],
        parameter_names: List[str],
        flux_names: List[str],
        parameter_bounds: Dict[str, Tuple[float, float]],
        flux_calculator: Callable,
        state_updater: Callable,
        dtype: torch.dtype=torch.float32,
        input_names: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.hru_num = hru_num
        self.dtype = dtype

        self.state_names = state_names
        self.forcing_names = forcing_names
        self.parameter_names = parameter_names
        self.flux_names = flux_names
        self.input_names = input_names
        self.parameter_bounds = parameter_bounds

        self.flux_calculator = flux_calculator
        self.state_updater = state_updater

        # 索引映射
        self.flux_map: Dict[str, int] = {name: i for i, name in enumerate(self.flux_names)}
        self.state_map: Dict[str, int] = {name: i for i, name in enumerate(self.state_names)}

        self._initialize_parameters()

    def _initialize_parameters(self) -> None:
        """初始化可训练参数边界缓存张量。"""
        min_bounds_list: List[float] = []
        max_bounds_list: List[float] = []
        for name in self.parameter_names:
            bounds = self.parameter_bounds.get(name)
            if bounds is None:
                raise ValueError(f"Parameter '{name}' must have bounds provided.")
            min_b, max_b = bounds
            min_bounds_list.append(min_b)
            max_bounds_list.append(max_b)

        self.register_buffer("min_bounds", torch.tensor(min_bounds_list, dtype=self.dtype))
        self.register_buffer("max_bounds", torch.tensor(max_bounds_list, dtype=self.dtype))

    def _get_initial_state(self) -> torch.Tensor:
        """
        Returns the initial state of the model.

        The initial state is a PyTorch tensor of shape (hru_num, num_state_variables).
        By default, all state variables are initialized to 0.0.

        Returns:
            torch.Tensor: A tensor representing the initial state.
        """
        num_state_variables = len(self.state_names)
        return torch.zeros(self.hru_num, num_state_variables, dtype=self.dtype)

    def _transform_parameters(self, unconstrained_params: torch.Tensor) -> torch.Tensor:
        """Transforms a tensor of unconstrained parameters to their bounded physical values."""
        return (
            self.min_bounds + (self.max_bounds - self.min_bounds) * unconstrained_params
        )

    def _core(
        self,
        forcings: torch.Tensor,
        states: torch.Tensor,
        parameters: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Executes one time step for multiple parallel units (HRUs).
        """
        forcing_values = forcings.unbind(-1)
        state_values = states.unbind(-1)
        param_values = parameters.unbind(-1)

        flux_outputs_tuple = self.flux_calculator(
            state_values, forcing_values, param_values
        )
        flux_outputs = torch.stack(flux_outputs_tuple, dim=-1)

        flux_values = flux_outputs.unbind(-1)
        new_states_tuple = self.state_updater(
            state_values, flux_values, forcing_values, param_values
        )
        new_states = torch.stack(new_states_tuple, dim=-1)

        torch.clamp_(new_states, min=0.0)

        return flux_outputs, new_states

    def _process_parameters(
        self,
        parameters: torch.Tensor,
        forcings_shape: Tuple[int, int, int, int],
        device: torch.device,
    ) -> torch.Tensor:
        """
        Validates, transforms, and prepares model parameters for the simulation loop.

        Args:
            parameters: An optional tensor of external parameters. If None, uses internal model parameters.
            timelen: The length of the time dimension for the simulation.
            device: The torch device (e.g., 'cpu' or 'cuda') to place new tensors on.

        Returns:
            A tensor of transformed parameters ready for the simulation, with a time dimension.
        """
        T, B, H, F = forcings_shape
        expected_dynamic_shape = (T, B, H, len(self.parameter_names))
        expected_static_shape = (B, H, len(self.parameter_names))
        if (parameters.shape != expected_dynamic_shape) & (
            parameters.shape != expected_static_shape
        ):
            raise ValueError(
                f"Provided parameters have shape {parameters.shape}, "
                + f"but expected dynamic shape: {expected_dynamic_shape} or static shape: {expected_static_shape}"
            )
        # Apply transformations (e.g., sigmoid) to ensure parameters are in a valid range
        transformed_parameters = self._transform_parameters(parameters)

        # Ensure parameters have a time dimension, repeating if they are static
        if len(transformed_parameters.shape) == 4:
            pass
        elif len(transformed_parameters.shape) == 3:
            transformed_parameters = transformed_parameters.unsqueeze(0).repeat(
                T, 1, 1, 1
            )
        return transformed_parameters

    def forward(
        self,
        forcings: torch.Tensor,
        states: Optional[torch.Tensor] = None,
        parameters: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Runs the full time-series simulation.

        Args:
            forcings: A tensor of input forcing data with shape [T, B, H, F],
                      where T=time, B=basins, H=HRUs, F=features.
            states: A tensor of the initial system states with shape [B, H, S],
                    where S is the number of states.
            parameters: An optional tensor of model parameters to override internal ones.

        Returns:
            A tuple containing:
            - torch.Tensor: The time series of calculated fluxes.
            - torch.Tensor: The time series of simulated states.
        """
        # time step, basin num, hru num, feature dim
        T, B, H, F = forcings.shape

        # Correctly get device from an existing tensor
        device = forcings.device

        transformed_parameters = self._process_parameters(
            parameters, forcings.shape, device
        )

        fluxes_placeholder = torch.zeros((T, B, H, len(self.flux_names)), device=device)
        states_placeholder = torch.zeros(
            (T, B, H, len(self.state_names)), device=device
        )

        if states is None:
            states = self._get_initial_state()
        current_states = torch.clone(states)

        for i in range(T):
            fluxes_, states_ = self._core(
                forcings[i, :, :, :], current_states, transformed_parameters[i, :, :, :]
            )
            fluxes_placeholder[i, :, :, :] = fluxes_
            states_placeholder[i, :, :, :] = states_
            current_states = states_  # Update states for the next iteration

        return fluxes_placeholder, states_placeholder
