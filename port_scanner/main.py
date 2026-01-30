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
import os
import json
import csv
from datetime import datetime

USAGE_INFO = '''
------------------------------------------------------------
Usage:   python3 port_scanner_template.py <target (OPTIONAL CIDR NOTATION)> <optional: start_port end_port> <optional: verbose> <optional: output_format>
Example: python3 port_scanner_template.py 172.20.0.0/24 1 1024 0 json


ARGUMENTS:
target: IP address or CIDR notation (e.g., 192.168.0.0/24)
(optional) start_port: Starting port number (default: 1)
(optional) end_port: Ending port number (default: 1024)
(optional) verbose: 0 (only open ports) or 1 (all ports) (default: 1)
(optional) output_format: Format to save results (default: None) supports html, csv, txt, json
------------------------------------------------------------

'''


def scan_port(target, port, timeout=1.0):
    """
    Scan a single port on the target host

    Args:
        target (str): IP address or hostname to scan
        port (int): Port number to scan
        timeout (float): Connection timeout in seconds

    Returns:
        tuple: (target_ip, port, status, time, banner)
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        start_time = time.perf_counter()
        s.connect((target, port))
        
        banner = None
        data_str = ""

        # attempt to grab initial banner
        try:
            s.settimeout(0.5)
            data = s.recv(1024)
            if data:
                data_str += data.decode(errors='ignore')
        except:
            pass
            
        if "mysql" not in data_str.lower():
            try:
                msg = f"HEAD / HTTP/1.1\r\nHost: {target}\r\n\r\n"
                s.sendall(msg.encode())
                s.settimeout(0.5)
                data = s.recv(1024)
                if data:
                    data_str += data.decode(errors='ignore')
            except:
                pass

        lower_data = data_str.lower()
        if "mysql" in lower_data:
            banner = "mysql"
        elif "ssh" in lower_data:
            banner = "ssh"
        elif "http" in lower_data:
            banner = "http"
        elif "html" in lower_data: 
             banner = "http"
        elif data_str:
            banner = data_str.strip()

        end_time = time.perf_counter()
        elapsed_time = (end_time - start_time)
        elapsed_time = round(elapsed_time, 4) # round to 4 decimal places
        s.close()
        return (target, port, 1, elapsed_time, banner)

    except (socket.timeout, ConnectionRefusedError, OSError):
        return (target, port, 0, timeout, None)


def scan_range(targets, start_port, end_port):
    """
    Scan a range of ports on the target hosts

    Args:
        targets (list): List of IP addresses to scan
        start_port (int): Starting port number
        end_port (int): Ending port number

    Returns:
        list: List of ports
    """
    ports = []

    for target in targets:
        print(f"[*] Scanning {target} from port {start_port} to {end_port}")

        for port in range(start_port, end_port + 1):
            scan_result = scan_port(target, port, 0.001)
            ports.append(scan_result)
            result = scan_result[2]
            if result == 1:
                print(f"[+] {target} Port {port} is open")

    return ports

def display_results(ports, verbose=1, output_format=None):
    open_count = 0
    for port in ports:
        if port[2] == 1:
            open_count += 1
            
    # Filter ports based on verbose
    filtered_ports = ports
    if verbose == 0:
        filtered_ports = [p for p in ports if p[2] == 1]
    
    if output_format is None:
        print(f"[+] Found {open_count} open ports")
        for port in filtered_ports:
            if port[2] == 1:
                port_status = "open"
            else:
                port_status = "closed"
            
            banner_val = port[4] if (len(port) > 4 and port[4]) else "null"
            print(f"Target: {port[0]} | Port {port[1]}: {port_status} (scanned in {port[3]:.4f} seconds) | Service: {banner_val}")
    else:
        if not os.path.exists("SCANS"):
            os.makedirs("SCANS")
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"SCANS/{timestamp}_port_scan.{output_format}"
        
        try:
            with open(filename, "w") as f:
                if output_format == "txt":
                    f.write(f"[+] Found {open_count} open ports\n")
                    for port in filtered_ports:
                        if port[2] == 1:
                            port_status = "open"
                        else:
                            port_status = "closed"
                        
                        banner_val = port[4] if (len(port) > 4 and port[4]) else "null"
                        f.write(f"Target: {port[0]} | Port {port[1]}: {port_status} (scanned in {port[3]:.4f} seconds) | Service: {banner_val}\n")
                        
                elif output_format == "html":
                    f.write("<html><body>\n")
                    f.write(f"<h1>Scan Results</h1>\n")
                    f.write(f"<p>Found {open_count} open ports</p>\n")
                    f.write("<ul>\n")
                    for port in filtered_ports:
                        if port[2] == 1:
                            port_status = "open"
                        else:
                            port_status = "closed"
                            
                        banner_val = port[4] if (len(port) > 4 and port[4]) else "null"
                        f.write(f"<li>Target: {port[0]} | Port {port[1]}: {port_status} (scanned in {port[3]:.4f} seconds) | Service: {banner_val}</li>\n")
                    f.write("</ul>\n</body></html>")
                    
                elif output_format == "csv":
                    writer = csv.writer(f)
                    writer.writerow(["Target", "Port", "Status", "Time", "Banner"])
                    for port in filtered_ports:
                        status = "open" if port[2] == 1 else "closed"
                        banner = port[4] if (len(port) > 4 and port[4]) else "null"
                        writer.writerow([port[0], port[1], status, port[3], banner])
                        
                elif output_format == "json":
                    data = []
                    for port in filtered_ports:
                        status = "open" if port[2] == 1 else "closed"
                        banner = port[4] if len(port) > 4 else None
                        data.append({
                            "target": port[0],
                            "port": port[1],
                            "status": status,
                            "time": port[3],
                            "banner": banner
                        })
                    json.dump(data, f, indent=4)
                    
            print(f"[+] Results saved to {filename}")
        except Exception as e:
            print(f"[-] Error saving results: {e}")


def main(target=None, start_port=1, end_port=1024, verbose=1, output_format=None): # Scan first 1024 ports by default
    """Main function"""
    MAX_ARGS = 6 # the maximum number of arguments allowed (target + start + end + verbose + format + script_name)
    
    if target is None and len(sys.argv) > 1:
        args = sys.argv[1:]
        
        # if unrecognized format, just do normal print
        if args[-1] in ["html", "csv", "txt", "json"]:
            output_format = args.pop()
            
        if len(args) == 0:
            print(USAGE_INFO)
            sys.exit(1)
            
        target = args[0]
        
        if len(args) == 2:
            # target verbose
            try:
                verbose = int(args[1])
            except ValueError:
                print("Verbose must be an integer.")
                sys.exit(1)
                
        elif len(args) == 3:
            # target start end
            try:
                start_port = int(args[1])
                end_port = int(args[2])
            except ValueError:
                print("Ports must be integers.")
                sys.exit(1)
                
        elif len(args) == 4:
            # target start end verbose
            try:
                start_port = int(args[1])
                end_port = int(args[2])
                verbose = int(args[3])
            except ValueError:
                print("Ports/Verbose must be integers.")
                sys.exit(1)
        
        elif len(args) > 4:
            print(USAGE_INFO)
            sys.exit(1)

    if target is None:
        print(USAGE_INFO)
        sys.exit(1)
        
    targets = []
    try:
        # Check if CIDR
        try:
             ip = ipaddress.ip_address(target)
             targets.append(str(ip))
        except ValueError:
             network = ipaddress.ip_network(target, strict=False)
             for ip in network.hosts():
                 targets.append(str(ip))
             if not targets and network.num_addresses == 1:
                 targets.append(str(network.network_address))
             # If it's a CIDR that yielded hosts, we are good.

    except ValueError:
        print(f"Invalid IP address or CIDR: {target}")
        sys.exit(1)

    if(start_port < 1 or end_port > 65535 or start_port > end_port):
        print("Invalid port range. Ports must be between 1 and 65535.")
        sys.exit(1)

    ports = scan_range(targets, start_port, end_port)

    print(f"\n[+] Scan complete!")
    display_results(ports, verbose, output_format)



if __name__ == "__main__":
    main()
