import os
import argparse
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


def get_config():
    """Parse CLI arguments and return configuration dictionary."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reauth",
        action="store_true",
        default=False,
        help="Force re-authentication with Google OAuth",
    )
    parser.add_argument(
        "--auth-only",
        action="store_true",
        default=False,
        help="Only authenticate and exit, do not start server",
    )
    parser.add_argument(
        "--http",
        action="store_true",
        default=True,
        help="Use HTTP transport (default: enabled for OpenCode compatibility)",
    )
    parser.add_argument(
        "--http-port",
        type=int,
        default=8001,
        help="Port for HTTP transport (default: 8001)",
    )
    args = parser.parse_args()

    base_dir = Path.home() / ".nsu_mcp"
    base_dir.mkdir(exist_ok=True)

    # Always use local backend
    api_url = os.getenv("API_URL", "http://localhost:8000")

    # Supabase configuration for admin auth
    supabase_url = os.getenv("SUPABASE_URL", "https://zxzcnpkfabiiecagczao.supabase.co")
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY", "your-anon-key")

    return {
        "reauth": args.reauth,
        "auth_only": args.auth_only,
        "api_url": api_url,
        "http": args.http,
        "http_port": args.http_port,
        "token_path": base_dir / "token.json",
        "credentials_path": Path(__file__).parent / "credentials.json",
        "history_path": base_dir / "history.json",
        "api_token_path": base_dir / "api_token.txt",
        "supabase_url": supabase_url,
        "supabase_anon_key": supabase_anon_key,
    }
