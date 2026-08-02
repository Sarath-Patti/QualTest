"""UDP client interface for modem network communication.

Defines the contract for UDP socket communication with physical or simulated modems.
Business logic omitted as per v0.1 milestone specification.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

from framework.logger import get_logger

logger = get_logger("Network.UDP")


@dataclass(frozen=True)
class UDPClientConfig:
    """Configuration parameters for UDP socket communication."""

    host: str = "127.0.0.1"
    port: int = 8081
    timeout_seconds: float = 5.0
    buffer_size: int = 4096


class UDPClient:
    """UDP datagram socket client interface."""

    def __init__(self, config: Optional[UDPClientConfig] = None) -> None:
        """Initializes UDPClient interface.

        Args:
            config: UDP client configuration parameters.
        """
        self.config = config or UDPClientConfig()
        logger.debug("UDPClient interface initialized.")

    def send_to(self, data: bytes, target: Optional[Tuple[str, int]] = None) -> int:
        """Sends a UDP datagram to target host and port.

        Args:
            data: Payload bytes to send.
            target: (host, port) tuple override.

        Returns:
            int: Number of bytes sent.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError("UDP networking is not implemented in v0.1.")

    def receive_from(self, max_bytes: Optional[int] = None) -> Tuple[bytes, Tuple[str, int]]:
        """Receives a UDP datagram.

        Args:
            max_bytes: Maximum payload bytes to receive.

        Returns:
            Tuple[bytes, Tuple[str, int]]: (data, (host, port)) tuple.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError("UDP networking is not implemented in v0.1.")

    def close(self) -> None:
        """Closes the UDP socket.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError("UDP networking is not implemented in v0.1.")
