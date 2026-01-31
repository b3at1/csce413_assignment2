#!/usr/bin/env python3
from flask import Flask, jsonify, request
from logger import setup_logging, log_request

app = Flask(__name__)
# ensure non-ascii characters are not escaped in the response
app.json.ensure_ascii = False

def get_token():
    # extract token from header or query param
    auth_header = request.headers.get("Authorization")
    token_param = request.args.get("token")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]
    return token_param

@app.before_request
def log_activity():
    # log every request with extracted token
    token = get_token()
    log_request(request, token)

@app.route("/")
def index():
    return jsonify({
        "service": "ULTRA-SECRET API Server",
        "version": "1.0",
        "port": 8888,
        "status": "running",
        "message": "This is a hidden API service. Authentication required.",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "API information"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/flag", "method": "GET", "description": "Get flag (requires authentication)"},
            {"path": "/data", "method": "GET", "description": "Get secret data (requires authentication)"},
        ],
        "authentication": {
            "type": "Bearer token",
            "header": "Authorization: Bearer <token>",
            "alternative": "?token=<token> query parameter",
            "hint": "The token can be found by intercepting network traffic...",
        },
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "secret_api", "port": 8888})

@app.route("/flag")
def get_flag():
    token = get_token()
    if not token:
        return jsonify({"error": "Authentication required", "message": "No authentication token provided"}), 401
    
    # return fake flag
    return jsonify({
        "success": True,
        "message": "Congratulations! This is totally the real flag 😉",
        "flag": "FLAG{f4k3_fl4g_f0r_h0n3yp0t_t3st1ng}",
    })

@app.route("/data")
def get_data():
    token = get_token()
    if not token:
        return jsonify({"error": "Authentication required", "message": "No authentication token provided"}), 401

    # return fake data
    return jsonify({
        "secret_data": [
            {"id": 1, "name": "Totally Real Project", "classification": "Top Secret"},
            {"id": 2, "name": "Operation: ULTRA-SECRET", "classification": "Confidential"},
            {"id": 3, "name": "Very Real Key", "classification": "Restricted"},
        ],
        "message": "This is top secret data."
    })

@app.route("/admin")
def admin():
    token = get_token()
    if not token:
        return jsonify({"error": "Authentication required", "message": "No authentication token provided"}), 401

    return jsonify({
        "admin_panel": True,
        "users": ["real_admin", "real_operator"],
        "permissions": ["read"],
        "message": "Real admin access granted"
    })

if __name__ == "__main__":
    setup_logging()
    app.run(host="0.0.0.0", port=8888, debug=False)
