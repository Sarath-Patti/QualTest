"""TCP simulator server implementation.

Provides a multithreaded TCP socket server emulating modem communication.
Handles client connection lifecycle, command processing, latency simulation,
failure injection, and graceful shutdown.
"""

import socket
import threading
import time
from typing import List, Optional, Tuple

from framework.logger import get_logger
from framework.simulator.base import BaseSimulator
from framework.simulator.failure_injector import FailureAction, FailureInjector

logger = get_logger("Network.TCPServer")


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
        port: int = 8080,
        response_delay_ms: float = 0.0,
        failure_injector: Optional[FailureInjector] = None,
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
        self._server_socket: Optional[socket.socket] = None
        self._listener_thread: Optional[threading.Thread] = None
        self._is_running: bool = False
        self._client_threads: List[threading.Thread] = []
        self._client_sockets: List[socket.socket] = []
        self._lock: threading.Lock = threading.Lock()

    @property
    def is_running(self) -> bool:
        """Indicates if the TCP server is running."""
        return self._is_running

    def start(self) -> None:
        """Starts the TCP server listener thread."""
        with self._lock:
            if self._is_running:
                logger.warning("TCP simulator server is already running.")
                return

            try:
                self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self._server_socket.bind((self.host, self.port))
                self._server_socket.listen(5)
                self._server_socket.settimeout(1.0)
                self._is_running = True
            except Exception as exc:
                logger.error("Failed to start TCP server on %s:%d: %s", self.host, self.port, exc)
                self._cleanup_socket()
                raise

            logger.info("Starting TCP simulator server on %s:%d", self.host, self.port)

            self._listener_thread = threading.Thread(
                target=self._listen_loop, name="TCPServerListener", daemon=True
            )
            self._listener_thread.start()

    def _listen_loop(self) -> None:
        """Background thread accepting client connection requests."""
        while self._is_running and self._server_socket:
            try:
                client_sock, client_addr = self._server_socket.accept()
            except socket.timeout:
                continue
            except Exception:
                if not self._is_running:
                    break
                logger.debug("TCP accept loop interrupted.")
                break

            logger.info("TCP Client connected from %s:%d", client_addr[0], client_addr[1])

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

    def _handle_client(self, client_sock: socket.socket, client_addr: Tuple[str, int]) -> None:
        """Handles communication loop for an individual connected TCP client."""
        client_sock.settimeout(2.0)
        buffer = ""

        try:
            while self._is_running:
                try:
                    data = client_sock.recv(4096)
                    if not data:
                        break
                    buffer += data.decode("utf-8", errors="replace")
                except socket.timeout:
                    continue
                except Exception:
                    break

                while "\n" in buffer or buffer.endswith("\r"):
                    if "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                    else:
                        line = buffer
                        buffer = ""

                    command = line.strip()
                    if not command:
                        continue

                    logger.info("Received TCP command: '%s' from %s:%d", command, client_addr[0], client_addr[1])

                    # Failure Injection Processing
                    if self.failure_injector and self.failure_injector.enabled:
                        action, payload = self.failure_injector.evaluate_failure(command)
                        if action == FailureAction.DROP_PACKET:
                            continue
                        elif action == FailureAction.TIMEOUT:
                            time.sleep(10.0)
                            continue
                        elif action == FailureAction.DISCONNECT:
                            logger.info("Connection reset/disconnect for %s:%d", client_addr[0], client_addr[1])
                            return
                        elif action == FailureAction.MALFORMED_RESPONSE:
                            response = str(payload)
                        else:
                            response = self.process_command(command)
                    else:
                        response = self.process_command(command)

                    logger.info("Sent TCP response: '%s' to %s:%d", response, client_addr[0], client_addr[1])

                    try:
                        client_sock.sendall((response + "\n").encode("utf-8"))
                    except Exception as exc:
                        logger.error("Error sending TCP response to %s:%d: %s", client_addr[0], client_addr[1], exc)
                        break

        finally:
            logger.info("TCP Client disconnected from %s:%d", client_addr[0], client_addr[1])
            try:
                client_sock.close()
            except Exception:
                pass
            with self._lock:
                if client_sock in self._client_sockets:
                    self._client_sockets.remove(client_sock)

    def stop(self) -> None:
        """Stops the TCP server gracefully."""
        with self._lock:
            if not self._is_running:
                return
            logger.info("Stopping TCP simulator server...")
            self._is_running = False

        with self._lock:
            for sock in self._client_sockets:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    sock.close()
                except Exception:
                    pass
            self._client_sockets.clear()

        self._cleanup_socket()

        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=2.0)

        logger.info("TCP simulator server stopped.")

    def _cleanup_socket(self) -> None:
        """Closes master listening socket."""
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None
