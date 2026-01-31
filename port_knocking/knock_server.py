#!/usr/bin/env python3
"""Starter template for the port knocking server."""

import argparse
import logging
import socket
import time
from os import subprocess

DEFAULT_KNOCK_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_SEQUENCE_WINDOW = 10.0


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def change_protected_port(protected_port, open=True):
    """Open the protected port using firewall rules."""
    try:
        # Command to insert a rule at the top of the INPUT chain
        command = [
            "iptables",
            "-I", "INPUT",  # Use -I to insert at the beginning of the chain
            "-p", "tcp",
            "--dport", str(protected_port),
            "-j", "ACCEPT" if open else "REJECT"
        ]
        
        # Execute the command
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Port {protected_port} {'opened' if open else 'closed'}: {'allowing' if open else 'blocking'} incoming tcp traffic on port {protected_port}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute iptables command: {e.stderr}")
    except FileNotFoundError:
        print("Error: iptables command not found. Ensure iptables is installed.")



def listen_for_knocks(sequence, window_seconds, protected_port):
    """Listen for knock sequence and open the protected port."""
    logger = logging.getLogger("KnockServer")
    logger.info("Listening for knocks: %s", sequence)
    logger.info("Protected port: %s", protected_port)

    # TODO: Create TCP listeners for each knock port.
    # TODO: Track each source IP and its progress through the sequence.
    # TODO: Enforce timing window per sequence.
    # TODO: On correct sequence, call change_protected_port() to open the port.
    # TODO: On incorrect sequence, reset progress
    # TODO: On exit, ensure protected port is closed.

    while True:
        time.sleep(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Port knocking server starter")
    parser.add_argument(
        "--sequence",
        default=",".join(str(port) for port in DEFAULT_KNOCK_SEQUENCE),
        help="Comma-separated knock ports",
    )
    parser.add_argument(
        "--protected-port",
        type=int,
        default=DEFAULT_PROTECTED_PORT,
        help="Protected service port",
    )
    parser.add_argument(
        "--window",
        type=float,
        default=DEFAULT_SEQUENCE_WINDOW,
        help="Seconds allowed to complete the sequence",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging()

    try:
        sequence = [int(port) for port in args.sequence.split(",")]
    except ValueError:
        raise SystemExit("Invalid sequence. Use comma-separated integers.")

    listen_for_knocks(sequence, args.window, args.protected_port)


if __name__ == "__main__":
    main()
