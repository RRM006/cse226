"""
Authentication tools for MCP server.
Handles student login, admin login, and session management.
"""

import os
import threading
import webbrowser
from pathlib import Path
from typing import Any, Optional
from enum import Enum
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import httpx
from pydantic import BaseModel

from config import get_config


class UserRole(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"
    NONE = "none"


class MCPSession(BaseModel):
    """Session object stored in MCP server."""

    role: UserRole = UserRole.NONE
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    admin_email: Optional[str] = None
    access_token: Optional[str] = None
    api_token: Optional[str] = None


_config = get_config()
API_URL = _config["api_url"] if isinstance(_config, dict) else _config["api_url"]
SUPABASE_URL = (
    _config["supabase_url"]
    if isinstance(_config, dict)
    else _config.get("supabase_url", "https://zxzcnpkfabiiecagczao.supabase.co")
)

_token_storage: MCPSession = MCPSession()


def set_session(session: MCPSession) -> None:
    """Set the global session."""
    global _token_storage
    _token_storage = session


def get_session() -> MCPSession:
    """Get the current session."""
    return _token_storage


def get_auth_headers() -> dict:
    """Get authorization headers for API calls."""
    session = get_session()
    if session.access_token:
        return {"Authorization": f"Bearer {session.access_token}"}
    return {}


def student_login(student_id: str, password: str) -> dict[str, Any]:
    """
    Student login with student ID and password.

    Args:
        student_id: 10-digit student ID (e.g., '2211234567')
        password: Student's password

    Returns:
        dict with success status, token, student info
    """
    if not student_id or not password:
        return {"success": False, "error": "student_id and password are required"}

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_URL}/api/v1/student/login",
                json={"student_id": student_id, "password": password},
            )

            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")

                session = MCPSession(
                    role=UserRole.STUDENT,
                    student_id=student_id,
                    student_name=data.get("name"),
                    access_token=token,
                )
                set_session(session)

                return {
                    "success": True,
                    "student_id": student_id,
                    "name": data.get("name"),
                    "is_first_login": data.get("is_first_login", False),
                    "message": f"Logged in as student {student_id}",
                }
            else:
                error_msg = response.json().get("detail", "Login failed")
                return {"success": False, "error": error_msg}
    except httpx.ConnectError:
        return {
            "success": False,
            "error": f"Cannot connect to API at {API_URL}. Is the backend running?",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def admin_login(access_token: str) -> dict[str, Any]:
    """
    Admin login with Supabase access token.

    Args:
        access_token: Supabase JWT token

    Returns:
        dict with success status, admin info
    """
    if not access_token:
        return {"success": False, "error": "access_token is required"}

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_URL}/api/v1/session/admin-login",
                json={"access_token": access_token},
            )

            if response.status_code == 200:
                session = MCPSession(
                    role=UserRole.ADMIN, admin_email="admin", access_token=access_token
                )
                set_session(session)

                return {"success": True, "message": "Logged in as admin"}
            else:
                error_msg = response.json().get("detail", "Login failed")
                return {"success": False, "error": error_msg}
    except httpx.ConnectError:
        return {
            "success": False,
            "error": f"Cannot connect to API at {API_URL}. Is the backend running?",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_current_user() -> dict[str, Any]:
    """
    Get current authenticated user info.

    Returns:
        dict with user info or error
    """
    session = get_session()
    headers = get_auth_headers()

    if not headers.get("Authorization"):
        return {
            "success": False,
            "error": "Not authenticated. Call student_login or admin_login first.",
        }

    try:
        with httpx.Client(timeout=30.0) as client:
            if session.role == UserRole.STUDENT:
                response = client.get(f"{API_URL}/api/v1/student/me", headers=headers)
            else:
                response = client.get(f"{API_URL}/api/v1/me", headers=headers)

            if response.status_code == 200:
                return {"success": True, "user": response.json()}
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to get user"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {API_URL}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def change_password(current_password: str, new_password: str) -> dict[str, Any]:
    """
    Student change password.

    Args:
        current_password: Current password
        new_password: New password (min 6 characters)

    Returns:
        dict with success status
    """
    session = get_session()
    headers = get_auth_headers()

    if session.role != UserRole.STUDENT:
        return {
            "success": False,
            "error": "Only students can change password. Login as student first.",
        }

    if not current_password or not new_password:
        return {
            "success": False,
            "error": "current_password and new_password are required",
        }

    if len(new_password) < 6:
        return {"success": False, "error": "New password must be at least 6 characters"}

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_URL}/api/v1/student/change-password",
                headers=headers,
                json={
                    "current_password": current_password,
                    "new_password": new_password,
                },
            )

            if response.status_code == 200:
                return {"success": True, "message": "Password changed successfully"}
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to change password"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {API_URL}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def logout() -> dict[str, Any]:
    """
    Logout current session.

    Returns:
        dict with success status
    """
    global _token_storage
    _token_storage = MCPSession()

    return {"success": True, "message": "Logged out successfully"}


