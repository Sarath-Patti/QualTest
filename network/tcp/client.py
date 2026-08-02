"""TCP client interface for modem network communication.

Provides a socket client for sending commands and receiving responses from
the TCP modem simulator.
"""

from dataclasses import dataclass
import socket
from typing import Optional

from framework.logger import get_logger

logger = get_logger("Network.TCPClient")


@dataclass(frozen=True)
class TCPClientConfig:
    """Configuration parameters for TCP socket connections."""

    host: str = "127.0.0.1"
    port: int = 8080
    timeout_seconds: float = 5.0
    buffer_size: int = 4096


class TCPClient:
    """TCP socket client for communicating with modem servers."""

    def __init__(self, config: Optional[TCPClientConfig] = None) -> None:
        """Initializes TCPClient.

        Args:
            config: Optional TCPClientConfig instance.
        """
        self.config = config or TCPClientConfig()
        self._socket: Optional[socket.socket] = None
        self._is_connected: bool = False
        logger.debug("TCPClient initialized for target %s:%d", self.config.host, self.config.port)

    @property
    def is_connected(self) -> bool:
        """Indicates whether the socket connection is currently active."""
        return self._is_connected

    def connect(self) -> None:
        """Establishes a TCP connection to the host modem simulator."""
        if self._is_connected:
            return

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.config.timeout_seconds)
            self._socket.connect((self.config.host, self.config.port))
            self._is_connected = True
            logger.debug("TCP connected to %s:%d", self.config.host, self.config.port)
        except Exception as exc:
            self._is_connected = False
            if self._socket:
                self._socket.close()
                self._socket = None
            logger.error("Failed to connect TCP client to %s:%d: %s", self.config.host, self.config.port, exc)
            raise

    def send(self, data: bytes) -> int:
        """Sends raw bytes over the TCP socket.

        Args:
            data: Payload bytes to send.

        Returns:
            int: Number of bytes sent.
        """
        if not self._is_connected or not self._socket:
            raise RuntimeError("TCP client is not connected.")
        return self._socket.send(data)

    def receive(self, max_bytes: Optional[int] = None) -> bytes:
        """Receives raw bytes from the TCP socket.

        Args:
            max_bytes: Maximum bytes to read.

        Returns:
            bytes: Received payload.
        """
        if not self._is_connected or not self._socket:
            raise RuntimeError("TCP client is not connected.")
        buf_size = max_bytes or self.config.buffer_size
        return self._socket.recv(buf_size)

    def send_command(self, command: str) -> str:
        """Helper method to connect, send a command, receive the response, and disconnect.

        Args:
            command: Command string to send.

        Returns:
            str: Response string received from simulator.
        """
        was_connected = self._is_connected
        if not was_connected:
            self.connect()

        try:
            payload = (command.strip() + "\n").encode("utf-8")
            self.send(payload)
            response_bytes = self.receive()
            response_str = response_bytes.decode("utf-8", errors="replace").strip()
            return response_str
        finally:
            if not was_connected:
                self.disconnect()

    def disconnect(self) -> None:
        """Closes the TCP connection."""
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None
        self._is_connected = False
        logger.debug("TCP client disconnected.")
