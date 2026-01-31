#!/usr/bin/env python3
"""Starter template for the port knocking server."""

import argparse
import logging
import socket
import select
import time
import subprocess

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
    
    ip_states = {}
    sockets = []
    sock_map = {}
    bound_ports = set()
    
    try:
        for port in sequence:
            if port in bound_ports:
                continue
            
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', port))
                s.listen(5)
                sockets.append(s)
                sock_map[s] = port
                bound_ports.add(port)
                logger.info("Listening on port %d", port)
            except OSError as e:
                logger.error("Failed to bind port %d: %s", port, e)
                # Close already opened sockets
                for s in sockets:
                    s.close()
                return

        while True:
            readable, _, _ = select.select(sockets, [], [], 1.0)
            
            for s in readable:
                conn, addr = s.accept()
                ip = addr[0]
                conn.close()
                
                knocked_port = sock_map[s]
                logger.info("Knock from %s on port %d", ip, knocked_port)
                
                now = time.time()
                state = ip_states.get(ip, {'index': 0, 'last_time': 0})
                
                # Check window timeout if strictly progressing
                if state['index'] > 0 and (now - state['last_time'] > window_seconds):
                    logger.info("Window expired for %s. Resetting.", ip)
                    state['index'] = 0
                
                # Check against expected port
                expected = sequence[state['index']]
                if knocked_port == expected:
                    state['index'] += 1
                    state['last_time'] = now
                    logger.info("Correct knock (%d/%d) for %s", state['index'], len(sequence), ip)
                    
                    if state['index'] == len(sequence):
                        logger.info("Sequence complete for %s. Opening protected port.", ip)
                        change_protected_port(protected_port, open=True)
                        state['index'] = 0
                else:
                    logger.info("Incorrect knock for %s (got %d, expected %d). Resetting.", ip, knocked_port, expected)
                    state['index'] = 0
                
                ip_states[ip] = state
                
    except KeyboardInterrupt:
        logger.info("Stopping knock server...")
    finally:
        logger.info("Closing knocking sockets...")
        for s in sockets:
            s.close()


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

    try:
        listen_for_knocks(sequence, args.window, args.protected_port)
    finally:
        change_protected_port(args.protected_port, open=False)

if __name__ == "__main__":
    main()
