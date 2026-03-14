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

from dotenv import load_dotenv

# Set up path before imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

from cli.credentials import (
    delete_credentials,
    is_logged_in,
    load_credentials,
    save_credentials,
    validate_nsu_email,
)


def build_supabase_oauth_url() -> str:
    """Build the Supabase Google OAuth URL."""
    supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    os.environ.get("SUPABASE_ANON_KEY", "")  # Required for config, not used in URL
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

        # If there are params suggesting completion
        if "access_token" in params or "code" in params or "error" in params:
            CallbackHandler.token_result["access_token"] = params.get(
                "access_token", [None]
            )[0]
            CallbackHandler.token_result["refresh_token"] = params.get(
                "refresh_token", [None]
            )[0]
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
            # We serve an HTML page that reads the URL fragment (where Supabase puts the token)
            # and redirects back to this same server with query parameters.
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
                    // Just unblock the local server
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
    oauth_url = build_supabase_oauth_url()

    if not oauth_url or not oauth_url.startswith("http"):
        print("❌ Login failed: SUPABASE_URL not configured.")
        print("   Please ensure backend/.env has SUPABASE_URL and SUPABASE_ANON_KEY")
        return

    print("Opening browser for NSU Google login...")
    print(f"URL: {oauth_url}")

    try:
        webbrowser.open(oauth_url)
    except Exception:
        print("Failed to open browser automatically.")
        print(f"Please open this URL manually: {oauth_url}")

    CallbackHandler.token_result = {}
    server = HTTPServer(("localhost", 54321), CallbackHandler)
    server.timeout = 1  # Use a short timeout so we can loop and check time

    print("Waiting for login... (timeout: 120 seconds)")

    import time
    start_time = time.time()
    # Handle requests until we get a result or hit the 120s timeout
    while not CallbackHandler.token_result and (time.time() - start_time) < 120:
        server.handle_request()

    server.server_close()

    if CallbackHandler.token_result.get("error"):
        print(f"❌ Login failed: {CallbackHandler.token_result.get('error')}")
        return

    access_token = CallbackHandler.token_result.get("access_token")
    refresh_token = CallbackHandler.token_result.get("refresh_token", "")

    if not access_token:
        print("❌ Login failed: no token received.")
        print("   The login may have been cancelled or timed out.")
        return

    email = decode_jwt_email(access_token)
    if not email:
        print("❌ Login failed: could not extract email from token.")
        return

    if not validate_nsu_email(email):
        print("❌ Login failed: only @northsouth.edu accounts are permitted.")
        print(f"   Your email: {email}")
        return

    save_credentials(access_token, refresh_token, email)
    print(f"✅ Logged in as {email}")


def cmd_logout():
    """Handle logout command."""
    delete_credentials()
    print("Logged out.")


def cmd_history():
    """Handle history command - fetch and display scan history from API."""
    if not is_logged_in():
        print("❌ You must be logged in to view history.")
        print("   Run: python cli/audit_cli.py login")
        raise SystemExit(1)
    
    import httpx
    
    creds = load_credentials()
    if not creds or not creds.get("access_token"):
        print("❌ Not logged in. Run 'audit-cli login' first.")
        raise SystemExit(1)
    
    api_url = os.environ.get("API_URL", "http://localhost:8000")
    headers = {"Authorization": f"Bearer {creds['access_token']}"}
    
    try:
        response = httpx.get(f"{api_url}/api/v1/history", headers=headers, timeout=30)
        if response.status_code == 401:
            print("❌ Session expired. Please run 'audit-cli login' again.")
            raise SystemExit(1)
        if response.status_code != 200:
            print(f"❌ Error fetching history: {response.status_code}")
            print(response.text)
            raise SystemExit(1)
        
        data = response.json()
        scans = data.get("scans", [])
        total = data.get("total", 0)
        
        if total == 0:
            print("\n📋 No scan history found.")
            return
        
        print(f"\n📋 Scan History ({total} total):")
        print("-" * 80)
        print(f"{'Date':<20} {'Type':<10} {'Program':<8} {'Level':<6} {'Status':<15}")
        print("-" * 80)
        
        for scan in scans:
            created = scan.get("created_at", "")
            if created:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    created = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            input_type = scan.get("input_type", "csv")
            program = scan.get("program", "-")
            level = scan.get("audit_level", "-")
            summary = scan.get("summary", {})
            eligible = summary.get("eligible")
            if eligible is True:
                status = "Eligible"
            elif eligible is False:
                status = "Not Eligible"
            else:
                status = "-"
            
            print(f"{created:<20} {input_type:<10} {program:<8} {level:<6} {status:<15}")
        
        print("-" * 80)
        
    except httpx.RequestError as e:
        print(f"❌ Network error: {e}")
        raise SystemExit(1)


