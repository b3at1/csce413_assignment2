# Honeypot Service

## Architecture and Design
This honeypot is designed to emulate the `secret_api` service. It runs on the same port (8888) and replicates the exact functions of the real API. However, instead of serving real data, it provides dummy data designed to convince an attacker of its legitimacy. 

The core difference is that all user interactions are intercepted and logged. The honeypot mirrors `api.py` regarding endpoints but integrates with `logger.py` via `setup_logging` to capture detailed request metadata.

## Logging Mechanisms & Capabilities
The honeypot captures comprehensive details about every incoming request, including:
- **Timestamp**: Exact time of the request.
- **IP Address**: Source IP of the attacker.
- **Port**: Source port.
- **Request Type**: HTTP method (GET, POST, etc.).
- **URL**: The specific endpoint accessed.
- **API Token**: If a token is provided in the request, it is extracted and logged.

The strategic value of this logging is detecting compromised credentials. Since legitimate users should not be interacting with the honeypot, any valid API token used here signals that the token has been stolen. This allows for immediate revocation and incident response.

## Analysis of Captured Attack
The logging system produces JSON-structured logs for easy parsing. Below is an example of a captured attack sequence:

```json
{"timestamp": "2026-01-31T23:00:00.816470", "ip_address": "172.20.0.1", "port": 55900, "http_request_type": "GET", "url": "http://172.20.0.30:8888/flag", "api_token": null}
172.20.0.1 - - [31/Jan/2026 23:00:00] "GET /flag HTTP/1.1" 401 -
{"timestamp": "2026-01-31T23:00:02.634680", "ip_address": "172.20.0.1", "port": 55916, "http_request_type": "GET", "url": "http://172.20.0.30:8888/", "api_token": null}
172.20.0.1 - - [31/Jan/2026 23:00:02] "GET / HTTP/1.1" 200 -
{"timestamp": "2026-01-31T23:00:08.357873", "ip_address": "172.20.0.1", "port": 57374, "http_request_type": "GET", "url": "http://172.20.0.30:8888/data", "api_token": null}
172.20.0.1 - - [31/Jan/2026 23:00:08] "GET /data HTTP/1.1" 401 -
{"timestamp": "2026-01-31T23:00:15.088240", "ip_address": "172.20.0.1", "port": 57386, "http_request_type": "GET", "url": "http://172.20.0.30:8888/data?token=FLAG{n3tw0rk_tr4ff1c_1s_n0t_s3cur3}", "api_token": "FLAG{n3tw0rk_tr4ff1c_1s_n0t_s3cur3}"}
172.20.0.1 - - [31/Jan/2026 23:00:15] "GET /data?token=FLAG{n3tw0rk_tr4ff1c_1s_n0t_s3cur3} HTTP/1.1" 200 -
```

### Interpretation
In this sequence:
1. An unauthorized IP attempts to access `/flag` without credentials.
2. The attacker probes the root path `/` and various endpoints.
3. Finally, the attacker successfully accesses `/data` using a valid API token.

This behavior confirms the IP address is hostile (as it is probing a honeypot) and provides proof that the specific API token used has been compromised.
