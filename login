#!/usr/bin/env python3
"""
Login CLI - Direct executable for login
Usage: login
"""
import sys
import os

# Get project root - assume script is in project root
project_root = os.getcwd()
sys.path.insert(0, project_root)
os.environ['PYTHONPATH'] = project_root

from dotenv import load_dotenv
env_path = os.path.join(project_root, "backend", ".env")
load_dotenv(env_path)

import base64
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from cli.credentials import save_credentials, validate_nsu_email


def build_supabase_oauth_url():
    supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    redirect = "http://localhost:54321/callback"
    return (
        f"{supabase_url}/auth/v1/authorize"
        f"?provider=google"
        f"&redirect_to={redirect}"
        f"&scope=email"
    )


def decode_jwt_email(token):
    try:
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return payload.get("email", "")
    except Exception:
        return ""


class CallbackHandler(BaseHTTPRequestHandler):
    token_result = {}

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if self.path == '/favicon.ico':
            self.send_response(404)
            self.end_headers()
            return

        if "access_token" in params or "code" in params or "error" in params:
            CallbackHandler.token_result["access_token"] = params.get("access_token", [None])[0]
            CallbackHandler.token_result["refresh_token"] = params.get("refresh_token", [None])[0]
            CallbackHandler.token_result["code"] = params.get("code", [None])[0]
            CallbackHandler.token_result["error"] = params.get("error", [None])[0]
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            if "error" in params:
                self.wfile.write(b"<h2>Login error. Return to your terminal.</h2>")
            else:
                self.wfile.write(b"<h2>Login complete. Return to your terminal.</h2><script>setTimeout(function(){window.close();}, 2000);</script>")
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
            <!DOCTYPE html>
            <html>
            <head><title>Processing Login...</title></head>
            <body>
            <h2>Processing login...</h2>
            <script>
            window.onload = function() {
                if (window.location.hash) {
                    window.location.replace("/callback?" + window.location.hash.substring(1));
                } else if (window.location.search) {
                    window.location.replace("/callback" + window.location.search);
                } else {
                    document.body.innerHTML = "<h2>No token found in URL. Return to your terminal.</h2>";
                    window.location.replace("/callback?error=no_token");
                }
            };
            </script>
            </body>
            </html>
            """)

    def log_message(self, format, *args):
        pass


def main():
    print("\n=== NSU Audit Login ===\n")
    
    oauth_url = build_supabase_oauth_url()

    if not oauth_url or not oauth_url.startswith("http"):
        print("Login failed: SUPABASE_URL not configured.")
        print("Please ensure backend/.env has SUPABASE_URL")
        sys.exit(1)

    print("Opening browser for NSU Google login...")
    print(f"URL: {oauth_url}\n")

    try:
        webbrowser.open(oauth_url)
    except Exception:
        print("Failed to open browser automatically.")
        print(f"Please open this URL manually: {oauth_url}")

    CallbackHandler.token_result = {}
    server = HTTPServer(("localhost", 54321), CallbackHandler)
    server.timeout = 1

    print("Waiting for login... (timeout: 120 seconds)")

    import time
    start_time = time.time()
    while not CallbackHandler.token_result and (time.time() - start_time) < 120:
        server.handle_request()

    server.server_close()

    if CallbackHandler.token_result.get("error"):
        print(f"Login failed: {CallbackHandler.token_result.get('error')}")
        sys.exit(1)

    access_token = CallbackHandler.token_result.get("access_token")
    refresh_token = CallbackHandler.token_result.get("refresh_token", "")

    if not access_token:
        print("Login failed: no token received.")
        sys.exit(1)

    email = decode_jwt_email(access_token)
    if not email:
        print("Login failed: could not extract email from token.")
        sys.exit(1)

    if not validate_nsu_email(email):
        print(f"Login failed: only @northsouth.edu accounts are permitted.")
        print(f"Your email: {email}")
        sys.exit(1)

    save_credentials(access_token, refresh_token, email)
    print(f"Logged in as {email}\n")


if __name__ == "__main__":
    main()