def send_audit_to_api(result: dict, input_type: str = "csv", csv_text: str = "") -> bool:
    """Send audit result to API to save to history."""
    import httpx
    
    creds = load_credentials()
    if not creds or not creds.get("access_token"):
        print("⚠️ Not logged in - cannot save to history.")
        return False
    
    api_url = os.environ.get("API_URL", "http://localhost:8000")
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
            f"{api_url}/api/v1/audit/save",
            headers=headers,
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Saved to history (ID: {data.get('scan_id', 'N/A')})")
            return True
        else:
            print(f"\n⚠️ Failed to save to history: {response.status_code}")
            return False
    except httpx.RequestError as e:
        print(f"\n⚠️ Network error - could not save to history: {e}")
        return False


def require_login():
    """Exit with a message if user is not logged in."""
    if not is_logged_in():
        print("❌ You must be logged in to run audits with --remote.")
        print("   Run: python cli/audit_cli.py login")
        raise SystemExit(1)


def cmd_l1(csv_path: str, program: str = None, remote: bool = False):
    """Run Level 1 audit (credit tally)."""
    import asyncio
    from pathlib import Path
    
    if remote:
        require_login()
    
    csv_file = Path(csv_path)
    if not csv_file.is_absolute():
        csv_file = Path.cwd() / csv_path
    
    if not csv_file.exists():
        print(f"❌ File not found: {csv_file}")
        raise SystemExit(1)
    
    with open(csv_file, 'r') as f:
        csv_text = f.read()
    
    if remote:
        async def run_remote():
            from backend.services.audit_service import run_audit
            result = await run_audit(
                csv_text=csv_text,
                program=program or "BSCSE",
                audit_level=1,
                waivers=[],
                knowledge_file=""
            )
            print("\n" + "=" * 60)
            print(result.get("result_text", ""))
            print("=" * 60)
            send_audit_to_api(result, "csv", csv_text)
        
        asyncio.run(run_remote())
    else:
        from src.level1_credit_tally import main as level1_main
        sys.argv = ["level1_credit_tally", csv_path]
        level1_main()


def cmd_l2(csv_path: str, program: str = None, remote: bool = False):
    """Run Level 2 audit (CGPA calculation)."""
    import asyncio
    from pathlib import Path
    
    if remote:
        require_login()
    
    csv_file = Path(csv_path)
    if not csv_file.is_absolute():
        csv_file = Path.cwd() / csv_path
    
    if not csv_file.exists():
        print(f"❌ File not found: {csv_file}")
        raise SystemExit(1)
    
    with open(csv_file, 'r') as f:
        csv_text = f.read()
    
    if remote:
        async def run_remote():
            from backend.services.audit_service import run_audit
            result = await run_audit(
                csv_text=csv_text,
                program=program or "BSCSE",
                audit_level=2,
                waivers=[],
                knowledge_file=""
            )
            print("\n" + "=" * 60)
            print(result.get("result_text", ""))
            print("=" * 60)
            send_audit_to_api(result, "csv", csv_text)
        
        asyncio.run(run_remote())
    else:
        from src.level2_cgpa_calculator import main as level2_main
        sys.argv = ["level2_cgpa_calculator", csv_path]
        level2_main()


