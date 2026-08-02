"""TCP simulator server implementation.

Provides a multithreaded TCP socket server emulating modem communication.
Handles client connection lifecycle, command processing, latency simulation,
failure injection, and graceful shutdown.
"""

import socket
import threading

from framework.logger import get_logger
from framework.simulator.base import BaseSimulator
from framework.simulator.failure_injector import FailureAction, FailureInjector

logger = get_logger("Network.TCPServer")

DEFAULT_TCP_PORT: int = 8080
TCP_BUFFER_SIZE: int = 4096
TCP_CLIENT_TIMEOUT: float = 2.0
TCP_LISTEN_BACKLOG: int = 128
SOCKET_ACCEPT_TIMEOUT: float = 1.0


class TCPServer(BaseSimulator):
    """Multithreaded TCP modem network simulator server.

    Attributes:
        host: IP address to bind server.
        port: Port number to bind server.
        response_delay_ms: Latency delay in milliseconds before returning responses.
        failure_injector: Optional FailureInjector instance.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = DEFAULT_TCP_PORT,
        response_delay_ms: float = 0.0,
        failure_injector: FailureInjector | None = None,
    ) -> None:
        """Initializes TCPServer.

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
        self._client_threads: list[threading.Thread] = []
        self._client_sockets: list[socket.socket] = []
        self._lock: threading.Lock = threading.Lock()

    @property
    def is_running(self) -> bool:
        """Indicates if the TCP server is running."""
        return self._is_running

    def start(self) -> None:
        """Starts the TCP simulator server in a background thread."""
        with self._lock:
            if self._is_running:
                logger.warning(
                    "TCP server is already running on %s:%d.", self.host, self.port
                )
                return

            try:
                self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._server_socket.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
                )
                self._server_socket.bind((self.host, self.port))
                self._server_socket.listen(TCP_LISTEN_BACKLOG)
                self._server_socket.settimeout(SOCKET_ACCEPT_TIMEOUT)
                self._is_running = True
            except Exception as exc:
                logger.error(
                    "Failed to bind TCP server on %s:%d: %s", self.host, self.port, exc
                )
                self.stop()
                raise

            self._listener_thread = threading.Thread(
                target=self._listen_loop,
                name="TCPServerListener",
                daemon=True,
            )
            self._listener_thread.start()
            logger.info(
                "TCP Simulator Server started listening on %s:%d", self.host, self.port
            )

    def _listen_loop(self) -> None:
        """Background thread listening for incoming client connections."""
        while self._is_running:
            if not self._server_socket:
                break

            try:
                client_sock, client_addr = self._server_socket.accept()
            except TimeoutError:
                continue
            except Exception:
                if not self._is_running:
                    break
                logger.debug("Socket accept interrupted.")
                continue

            logger.info(
                "TCP Client connected from %s:%d", client_addr[0], client_addr[1]
            )

            with self._lock:
                self._client_sockets.append(client_sock)

            client_thread = threading.Thread(
                target=self._handle_client,
                args=(client_sock, client_addr),
                name=f"TCPClientHandler-{client_addr[0]}:{client_addr[1]}",
                daemon=True,
            )
            with self._lock:
                self._client_threads.append(client_thread)
            client_thread.start()

    def _read_tcp_buffer(
        self, client_sock: socket.socket, buffer: str, client_addr: tuple[str, int]
    ) -> tuple[str, bool]:
        """Reads incoming TCP stream data into the provided line buffer."""
        try:
            data = client_sock.recv(TCP_BUFFER_SIZE)
            if not data:
                return buffer, False
            buffer += data.decode("utf-8", errors="replace")
            return buffer, True
        except TimeoutError:
            return buffer, True
        except Exception as exc:
            logger.debug(
                "TCP client receive exception from %s:%d: %s",
                client_addr[0],
                client_addr[1],
                exc,
            )
            return buffer, False

    def _evaluate_tcp_line(
        self, line: str, client_addr: tuple[str, int]
    ) -> tuple[bool, bool, str | None]:
        """Evaluates failure injection and generates response string for a command line.

        Returns:
            tuple[should_disconnect, should_continue, resp_str]
        """
        logger.info(
            "TCP Received command from %s:%d: '%s'",
            client_addr[0],
            client_addr[1],
            line,
        )

        action = FailureAction.NONE
        payload = None
        if self.failure_injector and self.failure_injector.enabled:
            action, payload = self.failure_injector.evaluate_failure(line)

        if action == FailureAction.DISCONNECT:
            logger.warning(
                "Failure Action: Dropping TCP connection for %s:%d",
                client_addr[0],
                client_addr[1],
            )
            return True, False, None

        if action == FailureAction.TIMEOUT:
            logger.warning(
                "Failure Action: Suppressing TCP response to force timeout for %s:%d",
                client_addr[0],
                client_addr[1],
            )
            return False, True, None

        if action == FailureAction.DROP_PACKET:
            logger.warning(
                "Failure Action: Dropping outgoing response packet for %s:%d",
                client_addr[0],
                client_addr[1],
            )
            return False, True, None

        if action == FailureAction.MALFORMED_RESPONSE:
            resp_str = str(payload)
        else:
            resp_str = self.process_command(line)

        return False, False, resp_str

    def _send_tcp_response(
        self, client_sock: socket.socket, client_addr: tuple[str, int], resp_str: str
    ) -> bool:
        """Sends encoded TCP response payload to client socket."""
        out_bytes = (resp_str + "\n").encode("utf-8")
        try:
            client_sock.sendall(out_bytes)
            logger.info(
                "TCP Sent response to %s:%d: '%s'",
                client_addr[0],
                client_addr[1],
                resp_str,
            )
            return True
        except Exception as exc:
            logger.error(
                "Failed to send TCP response to %s:%d: %s",
                client_addr[0],
                client_addr[1],
                exc,
            )
            return False

    def _handle_client(
        self, client_sock: socket.socket, client_addr: tuple[str, int]
    ) -> None:
        """Handles communication loop for an individual connected TCP client."""
        client_sock.settimeout(TCP_CLIENT_TIMEOUT)
        buffer = ""

        try:
            while self._is_running:
                buffer, keep_alive = self._read_tcp_buffer(
                    client_sock, buffer, client_addr
                )
                if not keep_alive:
                    break

                while "\n" in buffer or "\r" in buffer:
                    line, _, buffer = buffer.partition("\n")
                    line = line.strip("\r").strip()
                    if not line:
                        continue

                    disconnect, skip, resp_str = self._evaluate_tcp_line(
                        line, client_addr
                    )
                    if disconnect:
                        return
                    if skip or resp_str is None:
                        continue

                    if not self._send_tcp_response(client_sock, client_addr, resp_str):
                        return
        finally:
            logger.info(
                "TCP Client disconnected: %s:%d", client_addr[0], client_addr[1]
            )
            try:
                client_sock.close()
            except Exception:
                pass
            with self._lock:
                if client_sock in self._client_sockets:
                    self._client_sockets.remove(client_sock)

    def stop(self) -> None:
        """Stops the TCP simulator server and disconnects active clients."""
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

        with self._lock:
            for sock in self._client_sockets:
                try:
                    sock.close()
                except Exception:
                    pass
            self._client_sockets.clear()

        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=SOCKET_ACCEPT_TIMEOUT)

        logger.info("TCP Simulator Server stopped.")
