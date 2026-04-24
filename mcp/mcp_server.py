import asyncio
import json
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.streamable_http import StreamableHTTPServerTransport
from mcp.types import Tool, TextContent
import uvicorn

from config import get_config
from auth.google_oauth import get_drive_service, load_token
from tools.drive_tools import (
    list_drive_folder,
    get_transcript,
    search_drive,
    list_mcp_folders,
)
from tools.audit_tools import run_audit
from tools.email_tools import send_email
from tools.history_tools import (
    get_audit_history,
    get_offline_history,
    save_offline_audit,
)
from tools.batch_tools import batch_audit_folder
from tools.intent_parser import (
    parse_audit_query,
    format_clarification_request,
    validate_parsed_query,
)
from tools.auth_tools import (
    student_login,
    admin_login,
    admin_login_google,
    admin_login_oauth,
    complete_oauth_login,
    interactive_login,
    admin_autologin,
    get_current_user,
    change_password,
    logout,
    get_session_info,
)
from tools.history_api_tools import (
    get_history,
    get_scan_detail,
    delete_scan,
    get_all_scans,
    get_student_results,
    get_student_result_detail,
    get_student_scans,
    get_admin_results,
)
from tools.student_mgmt_tools import (
    create_student,
    list_students,
    get_student,
    update_student,
    reset_student_password,
    delete_student,
)
from tools.request_tools import (
    submit_request,
    get_my_requests,
    get_all_requests,
    get_request_detail,
    update_request_status,
)
from tools.audit_api_tools import (
    run_audit_csv,
    run_audit_ocr,
    run_audit_ocr_file,
    save_audit,
    save_audit_with_student,
)


app = Server("nsu-audit")