def admin_login_google() -> dict[str, Any]:
    """
    Admin login with Google OAuth (same as frontend).
    Opens browser for Google sign-in, returns to MCP server.

    Returns:
        dict with auth URL to open in browser
    """
    try:
        import supabase
    except ImportError:
        return {
            "success": False,
            "error": "Missing required dependency. Run: pip install @supabase/supabase-js",
        }

    supabase_client = supabase.create_client(
        SUPABASE_URL,
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4emNucGtmYWJpaWVjYWdjemFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI4MDExNDMsImV4cCI6MjA4ODM3NzE0M30.0Qo8IT6gBIOF3YMlHZm4dnh47lMUW5QesD_f3EVf9tM",
    )

    redirect_to = "http://localhost:8001/oauth/callback"

    auth_url = supabase_client.auth.sign_in_with_oauth(
        {"provider": "google", "options": {"redirect_to": redirect_to}}
    )

    if hasattr(auth_url, "url"):
        auth_url_str = auth_url.url
    else:
        auth_url_str = str(auth_url.get("url", ""))

    return {
        "success": True,
        "message": "Opening Google login in browser...",
        "auth_url": auth_url_str,
        "redirect_to": redirect_to,
        "instructions": "After logging in with your NSU email, you will be redirected back. The MCP server will capture the session automatically.",
    }


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler to capture OAuth callback."""

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/oauth/callback":
            query = parse_qs(parsed.query)

            if "access_token" in query:
                access_token = query["access_token"][0]

                session = MCPSession(
                    role=UserRole.ADMIN, admin_email="admin", access_token=access_token
                )
                set_session(session)

                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"""
                <html><head><title>Login Successful</title></head>
                <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: green;">Login Successful!</h1>
                    <p>You can now close this window and return to your chat.</p>
                    <script>setTimeout(() => window.close(), 3000);</script>
                </body></html>
                """)
            elif "error" in query:
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                error_msg = query.get("error_description", ["Login failed"])[0]
                self.wfile.write(
                    f'<html><body><h1 style="color: red;">Login Failed</h1><p>{error_msg}</p></body></html>'.encode()
                )
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def start_oauth_server() -> dict[str, Any]:
    """
    Start a local OAuth callback server.

    Returns:
        dict with server status
    """
    try:
        server = HTTPServer(("localhost", 8001), OAuthCallbackHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return {
            "success": True,
            "message": "OAuth callback server started on port 8001",
            "callback_url": "http://localhost:8001/oauth/callback",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_session_info() -> dict[str, Any]:
    """
    Get current session info.

    Returns:
        dict with session details
    """
    session = get_session()

    return {
        "role": session.role.value if session.role else "none",
        "student_id": session.student_id,
        "student_name": session.student_name,
        "admin_email": session.admin_email,
        "authenticated": session.access_token is not None,
    }
