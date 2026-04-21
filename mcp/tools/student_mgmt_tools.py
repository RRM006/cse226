"""
Student management tools for MCP server (Admin only).
"""

from typing import Any, Optional

import httpx

from config import get_config
from tools.auth_tools import get_auth_headers, get_session, UserRole


def _get_api_url() -> str:
    """Get API URL from config."""
    config = get_config()
    if isinstance(config, dict):
        return config.get("api_url", "http://localhost:8000")
    return config["api_url"]


def create_student(student_id: str, name: str, email: str) -> dict[str, Any]:
    """
    Create new student account (Admin only).

    Args:
        student_id: 10-digit student ID
        name: Student full name
        email: Student email

    Returns:
        dict with created student info
    """
    session = get_session()
    headers = get_auth_headers()

    if session.role != UserRole.ADMIN:
        return {"success": False, "error": "Admin access required."}

    if not headers.get("Authorization"):
        return {"success": False, "error": "Not authenticated."}

    if not student_id or len(student_id) != 10:
        return {"success": False, "error": "student_id must be 10 digits"}

    if not name:
        return {"success": False, "error": "name is required"}

    if not email:
        return {"success": False, "error": "email is required"}

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{api_url}/api/v1/students",
                headers=headers,
                json={"student_id": student_id, "name": name, "email": email},
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message": data.get("message", "Student created"),
                    "student_id": data.get("student_id"),
                    "default_password": data.get("default_password"),
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to create student"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_students(limit: int = 20, offset: int = 0) -> dict[str, Any]:
    """
    List all students (Admin only).

    Args:
        limit: Maximum results
        offset: Pagination offset

    Returns:
        dict with students list
    """
    session = get_session()
    headers = get_auth_headers()

    if session.role != UserRole.ADMIN:
        return {"success": False, "error": "Admin access required."}

    if not headers.get("Authorization"):
        return {"success": False, "error": "Not authenticated."}

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{api_url}/api/v1/students",
                headers=headers,
                params={"limit": limit, "offset": offset},
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "total": data.get("total", 0),
                    "students": data.get("students", []),
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to list students"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_student(student_id: str) -> dict[str, Any]:
    """
    Get student details (Admin only).

    Args:
        student_id: 10-digit student ID

    Returns:
        dict with student details
    """
    session = get_session()
    headers = get_auth_headers()

    if session.role != UserRole.ADMIN:
        return {"success": False, "error": "Admin access required."}

    if not headers.get("Authorization"):
        return {"success": False, "error": "Not authenticated."}

    if not student_id:
        return {"success": False, "error": "student_id is required"}

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{api_url}/api/v1/students/{student_id}", headers=headers
            )

            if response.status_code == 200:
                return {"success": True, "student": response.json()}
            elif response.status_code == 404:
                return {"success": False, "error": "Student not found"}
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to get student"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_student(
    student_id: str, name: str = None, email: str = None
) -> dict[str, Any]:
    """
    Update student info (Admin only).

    Args:
        student_id: 10-digit student ID
        name: New name (optional)
        email: New email (optional)

    Returns:
        dict with success status
    """
    session = get_session()
    headers = get_auth_headers()

    if session.role != UserRole.ADMIN:
        return {"success": False, "error": "Admin access required."}

    if not headers.get("Authorization"):
        return {"success": False, "error": "Not authenticated."}

    if not student_id:
        return {"success": False, "error": "student_id is required"}

    if not name and not email:
        return {"success": False, "error": "name or email is required"}

    api_url = _get_api_url()

    update_data = {}
    if name:
        update_data["name"] = name
    if email:
        update_data["email"] = email

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.patch(
                f"{api_url}/api/v1/students/{student_id}",
                headers=headers,
                json=update_data,
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "message": response.json().get("message", "Student updated"),
                }
            elif response.status_code == 404:
                return {"success": False, "error": "Student not found"}
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to update student"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def reset_student_password(student_id: str, new_password: str) -> dict[str, Any]:
    """
    Reset student password (Admin only).

    Args:
        student_id: 10-digit student ID
        new_password: New password (min 6 characters)

    Returns:
        dict with success status
    """
    session = get_session()
    headers = get_auth_headers()

    if session.role != UserRole.ADMIN:
        return {"success": False, "error": "Admin access required."}

    if not headers.get("Authorization"):
        return {"success": False, "error": "Not authenticated."}

    if not student_id:
        return {"success": False, "error": "student_id is required"}

    if not new_password or len(new_password) < 6:
        return {"success": False, "error": "new_password must be at least 6 characters"}

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.patch(
                f"{api_url}/api/v1/students/{student_id}/reset-password",
                headers=headers,
                json={"new_password": new_password},
            )

            if response.status_code == 200:
                return {"success": True, "message": "Password reset successfully"}
            elif response.status_code == 404:
                return {"success": False, "error": "Student not found"}
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to reset password"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_student(student_id: str) -> dict[str, Any]:
    """
    Delete student account (Admin only).

    Args:
        student_id: 10-digit student ID

    Returns:
        dict with success status
    """
    session = get_session()
    headers = get_auth_headers()

    if session.role != UserRole.ADMIN:
        return {"success": False, "error": "Admin access required."}

    if not headers.get("Authorization"):
        return {"success": False, "error": "Not authenticated."}

    if not student_id:
        return {"success": False, "error": "student_id is required"}

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.delete(
                f"{api_url}/api/v1/students/{student_id}", headers=headers
            )

            if response.status_code == 200:
                return {"success": True, "message": "Student deleted"}
            elif response.status_code == 404:
                return {"success": False, "error": "Student not found"}
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to delete student"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
