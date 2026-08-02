"""Base simulator abstraction for QualTest modem simulation.

Provides standard modem command mapping, response delay handling, failure injection support,
and abstract interface methods for protocol-specific simulator servers.
"""

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from framework.logger import get_logger

if TYPE_CHECKING:
    from framework.simulator.failure_injector import FailureInjector

logger = get_logger("Simulator.Base")

# Standard modem event response mappings
DEFAULT_MODEM_RESPONSES: dict[str, str] = {
    "ATTACH_REQUEST": "ATTACH_ACCEPT",
    "DETACH_REQUEST": "DETACH_ACCEPT",
    "PING": "PONG",
    "STATUS": "MODEM_READY",
}

UNKNOWN_COMMAND_RESPONSE: str = "UNKNOWN_COMMAND"


class BaseSimulator(ABC):
    """Abstract base class for all modem network simulators.

    Attributes:
        host: Simulator binding host IP address.
        port: Simulator binding network port.
        response_delay_ms: Simulated processing latency in milliseconds.
        failure_injector: Optional FailureInjector instance.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8080,
        response_delay_ms: float = 0.0,
        failure_injector: "FailureInjector | None" = None,
    ) -> None:
        """Initializes the base simulator interface.

        Args:
            host: Target binding IP address.
            port: Target binding port number.
            response_delay_ms: Simulated delay in milliseconds.
            failure_injector: Optional FailureInjector instance.
        """
        self.host = host
        self.port = port
        self.response_delay_ms = response_delay_ms
        self.failure_injector = failure_injector
        self._custom_handlers: dict[str, str] = dict(DEFAULT_MODEM_RESPONSES)

    def set_failure_injector(self, failure_injector: "FailureInjector | None") -> None:
        """Attaches a failure injector engine to the simulator.

        Args:
            failure_injector: FailureInjector instance.
        """
        self.failure_injector = failure_injector

    def register_command_handler(self, command: str, response: str) -> None:
        """Registers or overrides a simulated modem command response mapping.

        Args:
            command: Input command string.
            response: Expected response string.
        """
        self._custom_handlers[command.strip()] = response.strip()

    def process_command(self, command_str: str) -> str:
        """Processes an incoming modem command string and returns the simulated response.

        Applies configured response latency if response_delay_ms > 0.

        Args:
            command_str: Raw command payload received from client.

        Returns:
            str: Simulated modem response string.
        """
        cmd_clean = command_str.strip()

        # Apply configurable response delay if specified
        if self.response_delay_ms > 0:
            time.sleep(self.response_delay_ms / 1000.0)

        # Dispatch command
        response = self._custom_handlers.get(cmd_clean, UNKNOWN_COMMAND_RESPONSE)
        return response

    @property
    @abstractmethod
    def is_running(self) -> bool:
        """Indicates whether the simulator server is currently active.

        Returns:
            bool: True if running.
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """Starts the simulator server."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stops the simulator server gracefully."""
        pass
