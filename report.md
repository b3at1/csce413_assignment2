# 1. Executive Summary
#### Author: Sam Bederman
## YT Video (TODO: ADD LINKS)
PART 1:
PART 2:
PART 3:
## Overview
In this assignment, I was engaged by CSCE-413 to develop network tooling, perform comprehensive reconnaissance, and conduct a network-based vulnerability assessment. My objectives included creating specialized tools to enhance the organization's security posture and providing strategic remediation for any identified weaknesses. The engagement was successful in uncovering numerous security flaws, which ultimately led to the discovery and capture of three specific flags during the exercise.

## Critical Vulnerabilities Found
The assessment identified several high-impact vulnerabilities that could allow an adversary to compromise the environment. The primary MITRE ATT&CK techniques observed include:

T1557 – Adversary-in-the-Middle (AiTM): Exploited to intercept sensitive traffic and credentials.

T1021.004 – Remote Services (SSH): Leveraged through weak authentication to gain initial access.

T1550.001 – Use Alternate Authentication Material (Application Access Token): Used to impersonate authorized users and bypass standard auth flows via stolen API tokens.

## Recommended Fixes
A detailed analysis of the recommended security controls will be provided in Part 3 of this report. At a high level, the proposed remediation strategy focuses on implementing robust identity management through Multi-Factor Authentication (MFA) and transitioning to SSH key-based authentication to replace vulnerable password schemas. Additionally, the security posture should be reinforced by implementing strict network segmentation and enforcing securely encrypted network protocols (TLS 1.2+) to protect data in transit and prevent credential sniffing.
<div style="page-break-after: always;"></div>


# 2. Part 1: Reconnaissance
## Port Scanner Implementation
The port scanner implementation consistend of the minimum requirements: 
- Accept target IP/hostname and port range as arguments ✅  
- Perform TCP connect scans to detect open ports ✅  
- Display results showing port number, state (open/closed), and timing ✅  
- Handle errors gracefully (timeouts, connection refused, etc.) ✅  
- Service/banner detection - Identify what service is running on each port ✅ (only if the service responds with a banner)  
<br>
I also implemented the following extras:
- Scan multiple hosts (CIDR notation) ✅  
- Different verbosity / display levels ✅  
- Output formats (supports html, csv, txt, json) ✅ 
<br>
The scanner works as a 4 step process. First `main()` parses cli args, such as using the `ipaddress` library to convert a CIDR range into a range of targets. `scan_range` then loops over every IP, and for each IP loops over every port number. Then, inside the loop `scan_port` is called which does the actual scanning by first attempting a TCP handshake. If successful it attempts to identify the service by trying to receive the banner and sending more requests such as a HEAD request to identify the type of service. Lastly the returned tuples are incorporated into a list that is fed into `display_results` to output the scan results in the correct format.

## Discovered Services
The discovered services were as follows:
<p>Found 7 open ports</p>
<ul>
<li>Target: 172.20.0.1 | Port 1716: open (scanned in 0.9512 seconds) | Service: null</li>
<li>Target: 172.20.0.1 | Port 5001: open (scanned in 0.5029 seconds) | Service: http</li>
<li>Target: 172.20.0.10 | Port 5000: open (scanned in 0.5029 seconds) | Service: http</li>
<li>Target: 172.20.0.11 | Port 3306: open (scanned in 0.0002 seconds) | Service: mysql</li>
<li>Target: 172.20.0.20 | Port 2222: open (scanned in 0.0105 seconds) | Service: ssh</li>
<li>Target: 172.20.0.21 | Port 8888: open (scanned in 0.5704 seconds) | Service: http</li>
<li>Target: 172.20.0.22 | Port 6379: open (scanned in 0.5007 seconds) | Service: null</li>
</ul>

## Methodology
The methodology was scanning the 172.20.0.0/24 subnet from ports 1-9000. The scan results were used to identify services of interest to exploit such as 172.20.0.10:5000 which was exploited with the MITM attack to get `FLAG{n3tw0rk_tr4ff1c_1s_n0t_s3cur3}` as well as 172.20.0.21:8888 which utilized the first flag to get flag 3 `FLAG{p0rt_kn0ck1ng_4nd_h0n3yp0ts_s4v3_th3_d4y}` and 172.20.0.20:2222 which was exploited for flag 2 `FLAG{h1dd3n_s3rv1c3s_n33d_pr0t3ct10n}`
<div style="page-break-after: always;"></div>

# 3. Part 2: MITM Attack
## Vulnerability Analysis
The primary vulnerability identified is a lack of encryption for sensitive data in transit, facilitating an MITM attack. By intercepting unencrypted HTTP traffic, an attacker can capture the API authentication token (Flag 1).

The second vulnerability involves a Remote SSH service configured with weak or default credentials. This allows an adversary to perform a brute-force or credential-guessing attack to gain shell access to the host.

The third vulnerability is an insecure API endpoint that trusts stolen api access tokens (Flag 1). An attacker can use this "alternate authentication material" to impersonate a legitimate user and submit malicious requests to extract further sensitive data (Flag 3).

## Attack Methodology
To execute the attack, I positioned myself on the local network and used Wireshark to perform packet sniffing on the target interface. By monitoring the communication between the client and the server at 172.20.0.10, I was able to intercept the raw, unencrypted HTTP GET request and the subsequent server response.

## Captured Data
```http
GET /api/secrets HTTP/1.1
Host: 172.20.0.10:5000
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: [http://172.20.0.10:5000/](http://172.20.0.10:5000/)
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9


HTTP/1.1 200 OK
Server: Werkzeug/3.1.5 Python/3.11.14
Date: Sat, 31 Jan 2026 19:05:34 GMT
Content-Type: application/json
Content-Length: 214
Connection: close

[
  {
    "description": "API authentication token for secret services - MITM attack will reveal this!",
    "id": 1,
    "secret_name": "api_token",
    "secret_value": "FLAG{n3tw0rk_tr4ff1c_1s_n0t_s3cur3}"
  }
]
```
## Real-World Impact Assessment
The impact of an MITM attack is severe, as it grants an attacker complete visibility into "plaintext" credentials and session tokens. Once an API token is stolen, an attacker can bypass standard authentication barriers to perform unauthorized actions, such as data exfiltration or system configuration changes. This scenario demonstrates "vulnerability chaining" where a simple lack of encryption leads to identity theft (SSH/API), potentially resulting in elevated privileges within the infrastructure, or even full system compromise.
<div style="page-break-after: always;"></div>

# 4. Part 3: Security Fixes

<div style="page-break-after: always;"></div>

# 5. Remediation Recommendations

<div style="page-break-after: always;"></div>

# 6. Conclusion