"""Network communication package for TCP and UDP modem interfaces."""

from network.tcp.client import TCPClient
from network.udp.client import UDPClient

__all__ = ["TCPClient", "UDPClient"]
