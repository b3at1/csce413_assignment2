#!/usr/bin/env python3
import sys
import socket
import subprocess

def check_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.01)
        result = sock.connect((ip, port))
        sock.close()
        
        if result == 0:
            print(f"[+] Connection to {ip} {port} port succeeded!")
            return True
        else:
            print(f"[-] Connection to {ip} {port} port failed.")
            return False
    except Exception:
        return False


def attempt_ssh(ip, user, protected_port, password):
    if not check_port(ip, protected_port):
        print(f"[-] SSH connection to {user}@{ip}:{protected_port} failed.")
    else:
        try:
            cmd = [
                "sshpass", "-p", password,
                "ssh", "-o", "StrictHostKeyChecking=no",
                f"{user}@{ip} -p {protected_port}"
            ]
            ret_code = subprocess.call(cmd)
            if ret_code != 0:
                print(f"SSH command exited with error code {ret_code}.")
        except FileNotFoundError:
            print("Error: 'sshpass' is not installed or not in PATH.")
            sys.exit(1)
def main():
    # 1. Handle Arguments (mimicking ${1:-default})
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
    
    # We call the external script exactly as shown in the bash script
    knock_cmd = [
        sys.executable, "knock_client.py",
        "--target", target_ip,
        "--sequence", sequence,
        "--check"
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