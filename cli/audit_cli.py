#!/usr/bin/env python3
"""
NSU Audit Core CLI - Phase 2
Google OAuth login with NSU email restriction.
"""

import argparse
import base64
import json
import os
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx
from dotenv import load_dotenv

for _path in [
    Path(__file__).parent.parent / "archive",
    Path(__file__).parent.parent,
    Path(__file__).parent.parent / "backend",
]:
    if _path.exists():
        sys.path.insert(0, str(_path))

from cli.ui import (
    console,
    print_title,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_menu_item,
    print_header,
    print_divider,
    prompt_input,
    prompt_yes_no,
    prompt_choice,
    print_table,
    clear_screen,
    RICH_AVAILABLE,
    install_rich,
)
from cli.credentials import (
    delete_credentials,
    is_logged_in,
    load_credentials,
    save_credentials,
    validate_nsu_email,
)

if not RICH_AVAILABLE:
    install_rich()

load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

API_URL = os.environ.get("API_URL", "http://localhost:8000")


def build_supabase_oauth_url() -> str:
    """Build the Supabase Google OAuth URL."""
    supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    if not supabase_url:
        return ""
    redirect = "http://localhost:54321/callback"
    return (
        f"{supabase_url}/auth/v1/authorize"
        f"?provider=google"
        f"&redirect_to={redirect}"
        f"&scope=email"
    )


def decode_jwt_email(token: str) -> str:
    """Extract email from JWT payload without verifying signature."""
    try:
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return payload.get("email", "")
    except Exception:
        return ""


