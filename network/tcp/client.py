"""TCP client interface for modem network communication.

Defines the contract for TCP socket connections to physical or simulated modems.
Business logic omitted as per v0.1 milestone specification.
"""

from dataclasses import dataclass
from typing import Optional

from framework.logger import get_logger

logger = get_logger("Network.TCP")


@dataclass(frozen=True)
class TCPClientConfig:
    """Configuration parameters for TCP socket connections."""

    host: str = "127.0.0.1"
    port: int = 8080
    timeout_seconds: float = 5.0
    buffer_size: int = 4096


class TCPClient:
    """TCP socket client interface."""

    def __init__(self, config: Optional[TCPClientConfig] = None) -> None:
        """Initializes TCPClient interface.

        Args:
            config: TCP client configuration parameters.
        """
        self.config = config or TCPClientConfig()
        self._is_connected: bool = False
        logger.debug("TCPClient interface initialized.")

    @property
    def is_connected(self) -> bool:
        """Indicates whether socket connection is established.

        Returns:
            bool: Connection state flag.
        """
        return self._is_connected

    def connect(self) -> None:
        """Establishes a TCP connection to the host modem.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError("TCP networking is not implemented in v0.1.")

    def send(self, data: bytes) -> int:
        """Sends raw bytes over the TCP socket.

        Args:
            data: Payload bytes to send.

        Returns:
            int: Number of bytes sent.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError("TCP networking is not implemented in v0.1.")

    def receive(self, max_bytes: Optional[int] = None) -> bytes:
        """Receives raw bytes from the TCP socket.

        Args:
            max_bytes: Maximum bytes to read.

        Returns:
            bytes: Received payload.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError("TCP networking is not implemented in v0.1.")

    def disconnect(self) -> None:
        """Closes the TCP connection.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError("TCP networking is not implemented in v0.1.")
