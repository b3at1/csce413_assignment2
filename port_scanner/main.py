#!/usr/bin/env python3
"""
Port Scanner - Starter Template for Students
Assignment 2: Network Security

This is a STARTER TEMPLATE to help you get started.
You should expand and improve upon this basic implementation.

TODO for students:
1. Implement multi-threading for faster scans
2. Add banner grabbing to detect services
3. Add support for CIDR notation (e.g., 192.168.1.0/24)
4. Add different scan types (SYN scan, UDP scan, etc.)
5. Add output formatting (JSON, CSV, etc.)
6. Implement timeout and error handling
7. Add progress indicators
8. Add service fingerprinting
"""

import socket
import sys
import time
import ipaddress

USAGE_INFO = '''
Usage:   python3 port_scanner_template.py <target>
Example: python3 port_scanner_template.py 172.20.0.10
'''


def scan_port(target, port, timeout=1.0):
    """
    Scan a single port on the target host

    Args:
        target (str): IP address or hostname to scan
        port (int): Port number to scan
        timeout (float): Connection timeout in seconds

    Returns:
        bool: True if port is open, False otherwise
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        start_time = time.perf_counter()
        s.connect((target, port))
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        s.close()
        return (port, 1, elapsed_time)

    except (socket.timeout, ConnectionRefusedError, OSError):
        return (port, 0, timeout)


def scan_range(target, start_port, end_port):
    """
    Scan a range of ports on the target host

    Args:
        target (str): IP address or hostname to scan
        start_port (int): Starting port number
        end_port (int): Ending port number

    Returns:
        list: List of ports
    """
    ports = []

    print(f"[*] Scanning {target} from port {start_port} to {end_port}")
    print(f"[*] This may take a while...")

    for port in range(start_port, end_port + 1):
        scan_result = scan_port(target, port)
        ports.append(scan_result)
        result = scan_result[1]
        if result == 1:
            print(f"[+] Port {port} is open")

    return ports

def main(target=None, start_port=1, end_port=1024): # Scan first 1024 ports by default
    """Main function"""
    if target is None:
        if len(sys.argv) < 2:
            print(USAGE_INFO)
            sys.exit(1)
            
        target = sys.argv[1]
        
        if len(sys.argv) >= 4:
            try:
                start_port = int(sys.argv[2])
                end_port = int(sys.argv[3])
            except ValueError:
                print("Ports must be integers.")
                sys.exit(1)
            
    try:
        ipaddress.ip_address(target)
    except ValueError:
        print(f"Invalid IP address: {target}")
        sys.exit(1)
    if(start_port < 1 or end_port > 65535 or start_port > end_port):
        print("Invalid port range. Ports must be between 1 and 65535.")
        sys.exit(1)

    print(f"[*] Starting port scan on {target}")

    ports = scan_range(target, start_port, end_port)

    print(f"\n[+] Scan complete!")
    # TODO: Display results
    for port in ports:
        if port[1] == 1:
            port_status = "open"
        else:
            port_status = "closed"
        print(f"Port {port[0]}: {port_status} (scanned in {port[2]:.4f} seconds)")


if __name__ == "__main__":
    main()
