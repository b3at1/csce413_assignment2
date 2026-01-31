#!/usr/bin/env python3
import sys
import socket
import subprocess

# NOTE: this file is used in lieu of demo.sh for easier interoperability
# NOTE: sshpass must be installed for this demo to do automated ssh login
# NOTE: knock_server.py was moved to the ssh container to operate properly
def attempt_ssh(ip, user, protected_port, password):
    try:
        cmd = [
            "sshpass", "-p", password,
            "ssh", "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-p", str(protected_port),
            f"{user}@{ip}"
        ]
        ret_code = subprocess.call(cmd)
        if ret_code != 0:
            print(f"[-] SSH connection to {user}@{ip}:{protected_port} failed.")
            print(f"SSH command exited with error code {ret_code}.")
        else:
            print(f"[+] SSH connection to {user}@{ip}:{protected_port} succeeded.")
    except FileNotFoundError:
        print("Error: 'sshpass' is not installed or not in PATH.")
        sys.exit(1)
def main():
    # 1. Handle Arguments (mimicking ${1:-default})
    '''
    DEFAULT_TARGET_IP = "172.20.0.20"
    DEFAULT_KNOCK_SEQUENCE = [1234, 5678, 9012]
    DEFAULT_PROTECTED_PORT = 2222
    DEFAULT_DELAY = 0.3
    '''

    if len(sys.argv) != 4:
        print("[+] Usage: demo.py [TARGET_IP] [PORT1,PORT2,PORT3] [PROTECTED_PORT]")
        sys.exit(1)
    target_ip = sys.argv[1]
    sequence = sys.argv[2]
    protected_port = sys.argv[3]
    try: protected_port = int(protected_port)
    except ValueError:
        print(f"Error: Port must be an integer. Got {protected_port}")
        sys.exit(1)

    # 2. Initial SSH Attempt
    ssh_user = "sshuser"
    ssh_pass = "SecurePass2024!"

    print(f"Attempting initial SSH connection to {ssh_user}@{target_ip} WITHOUT knocking...")
    attempt_ssh(target_ip, ssh_user, protected_port, ssh_pass)

    print("-" * 40)

   
    print(f"[+] Sending knock sequence: {sequence}")
    
    # call the client script to perform the knock sequence
    knock_cmd = [
        sys.executable, "knock_client.py",
        "--target", target_ip,
        "--sequence", sequence,
        "--delay", "0.3"
    ]
    
    try:
        subprocess.check_call(knock_cmd)
    except subprocess.CalledProcessError as e:
        print(f"Error: knock_client.py failed with exit code {e.returncode}")
    except FileNotFoundError:
        print("Error: Could not find 'knock_client.py' in the current directory.")
        sys.exit(1)

    print("[+] Attempting ssh AFTER knocking")
    attempt_ssh(target_ip, ssh_user, protected_port, ssh_pass)

if __name__ == "__main__":
    main()