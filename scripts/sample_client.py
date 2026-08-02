#!/usr/bin/env python3
"""Sample client script for manual modem simulator communication testing.

Sends a single modem command string to the running TCP or UDP simulator server
and prints the received response.
"""

import argparse
import sys
from pathlib import Path

from network.tcp import TCPClient, TCPClientConfig
from network.udp import UDPClient, UDPClientConfig

DEFAULT_TCP_PORT: int = 8080
DEFAULT_UDP_PORT: int = 8081
DEFAULT_TIMEOUT: float = 3.0

# Add project root to Python path if executed directly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def parse_args() -> argparse.Namespace:
    """Parses sample client CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="sample_client",
        description="Sample client for testing QualTest modem simulator",
    )
    parser.add_argument(
        "-p",
        "--protocol",
        type=str,
        choices=["tcp", "udp"],
        default="tcp",
        help="Target protocol (tcp or udp)",
    )
    parser.add_argument(
        "-H",
        "--host",
        type=str,
        default="127.0.0.1",
        help="Target simulator host address",
    )
    parser.add_argument(
        "-P",
        "--port",
        type=int,
        default=None,
        help="Target simulator port number (default: 8080 for TCP, 8081 for UDP)",
    )
    parser.add_argument(
        "-c",
        "--command",
        type=str,
        default="ATTACH_REQUEST",
        help="Modem command string to send",
    )
    return parser.parse_args()


def main() -> int:
    """Main execution function for sample client."""
    args = parse_args()
    protocol = args.protocol.lower()
    host = args.host
    port = args.port or (DEFAULT_TCP_PORT if protocol == "tcp" else DEFAULT_UDP_PORT)
    command = args.command

    print(f"[*] Target      : {protocol.upper()}://{host}:{port}")
    print(f"[*] Sending     : '{command}'")

    try:
        if protocol == "tcp":
            tcp_client = TCPClient(
                TCPClientConfig(host=host, port=port, timeout_seconds=DEFAULT_TIMEOUT)
            )
            response = tcp_client.send_command(command)
        else:
            udp_client = UDPClient(
                UDPClientConfig(host=host, port=port, timeout_seconds=DEFAULT_TIMEOUT)
            )
            response = udp_client.send_command(command)
            udp_client.close()

        print(f"[+] Received   : '{response}'")
        return 0
    except Exception as exc:
        print(f"[-] Error      : {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
