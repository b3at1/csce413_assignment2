# Port Knocking Implementation

## Design Decisions
The system utilizes a split architecture where `knock_server.py` runs within the SSH container, while the port knocking container hosts the client and `demo.py`. Additional features include a timeout mechanism to reset the sequence window and a strict reset policy that clears progress upon receiving an incorrect knock.

## Implementation Details
The core logic resides in `knock_server.py`, where `listen_for_knocks` initializes non-blocking sockets for each port in the sequence. The main event loop uses `select.select` to handle incoming connections. For each connection, the server checks the `ip_states` dictionary to validate the sequence. If the port matches the expected value, the state advances; if it is incorrect or if the `window_seconds` timeout is exceeded, the state resets to zero. When the full sequence is verified, `change_protected_port` is called to execute the necessary `iptables` command, inserting a rule to accept traffic on the protected port.

The demo is handled by `demo.py` which coordinates the workflow by first calling `attempt_ssh` to verify the port is closed. It then spawns the `knock_client.py` process, which triggers `perform_knock_sequence` to iterate through the required ports using `send_knock` for each TCP handshake. Finally, `demo.py` calls `attempt_ssh` again to confirm that the firewall rule has been applied and access is granted.

## Security Analysis
Port knocking restricts access by keeping the SSH port closed until a specific sequence of connection attempts is detected. This obscures the service from casual scanners and automated attacks, adding a layer of defense-in-depth dependent on the secrecy of the knock sequence.

## Limitations and Improvements
Currently, the knocking ports reject connections rather than dropping packets, making them visible to scanners and potentially reducing the search space for an attacker. Security could be improved by configuring the firewall to silently drop packets, increasing the sequence complexity, and introducing dummy ports with randomized behavior to obfuscate the true knock sequence.