def cmd_l3(csv_path: str, program: str = None, remote: bool = False):
    """Run Level 3 audit (full graduation check)."""
    import asyncio
    from pathlib import Path
    
    if remote:
        require_login()
    
    project_root = Path(__file__).parent.parent
    csv_file = Path(csv_path)
    if not csv_file.is_absolute():
        csv_file = Path.cwd() / csv_path
    
    if not csv_file.exists():
        print(f"❌ File not found: {csv_file}")
        raise SystemExit(1)
    
    with open(csv_file, 'r') as f:
        csv_text = f.read()
    
    prog = program
    knowledge_path = None
    
    if prog and (prog.endswith('.md') or '/' in prog or '\\' in prog):
        knowledge_path = Path(prog)
        if not knowledge_path.is_absolute():
            knowledge_path = Path.cwd() / prog
    else:
        if not prog:
            from src.level3_audit_engine import parse_transcript
            _, prog, _ = parse_transcript(csv_path)
        knowledge_path = project_root / "program_knowledge" / f"program_knowledge_{prog}.md"
    
    if remote:
        async def run_remote():
            from backend.services.audit_service import run_audit
            result = await run_audit(
                csv_text=csv_text,
                program=prog or "BSCSE",
                audit_level=3,
                waivers=[],
                knowledge_file=str(knowledge_path)
            )
            print("\n" + "=" * 60)
            print(result.get("result_text", ""))
            print("=" * 60)
            send_audit_to_api(result, "csv", csv_text)
        
        asyncio.run(run_remote())
    else:
        from src.level3_audit_engine import main as level3_main
        sys.argv = ["level3_audit_engine", csv_path, str(knowledge_path)]
        level3_main()
        knowledge_path = project_root / "program_knowledge" / f"program_knowledge_{program}.md"

    # Phase 1 expects sys.argv format
    sys.argv = ["level3_audit_engine", csv_path, str(knowledge_path)]
    level3_main()


def get_ocr_audit_level():
    """Prompt user for audit level."""
    while True:
        try:
            level = input("Enter audit level (1, 2, or 3): ").strip()
            if level in ('1', '2', '3'):
                return int(level)
            print("Please enter 1, 2, or 3")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            raise SystemExit(0)


def get_ocr_program():
    """Prompt user for program."""
    while True:
        try:
            program = input("Enter program (BSCSE, BSEEE, or LLB): ").strip().upper()
            if program in ('BSCSE', 'BSEEE', 'LLB'):
                return program
            print("Please enter BSCSE, BSEEE, or LLB")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            raise SystemExit(0)


def get_ocr_file_path():
    """Prompt user for file path."""
    while True:
        try:
            file_path = input("Enter file path (PNG, JPG, or PDF): ").strip()
            if file_path:
                return file_path
            print("Please enter a file path")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            raise SystemExit(0)


