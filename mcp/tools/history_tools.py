import httpx
from datetime import datetime
from typing import Optional, Any

from config import get_config
from history.local_log import get_records as get_local_records
from auth.mcp_auth import get_session


def save_audit_to_database(
    student_id: str,
    program: str,
    audit_level: int,
    result_json: dict,
    result_text: str,
    input_type: str = "csv",
) -> dict:
    """
    Save audit result to Supabase database via backend API.

    Args:
        student_id: Student ID
        program: Program code (BSCSE, BSEEE, LLB)
        audit_level: 1, 2, or 3
        result_json: Full result dictionary
        result_text: Formatted result text
        input_type: Type of input (csv, ocr_image)

    Returns:
        {status: "success", scan_id} or {status: "error", message}
    """
    config = get_config()
    session = get_session()

    if not session.access_token:
        return {
            "status": "error",
            "message": "Not authenticated. Please login first.",
        }

    api_url = config["api_url"]

    eligible = result_json.get("eligible", False)

    data = {
        "student_id": student_id,
        "program": program,
        "audit_level": audit_level,
        "input_type": input_type,
        "result_json": result_json,
        "result_text": result_text,
        "eligible": eligible,
    }

    try:
        response = httpx.post(
            f"{api_url}/api/v1/audit/save",
            json=data,
            headers={"Authorization": f"Bearer {session.access_token}"},
            timeout=30.0,
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "status": "success",
                "scan_id": result.get("scan_id"),
                "message": "Audit saved to database",
            }
        elif response.status_code == 401:
            return {
                "status": "error",
                "message": "Authentication expired. Please login again.",
            }
        else:
            detail = response.json().get("detail", "Failed to save audit")
            return {
                "status": "error",
                "message": detail,
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection error: {str(e)}",
        }


def get_audit_history(
    limit: int = 20,
    program: Optional[str] = None,
    audit_level: Optional[int] = None,
    eligible_only: bool = False,
    since: Optional[str] = None,
    student_id: Optional[str] = None,
) -> list[dict[str, Any]]:
    """
        Get audit history records.

        Offline mode: reads from local history.json
        Remote mode: calls FastAPI backend

        Args:
            limit: Maximum number of records to return
            program: Filter by program (BSCSE, BSEEE, LLB)
            audit_level: Filter by audit level (1, 2, 3)
            eligible_only: If True, return only eligible records
            since: ISO date string to filter records after
            student_id: Filter by student ID (for students to see only their own records)

    Returns:
            List of {scan_id, student_id, program, audit_level, cgpa, eligible, created_at}
    """
    config = get_config()
    session = get_session()

    # Try remote API first - ensures admins get data from database
    remote_result = _get_history_remote(
        limit, program, audit_level, eligible_only, since, config, student_id
    )
    # If remote returned data (success), use it
    if remote_result:
        return remote_result

    # Remote empty/failed - fallback to local only for students (offline mode)
    if student_id:
        return _get_history_local(
            limit, program, audit_level, eligible_only, since, student_id
        )

    # For admins without student_id, remote should work - return empty if API failed
    return []


def _get_history_local(
    limit: int,
    program: Optional[str],
    audit_level: Optional[int],
    eligible_only: bool,
    since: Optional[str],
    student_id: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Get history from local JSON file."""
    records = get_local_records(
        limit=limit,
        program=program,
        audit_level=audit_level,
        eligible_only=eligible_only,
        since=since,
    )

    filtered = records
    if student_id:
        filtered = [r for r in records if r.get("student_id") == student_id]

    return [
        {
            "scan_id": r.get("scan_id", r.get("student_id", "")),
            "student_id": r.get("student_id", "Unknown"),
            "program": r.get("program", "Unknown"),
            "audit_level": r.get("audit_level", 3),
            "cgpa": r.get("cgpa", 0.0),
            "eligible": r.get("eligible", False),
            "created_at": r.get("created_at", ""),
        }
        for r in filtered
    ]


def _get_history_remote(
    limit: int,
    program: Optional[str],
    audit_level: Optional[int],
    eligible_only: bool,
    since: Optional[str],
    config: dict,
    student_id: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Get history from FastAPI backend."""
    api_url = config["api_url"]

    session = get_session()

    # Try access_token first (from Google OAuth), then api_token
    api_token = session.access_token or session.api_token

    # If no token or invalid token, try multiple fallbacks
    if not api_token or api_token in ("", "fallback"):
        # Fallback 1: Try backend session endpoint
        try:
            response = httpx.get(f"{api_url}/api/v1/session/load", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    api_token = data.get("access_token")
        except Exception:
            pass

    # Fallback 2: Try reading from stored token files
    if not api_token or api_token in ("", "fallback"):
        try:
            from pathlib import Path

            token_files = [
                Path.home() / ".nsu_mcp" / "supabase_token.txt",
                Path.home() / ".nsu_mcp" / "api_token.txt",
            ]
            for tf in token_files:
                if tf.exists():
                    token_content = tf.read_text().strip()
                    if token_content and token_content not in ("", "fallback"):
                        api_token = token_content
                        break
        except Exception:
            pass

    if not api_token or api_token in ("", "fallback"):
        return []

    headers = {"Authorization": f"Bearer {api_token}"}

    params: dict = {"limit": limit}
    if program:
        params["program"] = program
    if audit_level is not None:
        params["audit_level"] = audit_level
    if eligible_only:
        params["eligible_only"] = True
    if since:
        params["since"] = since
    if student_id:
        params["student_id"] = student_id

    try:
        response = httpx.get(
            f"{api_url}/api/v1/history", headers=headers, params=params, timeout=30.0
        )

        if response.status_code == 200:
            records = response.json()
            return [
                {
                    "scan_id": r.get("scan_id", r.get("student_id", "")),
                    "student_id": r.get("student_id", "Unknown"),
                    "program": r.get("program", "Unknown"),
                    "audit_level": r.get("audit_level", 3),
                    "cgpa": r.get("cgpa", 0.0),
                    "eligible": r.get("eligible", False),
                    "created_at": r.get("created_at", ""),
                }
                for r in records
            ]
        else:
            return []

    except Exception:
        return []
