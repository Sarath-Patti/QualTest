#!/usr/bin/env python3
"""Sample client script for manual modem simulator communication testing.

Sends a single modem command string to the running TCP or UDP simulator server
and prints the received response.
"""

import argparse
import sys
from pathlib import Path

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from network.tcp import TCPClient, TCPClientConfig
from network.udp import UDPClient, UDPClientConfig


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
    port = args.port or (8080 if protocol == "tcp" else 8081)
    command = args.command

    print(f"[*] Target      : {protocol.upper()}://{host}:{port}")
    print(f"[*] Sending     : '{command}'")

    try:
        if protocol == "tcp":
            client = TCPClient(TCPClientConfig(host=host, port=port, timeout_seconds=3.0))
            response = client.send_command(command)
        else:
            client = UDPClient(UDPClientConfig(host=host, port=port, timeout_seconds=3.0))
            response = client.send_command(command)
            client.close()

        print(f"[+] Received   : '{response}'")
        return 0
    except Exception as exc:
        print(f"[-] Error      : {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
