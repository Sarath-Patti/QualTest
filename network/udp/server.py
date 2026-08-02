"""UDP simulator server implementation.

Provides a datagram UDP socket server emulating modem communication.
Handles incoming datagrams, command processing, latency simulation,
failure injection, and graceful shutdown.
"""

import socket
import threading

from framework.logger import get_logger
from framework.simulator.base import BaseSimulator
from framework.simulator.failure_injector import FailureAction, FailureInjector

logger = get_logger("Network.UDPServer")

DEFAULT_UDP_PORT: int = 8081
UDP_BUFFER_SIZE: int = 4096
UDP_SOCKET_TIMEOUT: float = 1.0


class UDPServer(BaseSimulator):
    """UDP modem network simulator server.

    Attributes:
        host: IP address to bind server.
        port: Port number to bind server.
        response_delay_ms: Latency delay in milliseconds before returning responses.
        failure_injector: Optional FailureInjector instance.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = DEFAULT_UDP_PORT,
        response_delay_ms: float = 0.0,
        failure_injector: FailureInjector | None = None,
    ) -> None:
        """Initializes UDPServer.

        Args:
            host: Binding host IP address.
            port: Binding port number.
            response_delay_ms: Simulated delay in milliseconds.
            failure_injector: Optional FailureInjector instance.
        """
        super().__init__(
            host=host,
            port=port,
            response_delay_ms=response_delay_ms,
            failure_injector=failure_injector,
        )
        self._server_socket: socket.socket | None = None
        self._listener_thread: threading.Thread | None = None
        self._is_running: bool = False
        self._lock: threading.Lock = threading.Lock()

    @property
    def is_running(self) -> bool:
        """Indicates if the UDP server is running."""
        return self._is_running

    def start(self) -> None:
        """Starts the UDP simulator server in a background thread."""
        with self._lock:
            if self._is_running:
                logger.warning(
                    "UDP server is already running on %s:%d.", self.host, self.port
                )
                return

            try:
                self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self._server_socket.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
                )
                self._server_socket.bind((self.host, self.port))
                self._server_socket.settimeout(UDP_SOCKET_TIMEOUT)
                self._is_running = True
            except Exception as exc:
                logger.error(
                    "Failed to bind UDP server on %s:%d: %s", self.host, self.port, exc
                )
                self.stop()
                raise

            self._listener_thread = threading.Thread(
                target=self._listen_loop,
                name="UDPServerListener",
                daemon=True,
            )
            self._listener_thread.start()
            logger.info(
                "UDP Simulator Server started listening on %s:%d", self.host, self.port
            )

    def _receive_udp_datagram(self) -> tuple[str, tuple[str, int]] | None:
        """Receives a single UDP datagram from the server socket."""
        if not self._server_socket:
            return None

        try:
            data, client_addr = self._server_socket.recvfrom(UDP_BUFFER_SIZE)
            cmd_str = data.decode("utf-8", errors="replace").strip()
            if not cmd_str:
                return None
            return cmd_str, client_addr
        except TimeoutError:
            return None
        except Exception:
            if not self._is_running:
                return None
            logger.debug("UDP recvfrom interrupted.")
            return None

    def _process_udp_command(self, cmd_str: str, client_addr: tuple[str, int]) -> None:
        """Evaluates failure injection and sends UDP response for a command."""
        logger.info(
            "UDP Received datagram from %s:%d: '%s'",
            client_addr[0],
            client_addr[1],
            cmd_str,
        )

        action = FailureAction.NONE
        payload = None
        if self.failure_injector and self.failure_injector.enabled:
            action, payload = self.failure_injector.evaluate_failure(cmd_str)

        if action == FailureAction.DISCONNECT:
            logger.warning(
                "Failure Action: Ignoring UDP datagram from %s:%d (Disconnect simulation)",
                client_addr[0],
                client_addr[1],
            )
            return

        if action == FailureAction.TIMEOUT:
            logger.warning(
                "Failure Action: Suppressing UDP response for %s:%d (Timeout simulation)",
                client_addr[0],
                client_addr[1],
            )
            return

        if action == FailureAction.DROP_PACKET:
            logger.warning(
                "Failure Action: Dropping UDP response packet for %s:%d",
                client_addr[0],
                client_addr[1],
            )
            return

        if action == FailureAction.MALFORMED_RESPONSE:
            resp_str = str(payload)
        else:
            resp_str = self.process_command(cmd_str)

        out_bytes = (resp_str + "\n").encode("utf-8")
        if self._server_socket:
            try:
                self._server_socket.sendto(out_bytes, client_addr)
                logger.info(
                    "UDP Sent response to %s:%d: '%s'",
                    client_addr[0],
                    client_addr[1],
                    resp_str,
                )
            except Exception as exc:
                logger.error(
                    "Failed to send UDP response to %s:%d: %s",
                    client_addr[0],
                    client_addr[1],
                    exc,
                )

    def _listen_loop(self) -> None:
        """Background thread listening for incoming UDP datagrams."""
        while self._is_running:
            recv_result = self._receive_udp_datagram()
            if recv_result is None:
                continue

            cmd_str, client_addr = recv_result
            self._process_udp_command(cmd_str, client_addr)

    def stop(self) -> None:
        """Stops the UDP simulator server gracefully."""
        with self._lock:
            if not self._is_running:
                return
            self._is_running = False

        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None

        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=UDP_SOCKET_TIMEOUT)

        logger.info("UDP Simulator Server stopped.")
