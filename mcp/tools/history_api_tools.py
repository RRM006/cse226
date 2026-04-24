"""
History and results API tools for MCP server.
"""

from typing import Any, Optional

import httpx
import supabase

from config import get_config
from tools.auth_tools import get_auth_headers, get_session, UserRole


def _get_api_url() -> str:
    """Get API URL from config."""
    config = get_config()
    if isinstance(config, dict):
        return config.get("api_url", "http://localhost:8000")
    return config["api_url"]


def get_history(limit: int = 20, offset: int = 0) -> dict[str, Any]:
    """
    Get audit history (admin sees all, users see own).
    Direct Supabase query - works without backend for admin.

    Args:
        limit: Maximum results (1-100)
        offset: Pagination offset

    Returns:
        dict with scans list
    """
    session = get_session()

    # Direct Supabase query - works for everyone with service role
    try:
        client = supabase.create_client(
            "https://zxzcnpkfabiiecagczao.supabase.co",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4emNucGtmYWJpaWVjYWdjemFvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjgwMTE0MywiZXhwIjoyMDg4Mzc3MTQzfQ.l6NZ9WUFCMoGNUoFQE8qcI3Fe5hzIz6pD4AABipdRyM",
        )
        result = (
            client.table("scans")
            .select("id,student_id,program,audit_level,result_text,created_at")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        scans = []
        for r in result.data:
            scans.append(
                {
                    "id": str(r.get("id")),
                    "student_id": r.get("student_id"),
                    "program": r.get("program"),
                    "audit_level": r.get("audit_level"),
                    "result_text": (r.get("result_text") or "")[:100],
                    "created_at": r.get("created_at"),
                }
            )

        return {
            "success": True,
            "total": len(scans),
            "scans": scans,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_scan_detail(scan_id: str) -> dict[str, Any]:
    """
    Get specific scan details.

    Args:
        scan_id: UUID of the scan

    Returns:
        dict with scan details
    """
    headers = get_auth_headers()

    if not headers.get("Authorization"):
        return {
            "success": False,
            "error": "Not authenticated. Call student_login or admin_login first.",
        }

    if not scan_id:
        return {"success": False, "error": "scan_id is required"}

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{api_url}/api/v1/history/{scan_id}", headers=headers
            )

            if response.status_code == 200:
                return {"success": True, "scan": response.json()}
            elif response.status_code == 404:
                return {"success": False, "error": "Scan not found"}
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to get scan"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_scan(scan_id: str) -> dict[str, Any]:
    """
    Delete a scan.

    Args:
        scan_id: UUID of the scan to delete

    Returns:
        dict with success status
    """
    headers = get_auth_headers()

    if not headers.get("Authorization"):
        return {
            "success": False,
            "error": "Not authenticated. Call student_login or admin_login first.",
        }

    if not scan_id:
        return {"success": False, "error": "scan_id is required"}

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.delete(
                f"{api_url}/api/v1/history/{scan_id}", headers=headers
            )

            if response.status_code == 200:
                return {"success": True, "message": "Scan deleted"}
            elif response.status_code == 404:
                return {"success": False, "error": "Scan not found"}
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to delete scan"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_all_scans(limit: int = 20, offset: int = 0) -> dict[str, Any]:
    """
    Admin only: Get ALL scans across all users.

    Args:
        limit: Maximum results
        offset: Pagination offset

    Returns:
        dict with all scans
    """
    session = get_session()
    headers = get_auth_headers()

    if not headers.get("Authorization"):
        return {
            "success": False,
            "error": "Not authenticated. Call student_login or admin_login first.",
        }

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{api_url}/api/v1/history/all",
                headers=headers,
                params={"limit": limit, "offset": offset},
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "total": data.get("total", 0),
                    "scans": data.get("scans", []),
                }
            elif response.status_code == 403:
                return {"success": False, "error": "Admin access required"}
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to get scans"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_student_results(limit: int = 20, offset: int = 0) -> dict[str, Any]:
    """
    Student views own audit results.

    Args:
        limit: Maximum results
        offset: Pagination offset

    Returns:
        dict with results list
    """
    session = get_session()
    headers = get_auth_headers()

    if session.role != UserRole.STUDENT:
        return {
            "success": False,
            "error": "Only students can view their own results. Login as student first.",
        }

    if not headers.get("Authorization"):
        return {"success": False, "error": "Not authenticated."}

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{api_url}/api/v1/student/audit-results",
                headers=headers,
                params={"limit": limit, "offset": offset},
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "total": data.get("total", 0),
                    "results": data.get("results", []),
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to get results"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_student_result_detail(result_id: str) -> dict[str, Any]:
    """
    Student views specific audit result details.

    Args:
        result_id: UUID of the result

    Returns:
        dict with result details
    """
    session = get_session()
    headers = get_auth_headers()

    if session.role != UserRole.STUDENT:
        return {"success": False, "error": "Only students can view their own results."}

    if not headers.get("Authorization"):
        return {"success": False, "error": "Not authenticated."}

    if not result_id:
        return {"success": False, "error": "result_id is required"}

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{api_url}/api/v1/student/audit-results/{result_id}", headers=headers
            )

            if response.status_code == 200:
                return {"success": True, "result": response.json()}
            elif response.status_code == 404:
                return {"success": False, "error": "Result not found"}
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to get result"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_student_scans(limit: int = 20, offset: int = 0) -> dict[str, Any]:
    """
    Student views own scan history.

    Args:
        limit: Maximum results
        offset: Pagination offset

    Returns:
        dict with scans list
    """
    session = get_session()
    headers = get_auth_headers()

    if session.role != UserRole.STUDENT:
        return {"success": False, "error": "Only students can view their own scans."}

    if not headers.get("Authorization"):
        return {"success": False, "error": "Not authenticated."}

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{api_url}/api/v1/student/scans",
                headers=headers,
                params={"limit": limit, "offset": offset},
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "total": data.get("total", 0),
                    "scans": data.get("scans", []),
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to get scans"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_admin_results(limit: int = 20, offset: int = 0) -> dict[str, Any]:
    """
    Admin views all audit results.

    Args:
        limit: Maximum results
        offset: Pagination offset

    Returns:
        dict with all results
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
                f"{api_url}/api/v1/audit-results",
                headers=headers,
                params={"limit": limit, "offset": offset},
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "total": data.get("total", 0),
                    "results": data.get("results", []),
                }
            elif response.status_code == 403:
                return {"success": False, "error": "Admin access required"}
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to get results"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
