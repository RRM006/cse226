import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import httpx
from supabase import create_client, Client


class UserRole(Enum):
    ADMIN = "admin"
    STUDENT = "student"
    NONE = "none"


@dataclass
class MCPSession:
    role: UserRole = UserRole.NONE
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    admin_email: Optional[str] = None
    access_token: Optional[str] = None
    api_token: Optional[str] = None


_session: MCPSession = MCPSession()


def get_session() -> MCPSession:
    return _session


def clear_session():
    global _session
    _session = MCPSession()


def set_student_session(student_id: str, student_name: str, token: str):
    global _session
    _session.role = UserRole.STUDENT
    _session.student_id = student_id
    _session.student_name = student_name
    _session.access_token = token
    _session.api_token = token


def set_admin_session(email: str, token: str):
    global _session
    _session.role = UserRole.ADMIN
    _session.admin_email = email
    _session.access_token = token
    _session.api_token = token


def is_authenticated() -> bool:
    return _session.role != UserRole.NONE


def get_auth_status() -> dict:
    if _session.role == UserRole.STUDENT:
        return {
            "authenticated": True,
            "role": "student",
            "student_id": _session.student_id,
            "student_name": _session.student_name,
        }
    elif _session.role == UserRole.ADMIN:
        return {
            "authenticated": True,
            "role": "admin",
            "email": _session.admin_email,
        }
    else:
        return {
            "authenticated": False,
            "role": None,
        }


def student_login(api_url: str, student_id: str, password: str = None) -> dict:
    """
    Login as student via backend API.

    Returns:
        {status: "success", student_id, name, token} or {status: "error", message}
    """
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{api_url}/api/v1/student/login",
                json={"student_id": student_id, "password": password},
            )

            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                student_name = data.get("name", "")

                set_student_session(student_id, student_name, token)

                return {
                    "status": "success",
                    "student_id": student_id,
                    "name": student_name,
                    "token": token,
                }
            elif response.status_code == 401:
                return {
                    "status": "error",
                    "message": "Invalid credentials. Please check your student ID and password.",
                }
            elif response.status_code == 400:
                detail = response.json().get("detail", "Invalid request")
                return {
                    "status": "error",
                    "message": detail,
                }
            else:
                return {
                    "status": "error",
                    "message": f"Login failed with status {response.status_code}",
                }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection error: {str(e)}",
        }


def admin_login(
    api_url: str, email: str, password: str = None, google_id_token: str = None
) -> dict:
    """
    Login as admin via Supabase Auth.

    Supports:
    - Password-based login: email + password
    - Google OAuth: email + password=None (requires password=None or empty to trigger Google flow)

    Returns:
        {status: "success", email, role} or {status: "error", message}
    """
    try:
        from config import get_config

        config = get_config()
        supabase_url = config.get("supabase_url")
        supabase_anon_key = config.get("supabase_anon_key")

        if not supabase_url or not supabase_anon_key:
            return {
                "status": "error",
                "message": "Supabase configuration not found. Please check config.",
            }

        supabase: Client = create_client(supabase_url, supabase_anon_key)

        # Handle Google OAuth login (when password is None or empty)
        if not password and email:
            if google_id_token:
                response = supabase.auth.sign_in_with_id_token(
                    {"provider": "google", "token": google_id_token}
                )
            else:
                response = supabase.auth.sign_in_with_oauth(
                    {
                        "provider": "google",
                        "options": {
                            "email": email,
                            "redirect_to": "http://localhost:8001/callback",
                        },
                    }
                )
        else:
            response = supabase.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password,
                }
            )

        if response.user:
            user_email = response.user.email

            if not user_email.lower().endswith("@northsouth.edu"):
                return {
                    "status": "error",
                    "message": "Only @northsouth.edu accounts are allowed",
                }

            session = response.session
            set_admin_session(user_email, session.access_token)

            return {
                "status": "success",
                "email": user_email,
                "role": "admin",
                "token": session.access_token,
            }
        else:
            return {
                "status": "error",
                "message": "Login failed. Invalid credentials.",
            }

    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return {
                "status": "error",
                "message": "Invalid credentials. Please check your email and password.",
            }
        return {
            "status": "error",
            "message": f"Login error: {error_msg}",
        }


def admin_login_with_google(email: str, google_id_token: str = None) -> dict:
    """
    Login as admin via Supabase Auth using Google OAuth.

    This is used when user authenticates via Google OAuth first,
    then we link that to Supabase using the Google provider.

    Returns:
        {status: "success", email, role} or {status: "error", message}
    """
    try:
        from config import get_config
        import httpx

        config = get_config()
        supabase_url = config.get("supabase_url")
        supabase_anon_key = config.get("supabase_anon_key")

        if not supabase_url or not supabase_anon_key:
            return {
                "status": "error",
                "message": "Supabase configuration not found. Please check config.",
            }

        if not email.lower().endswith("@northsouth.edu"):
            return {
                "status": "error",
                "message": "Only @northsouth.edu accounts are allowed for admin access",
            }

        if not email:
            return {
                "status": "error",
                "message": "Email is required for Google OAuth login",
            }

        supabase: Client = create_client(supabase_url, supabase_anon_key)

        if google_id_token:
            try:
                response = supabase.auth.sign_in_with_id_token(
                    {"provider": "google", "token": google_id_token}
                )
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"sign_in_with_id_token failed: {str(e)}",
                }
        else:
            response = supabase.auth.sign_in_with_oauth(
                {
                    "provider": "google",
                    "options": {
                        "email": email,
                        "redirect_to": "http://localhost:8001/callback",
                    },
                }
            )

        # Handle OAuthResponse - use provider and url fields
        if hasattr(response, "provider") and response.provider == "google":
            # This is an OAuth redirect response - need to follow the URL
            auth_url = response.url
            return {
                "status": "redirect",
                "message": "Please complete Google OAuth in browser",
                "auth_url": auth_url,
            }

        # Check for session in response
        if hasattr(response, "session") and response.session:
            session = response.session
            user_email = session.user.email if hasattr(session.user, "email") else email

            if not user_email.lower().endswith("@northsouth.edu"):
                return {
                    "status": "error",
                    "message": "Only @northsouth.edu accounts are allowed",
                }

            set_admin_session(user_email, session.access_token)

            return {
                "status": "success",
                "email": user_email,
                "role": "admin",
                "token": session.access_token,
            }

        return {
            "status": "error",
            "message": "Google OAuth login failed. No valid session.",
        }

    except Exception as e:
        error_msg = str(e)
        return {
            "status": "error",
            "message": f"Google OAuth login error: {error_msg}",
        }


def verify_student_token(api_url: str, token: str) -> dict:
    """
    Verify student token by calling /api/v1/student/me endpoint.

    Returns:
        {valid: bool, student_id, name} or {valid: bool, error}
    """
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{api_url}/api/v1/student/me",
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "valid": True,
                    "student_id": data.get("student_id"),
                    "name": data.get("name"),
                }
            else:
                return {
                    "valid": False,
                    "error": "Token expired or invalid",
                }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
        }
