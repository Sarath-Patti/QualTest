"""Wireless modem simulator interface.

Defines the contract for simulating wireless modem behavior, AT command responses,
and RF network registration states.
Business logic omitted as per v0.1 milestone specification.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from framework.logger import get_logger

logger = get_logger("Simulator")


class ModemState(Enum):
    """Possible state enumeration for the modem simulator."""

    POWER_OFF = auto()
    INITIALIZING = auto()
    SEARCHING_NETWORK = auto()
    REGISTERED_HOME = auto()
    REGISTERED_ROAMING = auto()
    CONNECTED_DATA = auto()
    FAULT = auto()


@dataclass
class SimulatorConfig:
    """Configuration settings for modem simulator behavior."""

    imei: str = "359281080000000"
    iccid: str = "89014103211118510720"
    model_name: str = "SimModem-X55"
    firmware_version: str = "v1.0.0-mock"


class ModemSimulator:
    """Interface for simulating modem hardware responses and state transitions."""

    def __init__(self, config: Optional[SimulatorConfig] = None) -> None:
        """Initializes the ModemSimulator interface.

        Args:
            config: Simulator configuration settings.
        """
        self.config = config or SimulatorConfig()
        self._state = ModemState.POWER_OFF
        logger.debug("ModemSimulator interface initialized.")

    @property
    def current_state(self) -> ModemState:
        """Returns the current simulated state of the modem.

        Returns:
            ModemState: Current modem state.
        """
        return self._state

    def send_at_command(self, command: str) -> str:
        """Sends an AT command string to the simulated modem interface.

        Args:
            command: AT command string (e.g., 'AT+CSQ').

        Returns:
            str: Simulated modem response string.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError("Modem simulator logic is not implemented in v0.1.")

    def set_network_state(self, state: ModemState) -> None:
        """Sets the simulated modem network registration state.

        Args:
            state: Target ModemState to simulate.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError("Modem simulator state changes are not implemented in v0.1.")
