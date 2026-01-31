#!/bin/bash
set -e
# every time docker compose up, automatically start the knock server and sshd
# Start SSH server in background
/usr/sbin/sshd

echo "Blocking port 2222..."
iptables -A INPUT -p tcp --dport 2222 -j REJECT

# Run the knock server
echo "Starting Knock Server..."
exec python3 /usr/local/bin/knock_server.py
