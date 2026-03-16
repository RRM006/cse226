import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from config import get_config
from auth.google_oauth import get_drive_service
from tools.drive_tools import list_drive_folder, get_transcript, search_drive
from tools.audit_tools import run_audit
from tools.email_tools import send_email
from tools.history_tools import get_audit_history
from tools.batch_tools import batch_audit_folder


app = Server("nsu-audit")


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
                        "description": "Name of the Google Drive folder to list files from"
                    },
                    "file_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional file types to filter (e.g. ['csv', 'pdf', 'png'])",
                        "default": []
                    }
                },
                "required": ["folder_name"]
            }
        ),
        Tool(
            name="get_transcript",
            description="Download a transcript file from Google Drive. Returns raw CSV text or base64-encoded image/PDF for OCR.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "The Google Drive file ID (from list_drive_folder)"
                    },
                    "file_name": {
                        "type": "string",
                        "description": "Optional human-readable name for the file",
                        "default": ""
                    }
                },
                "required": ["file_id"]
            }
        ),
        Tool(
            name="search_drive",
            description="Search for transcript files in Google Drive by student ID, name, or keyword.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query - student ID, name, or filename keyword"
                    },
                    "folder_name": {
                        "type": "string",
                        "description": "Optional folder name to limit search to",
                        "default": ""
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="run_audit",
            description="Run a graduation audit (L1, L2, or L3) on a transcript. " +
                        "L1: Credit tally. L2: CGPA calculation. L3: Full graduation audit with deficiencies. " +
                        "Use get_transcript first to get the CSV content from Drive.",
            inputSchema={
                "type": "object",
                "properties": {
                    "transcript_content": {
                        "type": "string",
                        "description": "Raw CSV text content (from get_transcript with content_type=csv)"
                    },
                    "program": {
                        "type": "string",
                        "description": "Program: BSCSE, BSEEE, or LLB"
                    },
                    "audit_level": {
                        "type": "integer",
                        "description": "Audit level: 1 (credits), 2 (CGPA), or 3 (full graduation)"
                    },
                    "waivers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of course codes to waive (e.g. ['ENG102'])",
                        "default": []
                    },
                    "student_email": {
                        "type": "string",
                        "description": "Optional student email for records",
                        "default": ""
                    }
                },
                "required": ["transcript_content", "program", "audit_level"]
            }
        ),
        Tool(
            name="send_email",
            description="Send a graduation audit result email via Gmail. " +
                        "Use after run_audit to email the results to a student.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "audit_result": {
                        "type": "object",
                        "description": "The result object from run_audit"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Optional custom email subject",
                        "default": ""
                    },
                    "cc": {
                        "type": "string",
                        "description": "Optional CC address",
                        "default": ""
                    },
                    "include_full_report": {
                        "type": "boolean",
                        "description": "Include full audit report in email body",
                        "default": True
                    }
                },
                "required": ["to", "audit_result"]
            }
        ),
        Tool(
            name="get_audit_history",
            description="Get past audit records from history. " +
                        "Returns records sorted by date (newest first).",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records to return",
                        "default": 20
                    },
                    "program": {
                        "type": "string",
                        "description": "Filter by program (BSCSE, BSEEE, LLB)",
                        "default": ""
                    },
                    "audit_level": {
                        "type": "integer",
                        "description": "Filter by audit level (1, 2, or 3)",
                        "default": 0
                    },
                    "eligible_only": {
                        "type": "boolean",
                        "description": "If true, return only eligible students",
                        "default": False
                    },
                    "since": {
                        "type": "string",
                        "description": "ISO date string to filter records after (e.g. '2026-03-01')",
                        "default": ""
                    }
                }
            }
        ),
        Tool(
            name="batch_audit_folder",
            description="Audit all transcripts in a Google Drive folder. " +
                        "Lists folder, downloads each CSV, runs audit, optionally emails results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_name": {
                        "type": "string",
                        "description": "Name of the Google Drive folder containing transcripts"
                    },
                    "program": {
                        "type": "string",
                        "description": "Program: BSCSE, BSEEE, or LLB"
                    },
                    "audit_level": {
                        "type": "integer",
                        "description": "Audit level: 1, 2, or 3",
                        "default": 3
                    },
                    "send_emails": {
                        "type": "boolean",
                        "description": "Send email to each student with their results",
                        "default": False
                    },
                    "email_domain": {
                        "type": "string",
                        "description": "Domain to construct student emails (e.g. 'northsouth.edu')",
                        "default": ""
                    },
                    "waivers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of course codes to waive",
                        "default": []
                    }
                },
                "required": ["folder_name", "program", "audit_level"]
            }
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
            result = run_audit(transcript_content, program, audit_level, waivers, str(student_email) if student_email else None)
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
                include_full_report
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
            result = get_audit_history(limit, program, audit_level, eligible_only, since)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "batch_audit_folder":
            folder_name = arguments.get("folder_name", "")
            program = arguments.get("program", "BSCSE")
            audit_level = arguments.get("audit_level", 3)
            send_emails = arguments.get("send_emails", False)
            email_domain = arguments.get("email_domain") or None
            waivers = arguments.get("waivers") or []
            result = batch_audit_folder(folder_name, program, audit_level, send_emails, email_domain, waivers)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def run_server():
    """Run the MCP server with stdio transport."""
    config = get_config()
    
    print(f"NSU Audit MCP Server starting...")
    print(f"  Mode: {'Remote' if config['remote'] else 'Offline'}")
    print(f"  API URL: {config['api_url']}")
    print(f"  Token path: {config['token_path']}")
    
    print("\nInitializing Google OAuth (opening browser for login)...")
    get_drive_service(
        config['token_path'],
        config['credentials_path'],
        config['reauth']
    )
    print("Google authentication successful!")
    
    print("\nStarting MCP server (stdio transport)...")
    print("Server ready. Press Ctrl+C to stop.")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Main entry point for the NSU Audit MCP server."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
