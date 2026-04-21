"""
API-based audit tools for MCP server.
Uses backend API endpoints instead of offline engine.
"""

import base64
from pathlib import Path
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


VALID_PROGRAMS = ["BSCSE", "BSEEE", "LLB"]
VALID_AUDIT_LEVELS = [1, 2, 3]


def run_audit_csv(
    csv_content: str,
    program: str,
    audit_level: int = 3,
    waivers: list = None,
    knowledge_file: str = None,
) -> dict[str, Any]:
    """
    Run audit on CSV transcript using backend API.

    Args:
        csv_content: Raw CSV text content
        program: BSCSE, BSEEE, or LLB
        audit_level: 1, 2, or 3 (default: 3)
        waivers: Optional list of course codes to waive
        knowledge_file: Optional custom knowledge file name

    Returns:
        Audit result dict
    """
    program = program.upper()
    if program not in VALID_PROGRAMS:
        return {
            "success": False,
            "error": f"Invalid program. Must be one of {VALID_PROGRAMS}",
        }

    if audit_level not in VALID_AUDIT_LEVELS:
        return {"success": False, "error": f"Invalid audit_level. Must be 1, 2, or 3"}

    headers = get_auth_headers()
    if not headers.get("Authorization"):
        return {
            "success": False,
            "error": "Not authenticated. Call student_login or admin_login first.",
        }

    waivers = waivers or []
    waivers_str = ",".join(waivers) if waivers else ""

    api_url = _get_api_url()

    try:
        files = {"file": ("transcript.csv", csv_content.encode("utf-8"), "text/csv")}
        data = {
            "program": program,
            "audit_level": str(audit_level),
            "waivers": waivers_str,
        }
        if knowledge_file:
            data["knowledge_file"] = knowledge_file

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{api_url}/api/v1/audit/csv", files=files, data=data, headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "scan_id": result.get("scan_id"),
                    "student_id": result.get("student_id"),
                    "program": result.get("program"),
                    "audit_level": result.get("audit_level"),
                    "summary": result.get("summary", {}),
                    "result_text": result.get("result_text", ""),
                    "result_json": result.get("result_json", {}),
                    "created_at": result.get("created_at"),
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "Authentication failed. Please login again.",
                }
            else:
                error = response.json().get("detail", "Audit failed")
                return {"success": False, "error": str(error)}
    except httpx.ConnectError:
        return {
            "success": False,
            "error": f"Cannot connect to API at {api_url}. Is backend running?",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_audit_ocr(
    image_base64: str,
    program: str,
    audit_level: int = 3,
    waivers: list = None,
    file_type: str = "png",
) -> dict[str, Any]:
    """
    Run OCR audit on image/PDF using backend API.

    Args:
        image_base64: Base64-encoded image or PDF content
        program: BSCSE, BSEEE, or LLB
        audit_level: 1, 2, or 3 (default: 3)
        waivers: Optional list of course codes to waive
        file_type: File type (png, jpg, jpeg, pdf)

    Returns:
        Audit result dict with OCR details
    """
    program = program.upper()
    if program not in VALID_PROGRAMS:
        return {
            "success": False,
            "error": f"Invalid program. Must be one of {VALID_PROGRAMS}",
        }

    if audit_level not in VALID_AUDIT_LEVELS:
        return {"success": False, "error": f"Invalid audit_level. Must be 1, 2, or 3"}

    headers = get_auth_headers()
    if not headers.get("Authorization"):
        return {
            "success": False,
            "error": "Not authenticated. Call student_login or admin_login first.",
        }

    waivers = waivers or []
    waivers_str = ",".join(waivers) if waivers else ""

    api_url = _get_api_url()

    try:
        image_data = base64.b64decode(image_base64)

        files = {"file": (f"transcript.{file_type}", image_data, f"image/{file_type}")}
        data = {
            "program": program,
            "audit_level": str(audit_level),
            "waivers": waivers_str,
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{api_url}/api/v1/audit/ocr", files=files, data=data, headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "scan_id": result.get("scan_id"),
                    "student_id": result.get("student_id"),
                    "program": result.get("program"),
                    "audit_level": result.get("audit_level"),
                    "summary": result.get("summary", {}),
                    "result_text": result.get("result_text", ""),
                    "result_json": result.get("result_json", {}),
                    "created_at": result.get("created_at"),
                    "ocr_confidence": result.get("ocr_confidence"),
                    "ocr_extracted_rows": result.get("ocr_extracted_rows"),
                    "ocr_warnings": result.get("ocr_warnings", []),
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "Authentication failed. Please login again.",
                }
            elif response.status_code == 422:
                return {
                    "success": False,
                    "error": f"OCR failed: {response.json().get('detail', 'Low confidence')}",
                }
            else:
                error = response.json().get("detail", "OCR audit failed")
                return {"success": False, "error": str(error)}
    except httpx.ConnectError:
        return {
            "success": False,
            "error": f"Cannot connect to API at {api_url}. Is backend running?",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def save_audit(
    program: str,
    audit_level: int,
    result_json: dict,
    result_text: str,
    input_type: str = "csv",
    raw_input: str = "",
    waivers: list = None,
) -> dict[str, Any]:
    """
    Save audit result without running a new audit.

    Args:
        program: BSCSE, BSEEE, or LLB
        audit_level: 1, 2, or 3
        result_json: Result JSON object
        result_text: Result text summary
        input_type: csv or ocr
        raw_input: Raw input data
        waivers: List of waived courses

    Returns:
        dict with scan_id
    """
    program = program.upper()
    headers = get_auth_headers()

    if not headers.get("Authorization"):
        return {
            "success": False,
            "error": "Not authenticated. Call student_login or admin_login first.",
        }

    waivers = waivers or []

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{api_url}/api/v1/audit/save",
                headers=headers,
                json={
                    "program": program,
                    "audit_level": audit_level,
                    "result_json": result_json,
                    "result_text": result_text,
                    "input_type": input_type,
                    "raw_input": raw_input,
                    "waivers": waivers,
                },
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "scan_id": result.get("scan_id"),
                    "message": result.get("message", "Audit saved"),
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Save failed"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def save_audit_with_student(
    student_id: str,
    program: str,
    audit_level: int,
    result_json: dict,
    result_text: str,
    input_type: str = "csv",
    raw_input: str = "",
    waivers: list = None,
) -> dict[str, Any]:
    """
    Save audit result and link to a student.

    Args:
        student_id: 10-digit student ID
        program: BSCSE, BSEEE, or LLB
        audit_level: 1, 2, or 3
        result_json: Result JSON object
        result_text: Result text summary
        input_type: csv or ocr
        raw_input: Raw input data
        waivers: List of waived courses

    Returns:
        dict with scan_id and student_id
    """
    program = program.upper()
    headers = get_auth_headers()

    if not headers.get("Authorization"):
        return {
            "success": False,
            "error": "Not authenticated. Call student_login or admin_login first.",
        }

    if not student_id or len(student_id) != 10:
        return {"success": False, "error": "student_id must be 10 digits"}

    waivers = waivers or []

    api_url = _get_api_url()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{api_url}/api/v1/audit/save-with-student-id",
                headers=headers,
                json={
                    "student_id": student_id,
                    "program": program,
                    "audit_level": audit_level,
                    "result_json": result_json,
                    "result_text": result_text,
                    "input_type": input_type,
                    "raw_input": raw_input,
                    "waivers": waivers,
                },
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "scan_id": result.get("scan_id"),
                    "student_id": result.get("student_id"),
                    "program": result.get("program"),
                    "audit_level": result.get("audit_level"),
                    "summary": result.get("summary", {}),
                    "result_text": result.get("result_text", ""),
                    "created_at": result.get("created_at"),
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Save failed"),
                }
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {api_url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