def check_token_status(token_path: Path) -> str:
    """
    Check if valid token exists.

    Returns:
        'valid' - Token exists and is valid
        'expired' - Token exists but expired, can refresh
        'missing' - No token file or invalid
    """
    creds = load_token(token_path)
    if not creds:
        return "missing"
    if creds.valid:
        return "valid"
    if creds.expired and creds.refresh_token:
        return "expired"
    return "missing"


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    Return the list of available tools for NSU Audit MCP server.
    """
    return [
        Tool(
            name="list_drive_folder",
            description="List all transcript files in a Google Drive folder. Use this to find transcript files to audit.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_name": {
                        "type": "string",
                        "description": "Name of the Google Drive folder to list files from",
                    },
                    "file_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional file types to filter (e.g. ['csv', 'pdf', 'png'])",
                        "default": [],
                    },
                },
                "required": ["folder_name"],
            },
        ),
        Tool(
            name="list_mcp_folders",
            description="List all Google Drive folders that contain 'mcp' in their name. Use this to find available MCP transcript folders.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="audit_from_query",
            description="Run a graduation audit from natural language query. "
            + "Example: 'Run L3 audit on the mcptest folder for BSCSE' or 'Check if student can graduate'. "
            + "Automatically parses intent and orchestrates folder listing, file download, and audit execution.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query (e.g., 'Run L3 audit on mcptest folder for BSCSE', 'Check transcript in mcp2.0')",
                    }
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_transcript",
            description="Download a transcript file from Google Drive. Returns raw CSV text or base64-encoded image/PDF for OCR.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "The Google Drive file ID (from list_drive_folder)",
                    },
                    "file_name": {
                        "type": "string",
                        "description": "Optional human-readable name for the file",
                        "default": "",
                    },
                },
                "required": ["file_id"],
            },
        ),
        Tool(
            name="search_drive",
            description="Search for transcript files in Google Drive by student ID, name, or keyword.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query - student ID, name, or filename keyword",
                    },
                    "folder_name": {
                        "type": "string",
                        "description": "Optional folder name to limit search to",
                        "default": "",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="run_audit",
            description="[DEPRECATED - use run_audit_csv] Run a graduation audit on transcript.",
            inputSchema={
                "type": "object",
                "properties": {
                    "transcript_content": {"type": "string"},
                    "program": {"type": "string"},
                    "audit_level": {"type": "integer"},
                    "waivers": {"type": "array", "items": {"type": "string"}},
                    "student_email": {"type": "string"},
                },
                "required": ["transcript_content", "program", "audit_level"],
            },
        ),
        Tool(
            name="send_email",
            description="Send a graduation audit result email via Gmail. "
            + "Use after run_audit to email the results to a student.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "audit_result": {
                        "type": "object",
                        "description": "The result object from run_audit",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Optional custom email subject",
                        "default": "",
                    },
                    "cc": {
                        "type": "string",
                        "description": "Optional CC address",
                        "default": "",
                    },
                    "include_full_report": {
                        "type": "boolean",
                        "description": "Include full audit report in email body",
                        "default": True,
                    },
                },
                "required": ["to", "audit_result"],
            },
        ),
        Tool(
            name="get_audit_history",
            description="[DEPRECATED - use get_history] Get past audit records.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records to return",
                        "default": 20,
                    },
                    "program": {
                        "type": "string",
                        "description": "Filter by program (BSCSE, BSEEE, LLB)",
                        "default": "",
                    },
                    "audit_level": {
                        "type": "integer",
                        "description": "Filter by audit level (1, 2, or 3)",
                        "default": 0,
                    },
                    "eligible_only": {
                        "type": "boolean",
                        "description": "If true, return only eligible students",
                        "default": False,
                    },
                    "since": {
                        "type": "string",
                        "description": "ISO date string to filter records after (e.g. '2026-03-01')",
                        "default": "",
                    },
                },
            },
        ),
        Tool(
            name="list_audit_history",
            description="List audit history from offline storage. Works without backend - shows all previous audits.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20},
                    "program": {"type": "string", "default": ""},
                    "audit_level": {"type": "integer", "default": 0},
                    "eligible_only": {"type": "boolean", "default": False},
                },
            },
        ),
        Tool(
            name="batch_audit_folder",
            description="Audit all transcripts in a Google Drive folder. "
            + "Lists folder, downloads each CSV, runs audit, optionally emails results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_name": {
                        "type": "string",
                        "description": "Name of the Google Drive folder containing transcripts",
                    },
                    "program": {
                        "type": "string",
                        "description": "Program: BSCSE, BSEEE, or LLB",
                    },
                    "audit_level": {
                        "type": "integer",
                        "description": "Audit level: 1, 2, or 3",
                        "default": 3,
                    },
                    "send_emails": {
                        "type": "boolean",
                        "description": "Send email to each student with their results",
                        "default": False,
                    },
                    "email_domain": {
                        "type": "string",
                        "description": "Domain to construct student emails (e.g. 'northsouth.edu')",
                        "default": "",
                    },
                    "waivers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of course codes to waive",
                        "default": [],
                    },
                },
                "required": ["folder_name", "program", "audit_level"],
            },
        ),
        Tool(
            name="student_login",
            description="Login as a student with student ID and password from database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "10-digit student ID",
                    },
                    "password": {"type": "string", "description": "Student password"},
                },
                "required": ["student_id", "password"],
            },
        ),
        Tool(
            name="admin_login",
            description="Login as admin with token (manual).",
            inputSchema={
                "type": "object",
                "properties": {
                    "access_token": {
                        "type": "string",
                        "description": "Supabase JWT token",
                    },
                },
                "required": ["access_token"],
            },
        ),
        Tool(
            name="admin_login_google",
            description="Get Google OAuth URL for admin login. Opens in browser, then use complete_oauth_login.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="admin_autologin",
            description="Quick admin login using debug key. Works without browser.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="complete_oauth_login",
            description="Complete admin login with callback URL from browser.",
            inputSchema={
                "type": "object",
                "properties": {
                    "callback_url": {
                        "type": "string",
                        "description": "Full URL after OAuth redirect",
                    },
                },
                "required": ["callback_url"],
            },
        ),
        Tool(
            name="get_session_info",
            description="Get current session info. Shows if logged in, role, student ID etc.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="run_audit_csv",
            description="Run audit on CSV transcript using backend API. Requires authentication.",
            inputSchema={
                "type": "object",
                "properties": {
                    "csv_content": {
                        "type": "string",
                        "description": "Raw CSV text content",
                    },
                    "program": {
                        "type": "string",
                        "description": "Program: BSCSE, BSEEE, or LLB",
                    },
                    "audit_level": {
                        "type": "integer",
                        "description": "Audit level: 1, 2, or 3 (REQUIRED)",
                    },
                    "waivers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of course codes to waive",
                    },
                },
                "required": ["csv_content", "program", "audit_level"],
            },
        ),
        Tool(
            name="run_audit_ocr",
            description="Run OCR audit on base64 image/PDF using backend API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_base64": {
                        "type": "string",
                        "description": "Base64-encoded image or PDF content",
                    },
                    "program": {
                        "type": "string",
                        "description": "Program: BSCSE, BSEEE, or LLB",
                    },
                    "audit_level": {
                        "type": "integer",
                        "description": "Audit level: 1, 2, or 3 (REQUIRED)",
                    },
                    "waivers": {"type": "array", "items": {"type": "string"}},
                    "file_type": {
                        "type": "string",
                        "description": "File type: png, jpg, jpeg, or pdf",
                    },
                },
                "required": ["image_base64", "program", "audit_level"],
            },
        ),
        Tool(
            name="run_audit_ocr_file",
            description="Run OCR audit on local image/PDF file (ADMIN ONLY). Provides file path directly.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Full path to image or PDF file",
                    },
                    "program": {
                        "type": "string",
                        "description": "Program: BSCSE, BSEEE, or LLB",
                    },
                    "audit_level": {
                        "type": "integer",
                        "description": "Audit level: 1, 2, or 3 (REQUIRED)",
                    },
                    "waivers": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["file_path", "program", "audit_level"],
            },
        ),
        Tool(
            name="save_audit",
            description="Save audit result without running a new audit.",
            inputSchema={
                "type": "object",
                "properties": {
                    "program": {"type": "string"},
                    "audit_level": {"type": "integer"},
                    "result_json": {"type": "object"},
                    "result_text": {"type": "string"},
                    "input_type": {"type": "string", "default": "csv"},
                    "waivers": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["program", "audit_level", "result_json", "result_text"],
            },
        ),
        Tool(
            name="save_audit_with_student",
            description="Save audit result and link to a specific student.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string"},
                    "program": {"type": "string"},
                    "audit_level": {"type": "integer"},
                    "result_json": {"type": "object"},
                    "result_text": {"type": "string"},
                    "input_type": {"type": "string", "default": "csv"},
                    "waivers": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "student_id",
                    "program",
                    "audit_level",
                    "result_json",
                    "result_text",
                ],
            },
        ),
        Tool(
            name="get_history",
            description="Get audit history (admin sees all, users see own).",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20},
                    "offset": {"type": "integer", "default": 0},
                },
            },
        ),
        Tool(
            name="get_scan_detail",
            description="Get specific scan details by scan ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "scan_id": {"type": "string"},
                },
                "required": ["scan_id"],
            },
        ),
        Tool(
            name="delete_scan",
            description="Delete a scan by scan ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "scan_id": {"type": "string"},
                },
                "required": ["scan_id"],
            },
        ),
        Tool(
            name="get_student_results",
            description="Student views own audit results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20},
                    "offset": {"type": "integer", "default": 0},
                },
            },
        ),
        Tool(
            name="get_student_scans",
            description="Student views own scan history.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20},
                    "offset": {"type": "integer", "default": 0},
                },
            },
        ),
        Tool(
            name="create_student",
            description="Create new student account (Admin only).",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string"},
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                },
                "required": ["student_id", "name", "email"],
            },
        ),
        Tool(
            name="list_students",
            description="List all students (Admin only).",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20},
                    "offset": {"type": "integer", "default": 0},
                },
            },
        ),
        Tool(
            name="get_student",
            description="Get student details by student ID (Admin only).",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string"},
                },
                "required": ["student_id"],
            },
        ),
        Tool(
            name="update_student",
            description="Update student info (Admin only).",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string"},
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                },
                "required": ["student_id"],
            },
        ),
        Tool(
            name="reset_student_password",
            description="Reset student password (Admin only).",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string"},
                    "new_password": {"type": "string"},
                },
                "required": ["student_id", "new_password"],
            },
        ),
        Tool(
            name="delete_student",
            description="Delete student account (Admin only).",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string"},
                },
                "required": ["student_id"],
            },
        ),
        Tool(
            name="submit_request",
            description="Student submits a review/appeal request.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "audit_result_id": {"type": "string"},
                },
                "required": ["message"],
            },
        ),
        Tool(
            name="get_my_requests",
            description="Student views own requests.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20},
                    "offset": {"type": "integer", "default": 0},
                },
            },
        ),
        Tool(
            name="get_all_requests",
            description="Admin views all requests.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20},
                    "offset": {"type": "integer", "default": 0},
                },
            },
        ),
        Tool(
            name="update_request_status",
            description="Admin updates request status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {"type": "string"},
                    "status": {"type": "string"},
                    "admin_notes": {"type": "string"},
                },
                "required": ["request_id", "status"],
            },
        ),
        Tool(
            name="change_password",
            description="Student changes password.",
            inputSchema={
                "type": "object",
                "properties": {
                    "current_password": {"type": "string"},
                    "new_password": {"type": "string"},
                },
                "required": ["current_password", "new_password"],
            },
        ),
        Tool(
            name="logout",
            description="Logout current session. Clears all authentication.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool calls from MCP clients.

    Args:
        name: Name of the tool to call
        arguments: Dictionary of arguments passed to the tool

    Returns:
        List of TextContent objects with the tool's response
    """
    try:
        if name == "list_drive_folder":
            folder_name = arguments.get("folder_name", "")
            file_types = arguments.get("file_types") or None
            result = list_drive_folder(folder_name, file_types)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "list_mcp_folders":
            result = list_mcp_folders()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "audit_from_query":
            query = arguments.get("query", "")

            mcp_folders = list_mcp_folders()
            available_folders = mcp_folders if isinstance(mcp_folders, list) else []

            parsed = parse_audit_query(query, available_folders)

            is_valid, error_msg = validate_parsed_query(parsed)
            if not is_valid:
                clarification = format_clarification_request(parsed)
                response = {
                    "status": "needs_clarification",
                    "message": error_msg,
                    "clarification_needed": clarification,
                    "parsed_intent": parsed,
                }
                return [TextContent(type="text", text=json.dumps(response, indent=2))]

            folder_name = parsed["folder_name"]
            program = parsed["program"]
            audit_level = parsed["audit_level"]
            file_name = parsed.get("file_name")
            send_email_flag = parsed.get("send_email", False)
            student_email = parsed.get("student_email")
            waivers = parsed.get("waivers", [])

            files = list_drive_folder(folder_name, ["csv"])

            if isinstance(files, str):
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"status": "error", "message": files}, indent=2
                        ),
                    )
                ]

            if not files:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "status": "error",
                                "message": f"No CSV files found in folder '{folder_name}'",
                            },
                            indent=2,
                        ),
                    )
                ]

            target_file = None
            if file_name:
                for f in files:
                    if file_name.lower() in f["file_name"].lower():
                        target_file = f
                        break
                if not target_file:
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {
                                    "status": "error",
                                    "message": f"File '{file_name}' not found in folder '{folder_name}'. Available files: {[f['file_name'] for f in files]}",
                                },
                                indent=2,
                            ),
                        )
                    ]
            else:
                target_file = files[0]

            transcript_result = get_transcript(
                target_file["file_id"], target_file["file_name"]
            )

            if isinstance(transcript_result, str):
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "status": "error",
                                "message": f"Failed to download transcript: {transcript_result}",
                            },
                            indent=2,
                        ),
                    )
                ]

            csv_content = transcript_result.get("content", "")
            if not csv_content:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "status": "error",
                                "message": "No content found in transcript file",
                            },
                            indent=2,
                        ),
                    )
                ]

            audit_result = run_audit(
                csv_content, program, audit_level, waivers, student_email
            )

            email_status = None
            if send_email_flag and student_email:
                email_resp = send_email(student_email, audit_result)
                email_status = email_resp

            response = {
                "status": "success",
                "parsed_intent": parsed,
                "file_audited": target_file["file_name"],
                "audit_result": audit_result,
                "email_sent": send_email_flag,
                "email_status": email_status,
            }
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        elif name == "get_transcript":
            file_id = arguments.get("file_id", "")
            file_name = arguments.get("file_name") or None
            result = get_transcript(file_id, file_name)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "search_drive":
            query = arguments.get("query", "")
            folder_name = arguments.get("folder_name") or None
            result = search_drive(query, folder_name)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "run_audit":
            transcript_content = arguments.get("transcript_content", "")
            program = arguments.get("program", "BSCSE")
            audit_level = arguments.get("audit_level", 3)
            waivers = arguments.get("waivers") or []
            student_email = arguments.get("student_email")
            result = run_audit(
                transcript_content,
                program,
                audit_level,
                waivers,
                str(student_email) if student_email else None,
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "send_email":
            to = arguments.get("to", "")
            audit_result = arguments.get("audit_result", {})
            subject_arg = arguments.get("subject")
            cc_arg = arguments.get("cc")
            include_full_report = arguments.get("include_full_report", True)
            result = send_email(
                to,
                audit_result,
                subject_arg if subject_arg else None,
                cc_arg if cc_arg else None,
                include_full_report,
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_audit_history":
            limit = arguments.get("limit", 20)
            program = arguments.get("program") or None
            audit_level = arguments.get("audit_level")
            eligible_only = arguments.get("eligible_only", False)
            since = arguments.get("since") or None
            if audit_level == 0:
                audit_level = None
            result = get_audit_history(
                limit, program, audit_level, eligible_only, since
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "list_audit_history":
            limit = arguments.get("limit", 20)
            program = arguments.get("program") or None
            audit_level = arguments.get("audit_level")
            eligible_only = arguments.get("eligible_only", False)
            if audit_level == 0:
                audit_level = None
            result = get_offline_history(limit, program, audit_level, eligible_only)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "batch_audit_folder":
            folder_name = arguments.get("folder_name", "")
            program = arguments.get("program", "BSCSE")
            audit_level = arguments.get("audit_level", 3)
            send_emails = arguments.get("send_emails", False)
            email_domain = arguments.get("email_domain") or None
            waivers = arguments.get("waivers") or []
            result = batch_audit_folder(
                folder_name, program, audit_level, send_emails, email_domain, waivers
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "student_login":
            result = student_login(
                arguments.get("student_id", ""), arguments.get("password", "")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "student_login_browser":
            result = student_login_browser()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "admin_login":
            result = admin_login(arguments.get("access_token", ""))
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "admin_login_google":
            result = admin_login_oauth()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "admin_autologin":
            result = admin_autologin()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "complete_oauth_login":
            result = complete_oauth_login(arguments.get("callback_url", ""))
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_session_info":
            result = get_session_info()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "run_audit_csv":
            result = run_audit_csv(
                arguments.get("csv_content", ""),
                arguments.get("program", "BSCSE"),
                arguments.get("audit_level"),
                arguments.get("waivers"),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "run_audit_ocr":
            result = run_audit_ocr(
                arguments.get("image_base64", ""),
                arguments.get("program", "BSCSE"),
                arguments.get("audit_level"),
                arguments.get("waivers"),
                arguments.get("file_type", "png"),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "run_audit_ocr_file":
            result = run_audit_ocr_file(
                arguments.get("file_path", ""),
                arguments.get("program", "BSCSE"),
                arguments.get("audit_level"),
                arguments.get("waivers"),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "save_audit":
            result = save_audit(
                arguments.get("program", ""),
                arguments.get("audit_level", 3),
                arguments.get("result_json", {}),
                arguments.get("result_text", ""),
                arguments.get("input_type", "csv"),
                "",
                arguments.get("waivers"),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "save_audit_with_student":
            result = save_audit_with_student(
                arguments.get("student_id", ""),
                arguments.get("program", ""),
                arguments.get("audit_level", 3),
                arguments.get("result_json", {}),
                arguments.get("result_text", ""),
                arguments.get("input_type", "csv"),
                "",
                arguments.get("waivers"),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_history":
            result = get_history(
                arguments.get("limit", 20),
                arguments.get("offset", 0),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_scan_detail":
            result = get_scan_detail(arguments.get("scan_id", ""))
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "delete_scan":
            result = delete_scan(arguments.get("scan_id", ""))
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_student_results":
            result = get_student_results(
                arguments.get("limit", 20),
                arguments.get("offset", 0),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_student_scans":
            result = get_student_scans(
                arguments.get("limit", 20),
                arguments.get("offset", 0),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "create_student":
            result = create_student(
                arguments.get("student_id", ""),
                arguments.get("name", ""),
                arguments.get("email", ""),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "list_students":
            result = list_students(
                arguments.get("limit", 20),
                arguments.get("offset", 0),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_student":
            result = get_student(arguments.get("student_id", ""))
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "update_student":
            result = update_student(
                arguments.get("student_id", ""),
                arguments.get("name"),
                arguments.get("email"),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "reset_student_password":
            result = reset_student_password(
                arguments.get("student_id", ""),
                arguments.get("new_password", ""),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "delete_student":
            result = delete_student(arguments.get("student_id", ""))
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "submit_request":
            result = submit_request(
                arguments.get("message", ""),
                arguments.get("audit_result_id"),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_my_requests":
            result = get_my_requests(
                arguments.get("limit", 20),
                arguments.get("offset", 0),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_all_requests":
            result = get_all_requests(
                arguments.get("limit", 20),
                arguments.get("offset", 0),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "update_request_status":
            result = update_request_status(
                arguments.get("request_id", ""),
                arguments.get("status", ""),
                arguments.get("admin_notes"),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "change_password":
            result = change_password(
                arguments.get("current_password", ""),
                arguments.get("new_password", ""),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "logout":
            result = logout()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def initialize_auth():
    """Initialize Google OAuth and return config."""
    config = get_config()

    token_status = check_token_status(config["token_path"])

    if token_status == "valid":
        print("\nUsing existing Google OAuth token...")
        get_drive_service(
            config["token_path"], config["credentials_path"], reauth=False
        )
        print("Token validated successfully!")
    elif token_status == "expired":
        print("\nToken expired, refreshing Google OAuth...")
        get_drive_service(
            config["token_path"], config["credentials_path"], reauth=False
        )
        print("Token refreshed successfully!")
    else:
        print("\nNo token found. Initializing Google OAuth (opening browser)...")
        get_drive_service(
            config["token_path"], config["credentials_path"], config["reauth"]
        )
        print("Google authentication successful!")

    return config


async def run_server_stdio():
    """DEPRECATED: stdio transport has been removed. Use HTTP instead."""
    print("ERROR: stdio transport is no longer supported.")
    print("Please use HTTP transport: python mcp_server.py --http")
    sys.exit(1)


class MCPSseServer(uvicorn.Server):
    """Custom Uvicorn server for MCP SSE transport."""

    def install_signal_handlers(self):
        pass


async def run_server_http(host: str = "127.0.0.1", port: int = 8001):
    """Run the MCP server with Streamable HTTP transport for remote clients."""
    config = get_config()

    print(f"NSU Audit MCP Server starting...")
    print(f"  Mode: Streamable HTTP (for opencode and remote clients)")
    print(f"  Token path: {config['token_path']}")

    await initialize_auth()

    from starlette.applications import Starlette
    from starlette.routing import Route, Mount
    from starlette.responses import JSONResponse
    import contextlib
    import asyncio

    transport = StreamableHTTPServerTransport(
        mcp_session_id=None,
        is_json_response_enabled=True,
    )

    @contextlib.asynccontextmanager
    async def lifespan(app_instance):
        async with transport.connect() as (read_stream, write_stream):
            task = asyncio.create_task(
                app.run(read_stream, write_stream, app.create_initialization_options())
            )
            yield
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def handle_mcp(request):
        await transport.handle_request(
            request.scope,
            request.receive,
            request._send,
        )

    async def homepage(request):
        return JSONResponse(
            {
                "service": "NSU Audit MCP Server",
                "status": "running",
                "transport": "Streamable HTTP",
                "endpoints": {"mcp": "/mcp", "health": "/health"},
            }
        )

    async def health(request):
        return JSONResponse({"status": "healthy"})

    starlette_app = Starlette(
        routes=[
            Route("/", homepage),
            Route("/health", health),
            Mount(
                "/mcp",
                app=lambda scope, receive, send: transport.handle_request(
                    scope, receive, send
                ),
            ),
        ],
        lifespan=lifespan,
    )

    config_uvicorn = uvicorn.Config(
        starlette_app,
        host=host,
        port=port,
        log_level="info",
    )
    server = MCPSseServer(config=config_uvicorn)

    print(f"\nMCP HTTP server running at http://{host}:{port}/mcp")
    print(f"opencode can connect using: http://{host}:{port}/mcp")
    print("Press Ctrl+C to stop.")

    await server.serve()


def main():
    """Main entry point for the NSU Audit MCP server."""
    config = get_config()

    # Auth-only mode: just authenticate and exit
    if config.get("auth_only", False):
        print("NSU Audit MCP Server - Auth Only Mode")
        print(f"  Token path: {config['token_path']}")

        # If --reauth is explicitly passed, always force re-authentication
        if config.get("reauth", False):
            print("\nForcing re-authentication as requested...")
            # Remove existing token to force fresh auth
            if config["token_path"].exists():
                config["token_path"].unlink()
            get_drive_service(
                config["token_path"], config["credentials_path"], reauth=True
            )
        else:
            token_status = check_token_status(config["token_path"])

            if token_status == "valid":
                print("\nToken already valid. No need to re-authenticate.")
                return 0
            elif token_status == "expired":
                print("\nToken expired, refreshing...")
                get_drive_service(
                    config["token_path"], config["credentials_path"], reauth=False
                )
            else:
                print(
                    "\nNo token found. Initializing Google OAuth (opening browser)..."
                )
                get_drive_service(
                    config["token_path"],
                    config["credentials_path"],
                    config.get("reauth", False),
                )

        print("\nAuthentication successful!")
        return 0

    # Override config with command line args
    port = config.get("http_port", 8001)
    asyncio.run(run_server_http(port=port))


if __name__ == "__main__":
    main()