def cmd_ocr(file_path: str = None, program: str = None, audit_level: int = None):
    """Run OCR on image/PDF and then audit."""
    require_login()
    
    import asyncio
    from pathlib import Path as FilePath
    
    # If no file path provided, ask interactively
    if not file_path:
        file_path = get_ocr_file_path()
    
    # Resolve file path
    file_path_obj = FilePath(file_path)
    if not file_path_obj.is_absolute():
        file_path_obj = FilePath.cwd() / file_path
    
    if not file_path_obj.exists():
        print(f"❌ File not found: {file_path_obj}")
        raise SystemExit(1)
    
    # Check file type
    ext = file_path_obj.suffix.lower()
    if ext not in ('.png', '.jpg', '.jpeg', '.pdf'):
        print("❌ File must be PNG, JPG, or PDF")
        raise SystemExit(1)
    
    print(f"\n📄 Processing: {file_path_obj.name}")
    print(f"🔍 Running OCR...")
    
    # Load file
    with open(file_path_obj, 'rb') as f:
        file_bytes = f.read()
    
    # Import backend services
    from backend.services.ocr_service import process_ocr, process_pdf_first_page
    from backend.services.audit_service import run_audit
    
    async def run_ocr_audit():
        # Convert PDF if needed
        if ext == '.pdf':
            img_bytes = await process_pdf_first_page(file_bytes)
        else:
            img_bytes = file_bytes
        
        # Run OCR
        ocr_result = await process_ocr(img_bytes)
        
        print(f"   OCR Confidence: {ocr_result.confidence_avg:.2f}")
        print(f"   Rows Extracted: {ocr_result.extracted_row_count}")
        
        if ocr_result.warnings:
            print(f"   Warnings: {len(ocr_result.warnings)}")
        
        if ocr_result.extracted_row_count == 0:
            print("❌ No course data could be extracted from the image")
            raise SystemExit(1)
        
        # Ask for program if not provided
        prog = program
        if not prog:
            prog = get_ocr_program()
        
        # Ask for audit level if not provided
        level = audit_level
        if level is None:
            level = get_ocr_audit_level()
        
        print(f"\n📊 Running Level {level} Audit for {prog}...")
        
        # Find knowledge file
        project_root = FilePath(__file__).parent.parent
        knowledge_file = project_root / "program_knowledge" / f"program_knowledge_{prog}.md"
        
        if level == 3 and not knowledge_file.exists():
            print(f"❌ Knowledge file not found: {knowledge_file}")
            raise SystemExit(1)
        
        # Run audit
        audit_result = await run_audit(
            csv_text=ocr_result.csv_text,
            program=prog,
            audit_level=level,
            waivers=[],
            knowledge_file=str(knowledge_file) if level == 3 else ""
        )
        
        return ocr_result, audit_result
    
    # Run async function
    try:
        ocr_result, audit_result = asyncio.run(run_ocr_audit())
    except Exception as e:
        print(f"❌ Error: {e}")
        raise SystemExit(1)
    
    # Print result
    print("\n" + "=" * 60)
    print(audit_result.get('result_text', 'No output'))
    print("=" * 60)
    
    # Print summary
    print("\n📋 SUMMARY:")
    print(f"   Program: {audit_result.get('program')}")
    print(f"   Level: {audit_result.get('audit_level')}")
    print(f"   Total Credits: {audit_result.get('total_credits')}")
    if audit_result.get('cgpa'):
        print(f"   CGPA: {audit_result.get('cgpa')}")
    if audit_result.get('standing'):
        print(f"   Standing: {audit_result.get('standing')}")
    if audit_result.get('eligible') is not None:
        print(f"   Eligible: {'Yes' if audit_result.get('eligible') else 'No'}")
    if audit_result.get('missing_courses'):
        print(f"   Missing Courses: {', '.join(audit_result.get('missing_courses', []))}")