class CallbackHandler(BaseHTTPRequestHandler):
    """Handler for OAuth callback."""

    token_result = {}

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if self.path == '/favicon.ico':
            self.send_response(404)
            self.end_headers()
            return

        if "access_token" in params or "code" in params or "error" in params:
            CallbackHandler.token_result["access_token"] = params.get("access_token", [None])[0]
            CallbackHandler.token_result["refresh_token"] = params.get("refresh_token", [None])[0]
            CallbackHandler.token_result["code"] = params.get("code", [None])[0]
            CallbackHandler.token_result["error"] = params.get("error", [None])[0]

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            if "error" in params:
                self.wfile.write(b"<h2>Login error. Return to your terminal.</h2>")
            else:
                self.wfile.write(b"<h2>Login complete. Return to your terminal.</h2><script>setTimeout(function(){window.close();}, 2000);</script>")
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
            <!DOCTYPE html>
            <html>
            <head><title>Processing Login...</title></head>
            <body>
            <h2>Processing login...</h2>
            <script>
            window.onload = function() {
                if (window.location.hash) {
                    window.location.replace("/callback?" + window.location.hash.substring(1));
                } else if (window.location.search) {
                    window.location.replace("/callback" + window.location.search);
                } else {
                    document.body.innerHTML = "<h2>No token found in URL. Return to your terminal.</h2>";
                    window.location.replace("/callback?error=no_token");
                }
            };
            </script>
            </body>
            </html>
            """)

    def log_message(self, format, *args):
        pass


def cmd_login():
    """Handle login command with Google OAuth."""
    if is_logged_in():
        creds = load_credentials()
        if creds:
            print_info(f"Already logged in as: {creds.get('email', 'unknown')}")
            if not prompt_yes_no("Do you want to login with a different account?"):
                return True
            delete_credentials()

    # Pre-prompt for email as requested
    print_header("Login")
    while True:
        email_input = prompt_input("Enter your North South University email")
        if not email_input:
            print_error("Email cannot be empty.")
            continue
        if not email_input.endswith("@northsouth.edu"):
            print_error("Invalid email. Only @northsouth.edu accounts are allowed.")
            print_info("Please try again.")
            continue
        break

    oauth_url = build_supabase_oauth_url()

    if not oauth_url or not oauth_url.startswith("http"):
        print_error("Login failed: SUPABASE_URL not configured.")
        print_info("Please ensure backend/.env has SUPABASE_URL and SUPABASE_ANON_KEY")
        return False

    print_info("Opening browser for NSU Google login...")
    print(f"URL: {oauth_url}\n")

    try:
        webbrowser.open(oauth_url)
    except Exception:
        print_warning("Failed to open browser automatically.")
        print_info(f"Please open this URL manually: {oauth_url}")

    CallbackHandler.token_result = {}
    server = HTTPServer(("localhost", 54321), CallbackHandler)
    server.timeout = 1

    print_info("Waiting for login... (timeout: 120 seconds)")
    print("Press Ctrl+C to cancel\n")

    import time
    start_time = time.time()
    while not CallbackHandler.token_result and (time.time() - start_time) < 120:
        server.handle_request()

    server.server_close()

    if CallbackHandler.token_result.get("error"):
        error_msg = CallbackHandler.token_result.get('error', 'Unknown error')
        print_error(f"Login failed: {error_msg}")
        return False

    access_token = CallbackHandler.token_result.get("access_token")
    refresh_token = CallbackHandler.token_result.get("refresh_token", "")

    if not access_token:
        print_error("Login failed: no token received.")
        print_info("The login may have been cancelled or timed out.")
        return False

    email = decode_jwt_email(access_token)
    if not email:
        print_error("Login failed: could not extract email from token.")
        return False

    if not validate_nsu_email(email):
        print_error("Login failed: only @northsouth.edu accounts are permitted.")
        print_info(f"Your email: {email}")
        return False

    save_credentials(access_token, refresh_token, email)
    print_success(f"Logged in as {email}")
    return True


def cmd_logout():
    """Handle logout command."""
    if not is_logged_in():
        print_info("You are not logged in.")
        return True

    creds = load_credentials()
    email = creds.get("email", "Unknown") if creds else "Unknown"

    delete_credentials()
    print_success(f"Logged out successfully ({email})")
    return True


def cmd_history():
    """Handle history command - fetch and display scan history from API."""
    if not is_logged_in():
        print_error("You must be logged in to view history.")
        print_info("Run: python cli/audit_cli.py login")
        return False

    creds = load_credentials()
    if not creds or not creds.get("access_token"):
        print_error("Session expired. Please run 'login' again.")
        return False

    headers = {"Authorization": f"Bearer {creds['access_token']}"}

    try:
        response = httpx.get(f"{API_URL}/api/v1/history", headers=headers, timeout=30)
        if response.status_code == 401:
            print_error("Session expired. Please run 'login' again.")
            delete_credentials()
            return False
        if response.status_code != 200:
            print_error(f"Error fetching history: {response.status_code}")
            return False

        data = response.json()
        scans = data.get("scans", [])
        total = data.get("total", 0)

        if total == 0:
            print_header("Scan History")
            print_info("No scan history found.")
            return True

        print_header(f"Scan History ({total} total)")

        rows = []
        for scan in scans:
            created = scan.get("created_at", "")
            if created:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    created = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pass

            input_type = scan.get("input_type", "csv")
            program = scan.get("program", "-")
            level = scan.get("audit_level", "-")
            summary = scan.get("summary", {})
            eligible = summary.get("eligible")
            if eligible is True:
                status = "[green]Eligible[/green]"
            elif eligible is False:
                status = "[red]Not Eligible[/red]"
            else:
                status = "-"

            rows.append([created, input_type, program, level, status])

        if RICH_AVAILABLE:
            from cli.ui import create_table
            table = create_table(['Date', 'Type', 'Program', 'Level', 'Status'], rows)
            console.print(table)
        else:
            print_table(['Date', 'Type', 'Program', 'Level', 'Status'], rows)

        return True

    except httpx.RequestError as e:
        print_error(f"Network error: {e}")
        return False


def send_audit_to_api(result: dict, input_type: str = "csv", csv_text: str = "") -> bool:
    """Send audit result to API to save to history."""
    creds = load_credentials()
    if not creds or not creds.get("access_token"):
        print_warning("Not logged in - cannot save to history.")
        return False

    headers = {"Authorization": f"Bearer {creds['access_token']}"}
    result_json = result.get("result_json", {})

    payload = {
        "student_id": result_json.get("student_id", ""),
        "program": result_json.get("program", ""),
        "input_type": input_type,
        "raw_input": csv_text,
        "waivers": result_json.get("waivers_applied", []),
        "audit_level": result_json.get("audit_level"),
        "result_json": result_json,
        "result_text": result.get("result_text", ""),
    }

    try:
        response = httpx.post(
            f"{API_URL}/api/v1/audit/save",
            headers=headers,
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print_success(f"Saved to history (ID: {data.get('scan_id', 'N/A')})")
            return True
        else:
            print_warning(f"Failed to save to history: {response.status_code}")
            return False
    except httpx.RequestError as e:
        print_warning(f"Network error - could not save to history: {e}")
        return False


def require_login() -> bool:
    """Return False if user is not logged in (for interactive prompts)."""
    if not is_logged_in():
        print_error("You must be logged in to run this command.")
        print_info("Run: python cli/audit_cli.py login")
        return False
    return True


def get_csv_path(prompt_msg: str = "Enter CSV or OCR file path") -> str | None:
    """Prompt for CSV or image path with validation and re-prompt on invalid input."""
    while True:
        csv_path = prompt_input(prompt_msg)
        if not csv_path:
            print_error("Please enter a file path.")
            continue

        csv_file = Path(csv_path)
        if not csv_file.is_absolute():
            csv_file = Path.cwd() / csv_path

        if not csv_file.exists():
            print_error(f"File not found: {csv_file}")
            print_info("Please enter a valid file path.")
            continue

        if not csv_file.is_file():
            print_error(f"Not a file: {csv_file}")
            continue

        return csv_path


def get_program() -> str | None:
    """Prompt for program selection with validation."""
    programs = ['BSCSE', 'BSEEE', 'LLB']
    print_header("Select Program")
    idx = prompt_choice("Choose program", programs)
    if idx >= 0 and idx < len(programs):
        return programs[idx]
    return None


def get_audit_level() -> int | None:
    """Prompt for audit level with validation."""
    levels = ['Level 1 - Credit Tally', 'Level 2 - CGPA Calculator', 'Level 3 - Full Audit']
    print_header("Select Audit Level")
    idx = prompt_choice("Choose audit level", levels)
    if idx >= 0 and idx < len(levels):
        return idx + 1
    return None


def run_audit_offline(csv_path: str, level: int, program: str = None) -> bool:
    """Run audit using Phase 1 archive engine (offline mode)."""
    try:
        if level == 1:
            from src.level1_credit_tally import main as level_main
            sys.argv = ["level1_credit_tally", csv_path]
        elif level == 2:
            from src.level2_cgpa_calculator import main as level_main
            sys.argv = ["level2_cgpa_calculator", csv_path]
        elif level == 3:
            from src.level3_audit_engine import main as level_main, parse_transcript
            prog = program
            if not prog:
                _, prog, _ = parse_transcript(csv_path)
            project_root = Path(__file__).parent.parent
            knowledge_path = project_root / "program_knowledge" / f"program_knowledge_{prog}.md"
            sys.argv = ["level3_audit_engine", csv_path, str(knowledge_path)]
        else:
            print_error(f"Invalid audit level: {level}")
            return False

        level_main()
        return True
    except Exception as e:
        print_error(f"Error running audit: {e}")
        return False


async def run_audit_remote(csv_path: str, level: int, program: str = None, remote: bool = False) -> dict | None:
    """Run audit using backend service (remote mode)."""
    try:
        from backend.services.audit_service import run_audit

        with open(csv_path, 'r') as f:
            csv_text = f.read()

        prog = program or "BSCSE"
        knowledge_file = ""
        if level == 3:
            project_root = Path(__file__).parent.parent
            knowledge_file = str(project_root / "program_knowledge" / f"program_knowledge_{prog}.md")

        result = await run_audit(
            csv_text=csv_text,
            program=prog,
            audit_level=level,
            waivers=[],
            knowledge_file=knowledge_file
        )
        return result
    except Exception as e:
        print_error(f"Error running remote audit: {e}")
        return None


def cmd_audit(level: int, csv_path: str = None, program: str = None, remote: bool = False):
    """Run audit at specified level (generic handler for L1, L2, L3)."""
    level_names = {1: "Credit Tally", 2: "CGPA Calculator", 3: "Full Graduation Audit"}
    level_name = level_names.get(level, f"Level {level}")

    if remote and not require_login():
        return False

    print_header(f"Level {level} Audit - {level_name}")

    if not csv_path:
        csv_path = get_csv_path()
        if not csv_path:
            return False

    csv_file = Path(csv_path)
    if not csv_file.is_absolute():
        csv_file = Path.cwd() / csv_path

    if not csv_file.exists():
        print_error(f"File not found: {csv_file}")
        return False

    ext = csv_file.suffix.lower()
    if ext in ['.png', '.jpg', '.jpeg', '.pdf']:
        return cmd_ocr(file_path=str(csv_file), program=program, audit_level=level, remote=remote)

    prog = program
    if not prog:
        try:
            from src.level3_audit_engine import parse_transcript
            _, prog, _ = parse_transcript(csv_path)
            if prog:
                print_info(f"Detected program: {prog}")
        except Exception:
            pass

        if not prog:
            prog = get_program()
            if not prog:
                return False

    print_info(f"Program: {prog}")
    print_info(f"CSV: {csv_file}")
    print_info(f"Mode: {'Remote (saves to history)' if remote else 'Offline'}")
    print_divider()

    if remote:
        import asyncio
        result = asyncio.run(run_audit_remote(csv_path, level, prog, remote))
        if result:
            print_divider()
            print(result.get("result_text", ""))
            print_divider()
            with open(csv_file, 'r') as f:
                csv_text = f.read()
            send_audit_to_api(result, "csv", csv_text)
            return True
        return False
    else:
        return run_audit_offline(csv_path, level, prog)


def cmd_l1(csv_path: str = None, program: str = None, remote: bool = False):
    """Run Level 1 audit (credit tally)."""
    return cmd_audit(1, csv_path, program, remote)


def cmd_l2(csv_path: str = None, program: str = None, remote: bool = False):
    """Run Level 2 audit (CGPA calculation)."""
    return cmd_audit(2, csv_path, program, remote)


def cmd_l3(csv_path: str = None, program: str = None, remote: bool = False):
    """Run Level 3 audit (full graduation check)."""
    return cmd_audit(3, csv_path, program, remote)


def cmd_ocr(file_path: str = None, program: str = None, audit_level: int = None, remote: bool = False):
    """Run OCR on image/PDF and then audit."""
    if remote and not require_login():
        return False

    print_header("OCR Transcript Processing")

    if not file_path:
        file_path = prompt_input("Enter file path (PNG, JPG, or PDF)")
        if not file_path:
            print_error("No file path provided.")
            return False

    file_path_obj = Path(file_path)
    if not file_path_obj.is_absolute():
        file_path_obj = Path.cwd() / file_path

    if not file_path_obj.exists():
        print_error(f"File not found: {file_path_obj}")
        return False

    ext = file_path_obj.suffix.lower()
    if ext not in ('.png', '.jpg', '.jpeg', '.pdf'):
        print_error("File must be PNG, JPG, or PDF")
        return False

    print_info(f"Processing: {file_path_obj.name}")

    if audit_level is None:
        audit_level = get_audit_level()
        if audit_level is None:
            return False

    print_info(f"Running OCR processing...")

    try:
        import asyncio
        from backend.services.ocr_service import process_ocr, process_pdf_first_page
        from backend.services.audit_service import run_audit

        async def run_ocr_audit():
            with open(file_path_obj, 'rb') as f:
                file_bytes = f.read()

            if ext == '.pdf':
                img_bytes = await process_pdf_first_page(file_bytes)
            else:
                img_bytes = file_bytes

            ocr_result = await process_ocr(img_bytes)

            print_success(f"OCR Confidence: {ocr_result.confidence_avg:.2f}")
            print_info(f"Rows Extracted: {ocr_result.extracted_row_count}")

            if ocr_result.warnings:
                print_warning(f"Warnings: {len(ocr_result.warnings)}")

            if ocr_result.extracted_row_count == 0:
                print_error("No course data could be extracted from the image")
                return None, None

            # Auto-detect program from OCR result
            prog = program
            if not prog:
                try:
                    from src.level3_audit_engine import parse_transcript
                    _, prog, _ = parse_transcript(ocr_result.csv_text)
                    if prog:
                        print_info(f"Detected program: {prog}")
                except Exception:
                    pass
                
                if not prog:
                    prog = get_program()
                    if not prog:
                        return None, None

            print_info(f"Running {audit_level} audit for {prog}...")

            project_root = Path(__file__).parent.parent
            knowledge_file = str(project_root / "program_knowledge" / f"program_knowledge_{prog}.md")

            if audit_level == 3:
                knowledge_file_path = Path(knowledge_file)
                if not knowledge_file_path.exists():
                    print_error(f"Knowledge file not found: {knowledge_file_path}")
                    return None, None

            audit_result = await run_audit(
                csv_text=ocr_result.csv_text,
                program=prog,
                audit_level=audit_level,
                waivers=[],
                knowledge_file=knowledge_file if audit_level == 3 else ""
            )

            # Keep prog in audit_result for printing
            if 'result_json' in audit_result and 'program' not in audit_result['result_json']:
                audit_result['result_json']['program'] = prog

            return ocr_result, audit_result, prog

        res = asyncio.run(run_ocr_audit())
        if not res or res[1] is None:
            return False
            
        ocr_result, audit_result, final_prog = res

        if audit_result is None:
            return False

        print_divider()
        print(audit_result.get('result_text', 'No output'))
        print_divider()

        print_header("SUMMARY")
        result_json = audit_result.get('result_json', audit_result)
        print(f"  Program: {result_json.get('program', program)}")
        print(f"  Level: {result_json.get('audit_level', audit_level)}")
        print(f"  Total Credits: {result_json.get('total_credits', 'N/A')}")
        if result_json.get('cgpa'):
            print(f"  CGPA: {result_json.get('cgpa')}")
        if result_json.get('standing'):
            print(f"  Standing: {result_json.get('standing')}")
        if result_json.get('eligible') is not None:
            eligible = result_json.get('eligible')
            status = "[green]Eligible[/green]" if eligible else "[red]Not Eligible[/red]"
            print(f"  Eligible: {status}")
        if result_json.get('missing_courses'):
            print(f"  Missing Courses: {', '.join(result_json.get('missing_courses', []))}")

        if remote:
            send_audit_to_api(audit_result, "ocr", ocr_result.csv_text if ocr_result else "")

        return True

    except Exception as e:
        print_error(f"Error: {e}")
        return False


def show_help():
    """Display help information."""
    print_title("NSU Audit Core CLI - Help")

    if RICH_AVAILABLE:
        from rich.columns import Columns
        from rich.panel import Panel

        panels = [
            Panel("[cyan]python cli/audit_cli.py login[/cyan]\nLogin with NSU Google account", title="Login", border_style="green"),
            Panel("[cyan]python cli/audit_cli.py logout[/cyan]\nLogout and clear credentials", title="Logout", border_style="red"),
            Panel("[cyan]python cli/audit_cli.py history[/cyan]\nView your scan history", title="History", border_style="blue"),
            Panel("[cyan]python cli/audit_cli.py web[/cyan]\nRun backend and frontend locally", title="Web", border_style="yellow"),
        ]
        console.print(Columns(panels))

    print()
    print_header("Audit Commands")
    print("  python cli/audit_cli.py l1 <csv> [program] [--remote]")
    print("      Run Level 1 audit (Credit Tally)")
    print()
    print("  python cli/audit_cli.py l2 <csv> [program] [--remote]")
    print("      Run Level 2 audit (CGPA Calculator)")
    print()
    print("  python cli/audit_cli.py l3 <csv> [program] [--remote]")
    print("      Run Level 3 audit (Full Graduation Check)")
    print()
    print("  python cli/audit_cli.py ocr <file> [program] [level]")
    print("      Run OCR on image/PDF and audit")
    print()
    print_header("Authentication")
    print("  --remote flag saves results to your account history")
    print("  Login required for remote mode and history")
    print()
    print_header("Interactive Mode")
    print("  Run without arguments for interactive menu:")
    print("  python cli/audit_cli.py")


def show_welcome():
    """Display welcome screen."""
    print_title("NSU Audit Core CLI")
    print()
    if is_logged_in():
        creds = load_credentials()
        email = creds.get("email", "Unknown") if creds else "Unknown"
        print_success(f"Logged in as: {email}")
    else:
        print_info("Not logged in (remote mode disabled)")
    print()


def interactive_menu():
    """Show interactive menu with arrow key navigation."""
    from cli.ui import interactive_menu_prompt, pause
    
    options = [
        "Offline Mode",
        "Remote Mode",
        "History",
        "Login",
        "Logout",
        "Help",
        "Exit"
    ]

    while True:
        subtitle = ""
        if is_logged_in():
            creds = load_credentials()
            email = creds.get("email", "Unknown") if creds else "Unknown"
            if RICH_AVAILABLE:
                subtitle = f"[bold green]✓[/bold green] Logged in: {email}"
            else:
                subtitle = f"✅ Logged in: {email}"
        else:
            if RICH_AVAILABLE:
                subtitle = "[bold yellow]![/bold yellow] Not logged in"
            else:
                subtitle = "⚠️  Not logged in"

        try:
            selected_idx = interactive_menu_prompt("=== MAIN MENU ===", subtitle, options)
        except (EOFError, KeyboardInterrupt):
            print("\n")
            print_info("Exiting...")
            break
            
        choice = options[selected_idx]
        clear_screen()
        
        try:
            if choice == "Exit":
                print_success("Goodbye!")
                break
            
            elif choice == "Help":
                show_help()
                pause()
                
            elif choice == "Logout":
                cmd_logout()
                pause()
                
            elif choice == "History":
                cmd_history()
                pause()
                
            elif choice == "Login":
                success = cmd_login()
                if success:
                    pause()
                else:
                    print_info("\nPress Enter to return to menu...")
                    try:
                        prompt_input("Press Enter to continue")
                    except (EOFError, KeyboardInterrupt):
                        pass
                    
            elif choice == "Offline Mode":
                print_header("Offline Mode")
                level = get_audit_level()
                if level:
                    cmd_audit(level=level, remote=False)
                pause()
                    
            elif choice == "Remote Mode":
                print_header("Remote Mode")
                if not is_logged_in():
                    print_warning("You must login first")
                    pause("Press Enter to go to Login...")
                    cmd_login()
                    # After login, check if successful
                    if not is_logged_in():
                        continue # return to menu
                    clear_screen()
                    print_header("Remote Mode")
                    
                level = get_audit_level()
                if level:
                    cmd_audit(level=level, remote=True)
                pause()

        except (EOFError, KeyboardInterrupt):
            print("\n")
            print_warning("Operation cancelled.")


def main():
    import sys
    if len(sys.argv) > 1:
        print_error("Error: Command-line arguments are no longer supported.")
        print_info("Please simply run 'cli' (or 'python cli/audit_cli.py') without arguments to use the interactive menu.")
        sys.exit(1)

    show_welcome()
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")


if __name__ == "__main__":
    main()
