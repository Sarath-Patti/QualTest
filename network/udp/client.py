"""UDP client interface for modem network communication.

Provides a datagram socket client for sending commands and receiving responses from
the UDP modem simulator.
"""

from dataclasses import dataclass
import socket
from typing import Optional, Tuple

from framework.logger import get_logger

logger = get_logger("Network.UDPClient")


@dataclass(frozen=True)
class UDPClientConfig:
    """Configuration parameters for UDP socket communication."""

    host: str = "127.0.0.1"
    port: int = 8081
    timeout_seconds: float = 5.0
    buffer_size: int = 4096


class UDPClient:
    """UDP datagram socket client."""

    def __init__(self, config: Optional[UDPClientConfig] = None) -> None:
        """Initializes UDPClient.

        Args:
            config: Optional UDPClientConfig settings.
        """
        self.config = config or UDPClientConfig()
        self._socket: Optional[socket.socket] = None
        self._init_socket()
        logger.debug("UDPClient initialized for target %s:%d", self.config.host, self.config.port)

    def _init_socket(self) -> None:
        """Creates and configures underlying UDP socket."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.settimeout(self.config.timeout_seconds)

    def send_to(self, data: bytes, target: Optional[Tuple[str, int]] = None) -> int:
        """Sends a UDP datagram to the target address.

        Args:
            data: Payload bytes to send.
            target: Optional (host, port) tuple. Defaults to config host/port.

        Returns:
            int: Number of bytes sent.
        """
        if not self._socket:
            self._init_socket()
        dest = target or (self.config.host, self.config.port)
        return self._socket.sendto(data, dest)

    def receive_from(self, max_bytes: Optional[int] = None) -> Tuple[bytes, Tuple[str, int]]:
        """Receives a UDP datagram.

        Args:
            max_bytes: Maximum payload bytes to read.

        Returns:
            Tuple[bytes, Tuple[str, int]]: (data, (host, port)) tuple.
        """
        if not self._socket:
            self._init_socket()
        buf_size = max_bytes or self.config.buffer_size
        return self._socket.recvfrom(buf_size)

    def send_command(
        self, command: str, target: Optional[Tuple[str, int]] = None
    ) -> str:
        """Sends a command string over UDP and returns the response string.

        Args:
            command: Command string to send.
            target: Optional target (host, port) tuple.

        Returns:
            str: Response string received from simulator.
        """
        payload = (command.strip() + "\n").encode("utf-8")
        self.send_to(payload, target)
        data, _ = self.receive_from()
        return data.decode("utf-8", errors="replace").strip()

    def close(self) -> None:
        """Closes the UDP socket."""
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None
        logger.debug("UDP client socket closed.")
