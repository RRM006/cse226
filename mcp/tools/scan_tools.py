import httpx
from typing import Optional, Any
from supabase import create_client, Client

from config import get_config
from auth.mcp_auth import get_session, UserRole


def get_supabase_client() -> Optional[Client]:
    """Create Supabase client using config."""
    config = get_config()
    supabase_url = config.get("supabase_url")
    supabase_anon_key = config.get("supabase_anon_key")

    if not supabase_url or not supabase_anon_key:
        return None

    return create_client(supabase_url, supabase_anon_key)


def get_scan_detail(scan_id: str) -> dict:
    """
    Get full details of a specific scan by ID.

    Args:
        scan_id: The scan ID to retrieve

    Returns:
        {status: "success", scan: {...}} or {status: "error", message}
    """
    session = get_session()
    config = get_config()
    api_url = config["api_url"]

    if not session.access_token:
        return {
            "status": "error",
            "message": "Not authenticated. Please login first.",
        }

    try:
        response = httpx.get(
            f"{api_url}/api/v1/history/{scan_id}",
            headers={"Authorization": f"Bearer {session.access_token}"},
            timeout=30.0,
        )

        if response.status_code == 200:
            return {
                "status": "success",
                "scan": response.json(),
            }
        elif response.status_code == 404:
            return {
                "status": "error",
                "message": "Scan not found",
            }
        elif response.status_code == 403:
            return {
                "status": "error",
                "message": "Not authorized to view this scan",
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to get scan: {response.status_code}",
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection error: {str(e)}",
        }


def delete_scan(scan_id: str) -> dict:
    """
    Delete a specific scan by ID.

    Args:
        scan_id: The scan ID to delete

    Returns:
        {status: "success", message} or {status: "error", message}
    """
    session = get_session()
    config = get_config()
    api_url = config["api_url"]

    if not session.access_token:
        return {
            "status": "error",
            "message": "Not authenticated. Please login first.",
        }

    try:
        response = httpx.delete(
            f"{api_url}/api/v1/history/{scan_id}",
            headers={"Authorization": f"Bearer {session.access_token}"},
            timeout=30.0,
        )

        if response.status_code == 200:
            return {
                "status": "success",
                "message": "Scan deleted successfully",
            }
        elif response.status_code == 404:
            return {
                "status": "error",
                "message": "Scan not found",
            }
        elif response.status_code == 403:
            return {
                "status": "error",
                "message": "Not authorized to delete this scan",
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to delete scan: {response.status_code}",
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection error: {str(e)}",
        }


def get_student_scans(
    student_id: str,
    limit: int = 20,
) -> dict:
    """
    Get all scans for a specific student.

    Args:
        student_id: The student ID to search for
        limit: Maximum number of records to return

    Returns:
        {status: "success", scans: [...]} or {status: "error", message}
    """
    session = get_session()
    config = get_config()
    api_url = config["api_url"]

    if not session.access_token:
        return {
            "status": "error",
            "message": "Not authenticated. Please login first.",
        }

    try:
        response = httpx.get(
            f"{api_url}/api/v1/history/student/scans",
            headers={"Authorization": f"Bearer {session.access_token}"},
            params={"limit": limit},
            timeout=30.0,
        )

        if response.status_code == 200:
            data = response.json()
            scans = data.get("scans", [])
            filtered = [s for s in scans if s.get("student_id") == student_id]
            return {
                "status": "success",
                "student_id": student_id,
                "total": len(filtered),
                "scans": filtered,
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to get student scans: {response.status_code}",
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection error: {str(e)}",
        }


def get_audit_statistics() -> dict:
    """
    Get aggregated audit statistics from Supabase.

    Returns:
        {status: "success", statistics: {...}} or {status: "error", message}
    """
    supabase = get_supabase_client()

    if not supabase:
        return {
            "status": "error",
            "message": "Supabase not configured",
        }

    try:
        total_response = supabase.table("scans").select("*", count="exact").execute()
        total_scans = total_response.count or 0

        programs = ["BSCSE", "BSEEE", "LLB"]
        program_stats = {}
        for prog in programs:
            prog_response = (
                supabase.table("scans")
                .select("*", count="exact")
                .eq("program", prog)
                .execute()
            )
            program_stats[prog] = prog_response.count or 0

        audit_levels = {}
        for level in [1, 2, 3]:
            level_response = (
                supabase.table("scans")
                .select("*", count="exact")
                .eq("audit_level", level)
                .execute()
            )
            audit_levels[f"L{level}"] = level_response.count or 0

        eligible_count = 0
        not_eligible_count = 0
        scans_response = supabase.table("scans").select("result_json").execute()
        for scan in scans_response.data:
            result_json = scan.get("result_json", {})
            if result_json.get("eligible", False):
                eligible_count += 1
            else:
                not_eligible_count += 1

        return {
            "status": "success",
            "statistics": {
                "total_scans": total_scans,
                "by_program": program_stats,
                "by_audit_level": audit_levels,
                "eligibility": {
                    "eligible": eligible_count,
                    "not_eligible": not_eligible_count,
                },
            },
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get statistics: {str(e)}",
        }
