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


def require_login():
    """Exit with a message if user is not logged in."""
    if not is_logged_in():
        print("❌ You must be logged in to run audits.")
        print("   Run: python cli/audit_cli.py login")
        raise SystemExit(1)


def cmd_l1(csv_path: str, program: str = None):
    """Run Level 1 audit (credit tally)."""
    require_login()
    # Import Phase 1 logic
    from src.level1_credit_tally import main as level1_main

    # Phase 1 expects sys.argv format
    sys.argv = ["level1_credit_tally", csv_path]
    level1_main()


def cmd_l2(csv_path: str, program: str = None):
    """Run Level 2 audit (CGPA calculation)."""
    require_login()
    # Import Phase 1 logic
    from src.level2_cgpa_calculator import main as level2_main

    # Phase 1 expects sys.argv format
    sys.argv = ["level2_cgpa_calculator", csv_path]
    level2_main()


def cmd_l3(csv_path: str, program: str = None):
    """Run Level 3 audit (full graduation check)."""
    require_login()
    # Import Phase 1 logic
    from src.level3_audit_engine import main as level3_main
    from src.level3_audit_engine import parse_transcript
    
    project_root = Path(__file__).parent.parent
    knowledge_path = None
    
    # If the second argument happens to be a markdown file instead of a program name
    if program and (program.endswith('.md') or '/' in program or '\\' in program):
        knowledge_path = Path(program)
        if not knowledge_path.is_absolute():
            # Treat it as relative to where the command was run
            knowledge_path = Path.cwd() / program
    else:
        if not program:
            _, program, _ = parse_transcript(csv_path)
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


def main():
    parser = argparse.ArgumentParser(
        description="NSU Audit Core CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/audit_cli.py login              # Login with NSU Google account
  python cli/audit_cli.py logout             # Logout
  python cli/audit_cli.py l1 data/test.csv BSCSE   # Run Level 1 audit
  python cli/audit_cli.py l2 data/test.csv BSCSE   # Run Level 2 audit
  python cli/audit_cli.py l3 data/test.csv BSCSE   # Run Level 3 audit
  python cli/audit_cli.py ocr image.png           # OCR + audit (prompts for level)
  python cli/audit_cli.py ocr image.png BSEEE 3   # OCR + Level 3 audit

Note: All audit commands (l1, l2, l3, ocr) require login with @northsouth.edu email.
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Login command
    subparsers.add_parser("login", help="Login with NSU Google account")

    # Logout command
    subparsers.add_parser("logout", help="Logout and clear credentials")

    # Level 1 command
    l1_parser = subparsers.add_parser("l1", help="Run Level 1 audit (credit tally)")
    l1_parser.add_argument("csv", help="Path to CSV file")
    l1_parser.add_argument(
        "program",
        nargs="?",
        help="Program (BSCSE, BSEEE, LLB) - optional, detected from CSV",
    )

    # Level 2 command
    l2_parser = subparsers.add_parser("l2", help="Run Level 2 audit (CGPA calculation)")
    l2_parser.add_argument("csv", help="Path to CSV file")
    l2_parser.add_argument(
        "program",
        nargs="?",
        help="Program (BSCSE, BSEEE, LLB) - optional, detected from CSV",
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

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "login":
        cmd_login()
    elif args.command == "logout":
        cmd_logout()
    elif args.command == "l1":
        cmd_l1(args.csv, args.program)
    elif args.command == "l2":
        cmd_l2(args.csv, args.program)
    elif args.command == "l3":
        cmd_l3(args.csv, args.program)
    elif args.command == "ocr":
        cmd_ocr(args.file, args.program, args.level)


if __name__ == "__main__":
    main()
