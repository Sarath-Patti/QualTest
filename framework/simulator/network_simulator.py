"""Unified network simulator manager interface for QualTest framework.

Hides protocol-specific server implementation details behind a clean, unified API.
"""

from typing import Optional, TYPE_CHECKING

from framework.config import Settings, get_settings
from framework.logger import get_logger
from framework.simulator.base import BaseSimulator

if TYPE_CHECKING:
    from framework.simulator.failure_injector import FailureInjector

logger = get_logger("Simulator.Manager")


class NetworkSimulator:
    """High-level protocol-agnostic modem network simulator controller.

    Manages lifecycle of underlying TCP or UDP server instances.
    """

    def __init__(
        self,
        protocol: str = "TCP",
        host: Optional[str] = None,
        port: Optional[int] = None,
        response_delay_ms: Optional[float] = None,
        failure_injector: Optional["FailureInjector"] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        """Initializes NetworkSimulator controller.

        Args:
            protocol: Protocol selector ('TCP' or 'UDP').
            host: Binding host override.
            port: Binding port override.
            response_delay_ms: Response delay in milliseconds override.
            failure_injector: Optional FailureInjector instance.
            settings: Framework Settings instance.
        """
        cfg = settings or get_settings()
        self.protocol = protocol.upper().strip()
        self.host = host or "127.0.0.1"

        if port is not None:
            self.port = port
        else:
            self.port = 8080 if self.protocol == "TCP" else 8081

        self.response_delay_ms = (
            response_delay_ms if response_delay_ms is not None else 0.0
        )
        self.failure_injector = failure_injector

        self._server: Optional[BaseSimulator] = None
        self._init_server()

    def _init_server(self) -> None:
        """Instantiates the appropriate protocol server."""
        if self.protocol == "TCP":
            from network.tcp.server import TCPServer

            self._server = TCPServer(
                host=self.host,
                port=self.port,
                response_delay_ms=self.response_delay_ms,
                failure_injector=self.failure_injector,
            )
        elif self.protocol == "UDP":
            from network.udp.server import UDPServer

            self._server = UDPServer(
                host=self.host,
                port=self.port,
                response_delay_ms=self.response_delay_ms,
                failure_injector=self.failure_injector,
            )
        else:
            raise ValueError(f"Unsupported simulator protocol: {self.protocol}")

    def set_failure_injector(self, failure_injector: Optional["FailureInjector"]) -> None:
        """Sets the failure injector instance on the underlying server.

        Args:
            failure_injector: FailureInjector instance.
        """
        self.failure_injector = failure_injector
        if self._server:
            self._server.set_failure_injector(failure_injector)

    @property
    def is_running(self) -> bool:
        """Indicates whether the underlying network server is running.

        Returns:
            bool: Running state flag.
        """
        return self._server.is_running if self._server else False

    def start(self) -> None:
        """Starts the underlying network server."""
        if self._server:
            logger.info(
                "Starting %s Network Simulator on %s:%d (delay: %.1fms, failure_injection: %s)...",
                self.protocol,
                self.host,
                self.port,
                self.response_delay_ms,
                "ENABLED" if (self.failure_injector and self.failure_injector.enabled) else "DISABLED",
            )
            self._server.start()

    def stop(self) -> None:
        """Stops the underlying network server gracefully."""
        if self._server and self._server.is_running:
            logger.info("Shutting down %s Network Simulator...", self.protocol)
            self._server.stop()
