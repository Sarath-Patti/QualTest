"""Simulator package for wireless modem emulation, network simulation, and failure injection."""

from framework.simulator.base import (
    DEFAULT_MODEM_RESPONSES,
    UNKNOWN_COMMAND_RESPONSE,
    BaseSimulator,
)
from framework.simulator.failure_injector import (
    FailureAction,
    FailureConfig,
    FailureInjector,
)
from framework.simulator.network_simulator import NetworkSimulator
from framework.simulator.simulator import (
    ModemSimulator,
    ModemState,
    SimulatorConfig,
)

__all__ = [
    "BaseSimulator",
    "NetworkSimulator",
    "ModemSimulator",
    "SimulatorConfig",
    "ModemState",
    "FailureInjector",
    "FailureConfig",
    "FailureAction",
    "DEFAULT_MODEM_RESPONSES",
    "UNKNOWN_COMMAND_RESPONSE",
]