def cmd_web(npm_cmd="npm"):
    """Run both backend and frontend for local development."""
    import subprocess
    import sys
    import os
    from pathlib import Path

    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend"
    frontend_dir = project_root / "frontend"

    print("=" * 60)
    print("Starting NSU Audit Core - Local Development")
    print("=" * 60)
    print("\nBackend: http://localhost:8000")
    print("Frontend: http://localhost:5173")
    print("\nPress Ctrl+C to stop both servers")
    print("=" * 60)

    backend_process = None
    frontend_process = None

    try:
        print("\n[1/2] Starting backend (FastAPI)...")
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
            cwd=str(backend_dir),
            env={**os.environ, "PYTHONPATH": str(backend_dir)},
        )

        print("[2/2] Starting frontend (Vite)...")
        frontend_process = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=str(frontend_dir),
        )

        print("\n✅ Both servers are running!")
        print("   Backend: http://localhost:8000")
        print("   Frontend: http://localhost:5173")

        backend_process.wait()
    except KeyboardInterrupt:
        print("\n\nShutting down servers...")
    finally:
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
        print("✅ Servers stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="NSU Audit Core CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/audit_cli.py login              # Login with NSU Google account
  python cli/audit_cli.py logout             # Logout
  python cli/audit_cli.py web                # Run both backend and frontend locally
  python cli/audit_cli.py l1 data/test.csv BSCSE   # Run Level 1 audit
  python cli/audit_cli.py l2 data/test.csv BSCSE   # Run Level 2 audit
  python cli/audit_cli.py l3 data/test.csv BSCSE   # Run Level 3 audit
  python cli/audit_cli.py l3 data/test.csv BSCSE --remote   # Run audit and save to history
  python cli/audit_cli.py ocr image.png           # OCR + audit (prompts for level)
  python cli/audit_cli.py ocr image.png BSEEE 3   # OCR + Level 3 audit
  python cli/audit_cli.py history                 # View scan history

Note: All audit commands (l1, l2, l3, ocr) work offline without login.
      Use --remote flag to save results to your account history.
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Login command
    subparsers.add_parser("login", help="Login with NSU Google account")

    # Logout command
    subparsers.add_parser("logout", help="Logout and clear credentials")

    # History command
    subparsers.add_parser("history", help="View your scan history")

    # Level 1 command
    l1_parser = subparsers.add_parser("l1", help="Run Level 1 audit (credit tally)")
    l1_parser.add_argument("csv", help="Path to CSV file")
    l1_parser.add_argument(
        "program",
        nargs="?",
        help="Program (BSCSE, BSEEE, LLB) - optional, detected from CSV",
    )
    l1_parser.add_argument(
        "--remote",
        action="store_true",
        help="Save result to your account history",
    )

    # Level 2 command
    l2_parser = subparsers.add_parser("l2", help="Run Level 2 audit (CGPA calculation)")
    l2_parser.add_argument("csv", help="Path to CSV file")
    l2_parser.add_argument(
        "program",
        nargs="?",
        help="Program (BSCSE, BSEEE, LLB) - optional, detected from CSV",
    )
    l2_parser.add_argument(
        "--remote",
        action="store_true",
        help="Save result to your account history",
    )

    # Level 3 command
    l3_parser = subparsers.add_parser(
        "l3", help="Run Level 3 audit (full graduation check)"
    )
    l3_parser.add_argument("csv", help="Path to CSV file")
    l3_parser.add_argument(
        "program",
        nargs="?",
        help="Program (BSCSE, BSEEE, LLB) - optional, detected from CSV",
    )
    l3_parser.add_argument(
        "--remote",
        action="store_true",
        help="Save result to your account history",
    )

    # OCR command
    ocr_parser = subparsers.add_parser(
        "ocr", help="Run OCR on image/PDF and then audit"
    )
    ocr_parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Path to image (PNG, JPG) or PDF file - will prompt if not provided"
    )
    ocr_parser.add_argument(
        "program",
        nargs="?",
        default=None,
        help="Program (BSCSE, BSEEE, LLB) - will prompt if not provided",
    )
    ocr_parser.add_argument(
        "level",
        nargs="?",
        type=int,
        default=None,
        help="Audit level (1, 2, or 3) - will prompt if not provided",
    )

    # Web command
    web_parser = subparsers.add_parser("web", help="Run both backend and frontend for local development")
    web_parser.add_argument(
        "npm",
        nargs="?",
        default="npm",
        help="Path to npm executable (default: npm)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "login":
        cmd_login()
    elif args.command == "logout":
        cmd_logout()
    elif args.command == "history":
        cmd_history()
    elif args.command == "l1":
        cmd_l1(args.csv, args.program, getattr(args, 'remote', False))
    elif args.command == "l2":
        cmd_l2(args.csv, args.program, getattr(args, 'remote', False))
    elif args.command == "l3":
        cmd_l3(args.csv, args.program, getattr(args, 'remote', False))
    elif args.command == "ocr":
        cmd_ocr(args.file, args.program, args.level)
    elif args.command == "web":
        cmd_web(args.npm)


if __name__ == "__main__":
    main()
