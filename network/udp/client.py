"""UDP client interface for modem network communication.

Provides a datagram socket client for sending commands and receiving responses from
the UDP modem simulator.
"""

import socket
from dataclasses import dataclass

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

    def __init__(self, config: UDPClientConfig | None = None) -> None:
        """Initializes UDPClient.

        Args:
            config: Optional UDPClientConfig settings.
        """
        self.config = config or UDPClientConfig()
        self._socket: socket.socket | None = None
        self._init_socket()
        logger.debug(
            "UDPClient initialized for target %s:%d", self.config.host, self.config.port
        )

    def _init_socket(self) -> None:
        """Creates and configures underlying UDP socket."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.settimeout(self.config.timeout_seconds)

    def send_to(self, data: bytes, target: tuple[str, int] | None = None) -> int:
        """Sends a UDP datagram to the target address.

        Args:
            data: Payload bytes to send.
            target: Optional (host, port) tuple. Defaults to config host/port.

        Returns:
            int: Number of bytes sent.
        """
        if not self._socket:
            self._init_socket()
        assert self._socket is not None
        dest = target or (self.config.host, self.config.port)
        return self._socket.sendto(data, dest)

    def send(self, data: bytes) -> int:
        """Alias method to send UDP payload to configured target."""
        return self.send_to(data)

    def receive_from(
        self, max_bytes: int | None = None
    ) -> tuple[bytes, tuple[str, int]]:
        """Receives a UDP datagram.

        Args:
            max_bytes: Maximum payload bytes to read.

        Returns:
            tuple[bytes, tuple[str, int]]: (data, (host, port)) tuple.
        """
        if not self._socket:
            self._init_socket()
        assert self._socket is not None
        buf_size = max_bytes or self.config.buffer_size
        return self._socket.recvfrom(buf_size)

    def receive(self, max_bytes: int | None = None) -> bytes:
        """Alias method to receive UDP payload."""
        data, _ = self.receive_from(max_bytes)
        return data

    def send_command(self, command: str, target: tuple[str, int] | None = None) -> str:
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
