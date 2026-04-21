"""
Request/Appeal tools for MCP server.
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


def submit_request(message: str, audit_result_id: str = None) -> dict[str, Any]:
    """
    Student submits a review/appeal request.

    Args:
        message: Request message (min 10 characters)
        audit_result_id: Optional audit result ID to link

    Returns:
        dict with request info
    """
    session = get_session()
    headers = get_auth_headers()

    if session.role != UserRole.STUDENT:
        return {
            "success": False,
            "error": "Only students can submit requests. Login as student first.",
        }

    if not headers.get("Authorization"):
        return {"success": False, "error": "Not authenticated."}

    if not message or len(message) < 10:
        return {"success": False, "error": "message must be at least 10 characters"}

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            payload = {"message": message}
            if audit_result_id:
                payload["audit_result_id"] = audit_result_id

            response = client.post(
                f"{api_url}/api/v1/student/requests", headers=headers, json=payload
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message": data.get("message", "Request submitted"),
                    "request_id": data.get("request_id"),
                    "status": data.get("status"),
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to submit request"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_my_requests(limit: int = 20, offset: int = 0) -> dict[str, Any]:
    """
    Student views own requests.

    Args:
        limit: Maximum results
        offset: Pagination offset

    Returns:
        dict with requests list
    """
    session = get_session()
    headers = get_auth_headers()

    if session.role != UserRole.STUDENT:
        return {"success": False, "error": "Only students can view their own requests."}

    if not headers.get("Authorization"):
        return {"success": False, "error": "Not authenticated."}

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{api_url}/api/v1/student/requests",
                headers=headers,
                params={"limit": limit, "offset": offset},
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "total": data.get("total", 0),
                    "requests": data.get("requests", []),
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to get requests"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_all_requests(limit: int = 20, offset: int = 0) -> dict[str, Any]:
    """
    Admin views all requests.

    Args:
        limit: Maximum results
        offset: Pagination offset

    Returns:
        dict with all requests
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
                f"{api_url}/api/v1/requests",
                headers=headers,
                params={"limit": limit, "offset": offset},
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "total": data.get("total", 0),
                    "requests": data.get("requests", []),
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to get requests"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_request_detail(request_id: str) -> dict[str, Any]:
    """
    Admin views specific request details.

    Args:
        request_id: UUID of the request

    Returns:
        dict with request details
    """
    session = get_session()
    headers = get_auth_headers()

    if session.role != UserRole.ADMIN:
        return {"success": False, "error": "Admin access required."}

    if not headers.get("Authorization"):
        return {"success": False, "error": "Not authenticated."}

    if not request_id:
        return {"success": False, "error": "request_id is required"}

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{api_url}/api/v1/requests/{request_id}", headers=headers
            )

            if response.status_code == 200:
                return {"success": True, "request": response.json()}
            elif response.status_code == 404:
                return {"success": False, "error": "Request not found"}
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to get request"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_request_status(
    request_id: str, status: str, admin_notes: str = None
) -> dict[str, Any]:
    """
    Admin updates request status.

    Args:
        request_id: UUID of the request
        status: reviewed, approved, or rejected
        admin_notes: Optional notes

    Returns:
        dict with success status
    """
    session = get_session()
    headers = get_auth_headers()

    if session.role != UserRole.ADMIN:
        return {"success": False, "error": "Admin access required."}

    if not headers.get("Authorization"):
        return {"success": False, "error": "Not authenticated."}

    if not request_id:
        return {"success": False, "error": "request_id is required"}

    valid_statuses = ["reviewed", "approved", "rejected"]
    if status not in valid_statuses:
        return {"success": False, "error": f"status must be one of {valid_statuses}"}

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            payload = {"status": status}
            if admin_notes:
                payload["admin_notes"] = admin_notes

            response = client.patch(
                f"{api_url}/api/v1/requests/{request_id}", headers=headers, json=payload
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message": data.get("message", "Request updated"),
                    "request_id": data.get("request_id"),
                    "status": data.get("status"),
                }
            elif response.status_code == 404:
                return {"success": False, "error": "Request not found"}
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to update request"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
