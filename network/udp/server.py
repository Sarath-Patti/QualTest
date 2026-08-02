"""UDP simulator server implementation.

Provides a datagram UDP socket server emulating modem communication.
Handles incoming datagrams, command processing, latency simulation,
and graceful shutdown.
"""

import socket
import threading
from typing import Optional

from framework.logger import get_logger
from framework.simulator.base import BaseSimulator

logger = get_logger("Network.UDPServer")


class UDPServer(BaseSimulator):
    """UDP modem network simulator server.

    Attributes:
        host: IP address to bind server.
        port: Port number to bind server.
        response_delay_ms: Latency delay in milliseconds before returning responses.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8081,
        response_delay_ms: float = 0.0,
    ) -> None:
        """Initializes UDPServer.

        Args:
            host: Binding host IP address.
            port: Binding port number.
            response_delay_ms: Simulated delay in milliseconds.
        """
        super().__init__(host=host, port=port, response_delay_ms=response_delay_ms)
        self._server_socket: Optional[socket.socket] = None
        self._listener_thread: Optional[threading.Thread] = None
        self._is_running: bool = False
        self._lock: threading.Lock = threading.Lock()

    @property
    def is_running(self) -> bool:
        """Indicates if the UDP server is running.

        Returns:
            bool: Running flag.
        """
        return self._is_running

    def start(self) -> None:
        """Starts the UDP server listener thread."""
        with self._lock:
            if self._is_running:
                logger.warning("UDP simulator server is already running.")
                return

            try:
                self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self._server_socket.bind((self.host, self.port))
                self._server_socket.settimeout(1.0)
                self._is_running = True
            except Exception as exc:
                logger.error("Failed to start UDP server on %s:%d: %s", self.host, self.port, exc)
                self._cleanup_socket()
                raise

            logger.info("Starting UDP simulator server on %s:%d", self.host, self.port)

            self._listener_thread = threading.Thread(
                target=self._listen_loop, name="UDPServerListener", daemon=True
            )
            self._listener_thread.start()

    def _listen_loop(self) -> None:
        """Background thread receiving UDP datagrams."""
        while self._is_running and self._server_socket:
            try:
                data, addr = self._server_socket.recvfrom(4096)
            except socket.timeout:
                continue
            except Exception:
                if not self._is_running:
                    break
                logger.debug("UDP receive loop interrupted.")
                break

            command = data.decode("utf-8", errors="replace").strip()
            if not command:
                continue

            logger.info("Received UDP command: '%s' from %s:%d", command, addr[0], addr[1])
            response = self.process_command(command)
            logger.info("Sent UDP response: '%s' to %s:%d", response, addr[0], addr[1])

            try:
                payload = (response + "\n").encode("utf-8")
                self._server_socket.sendto(payload, addr)
            except Exception as exc:
                logger.error("Error sending UDP response to %s:%d: %s", addr[0], addr[1], exc)

    def stop(self) -> None:
        """Stops the UDP server gracefully."""
        with self._lock:
            if not self._is_running:
                return
            logger.info("Stopping UDP simulator server...")
            self._is_running = False

        self._cleanup_socket()

        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=2.0)

        logger.info("UDP simulator server stopped.")

    def _cleanup_socket(self) -> None:
        """Closes master UDP socket."""
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None
