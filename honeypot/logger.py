import logging
import json
import os
from datetime import datetime

log_path = "/app/logs/connections.jsonl"

def setup_logging():
    # ensure log directory exists
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
    )

def log_request(request, token=None):
    # capture request details
    data = {
        "timestamp": datetime.now().isoformat(),
        "ip_address": request.remote_addr,
        "port": request.environ.get("REMOTE_PORT"),
        "http_request_type": request.method,
        "url": request.url,
        "api_token": token
    }
    # ensure_ascii=True escapes non-ASCII characters to \uXXXX sequences
    logging.info(json.dumps(data, default=str, ensure_ascii=True))
