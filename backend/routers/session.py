import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/session", tags=["session"])


class SaveSessionRequest(BaseModel):
    access_token: str


@router.post("/save")
async def save_session(request: SaveSessionRequest):
    """
    Save the Supabase access token to a file that MCP can read.
    Called by frontend after successful login.
    """
    token_path = Path.home() / ".nsu_mcp" / "supabase_token.txt"
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(request.access_token)
    token_path.chmod(0o600)

    return {"status": "success", "message": "Session saved"}


@router.get("/load")
async def load_session():
    """
    Load the saved Supabase access token.
    Used by MCP to get auth token.
    """
    token_path = Path.home() / ".nsu_mcp" / "supabase_token.txt"
    if not token_path.exists():
        return {"status": "error", "message": "No session found"}

    access_token = token_path.read_text().strip()
    if not access_token:
        return {"status": "error", "message": "Empty session"}

    return {"status": "success", "access_token": access_token}


@router.post("/admin-login")
async def admin_login_session(request: SaveSessionRequest):
    """
    Create admin session from a Supabase access token.
    MCP calls this after getting a valid Supabase token.
    Saves the token for future MCP tool calls.

    For development: also accepts a special debug token to test MCP without full OAuth.
    """
    access_token = request.access_token
    import os

    # Check for special debug token (for testing only)
    if access_token == "dev-admin-token":
        debug_secret = os.getenv("MCP_DEBUG_SECRET", "")
        if not debug_secret:
            return {
                "status": "error",
                "message": "Debug login not enabled. Set MCP_DEBUG_SECRET env var.",
            }

        # Create debug token
        import jwt
        from datetime import datetime, timedelta, timezone

        token_payload = {
            "sub": "debug-user-001",
            "email": "admin@northsouth.edu",
            "role": "admin",
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        }
        debug_token = jwt.encode(token_payload, debug_secret, algorithm="HS256")

        # Save token
        token_path = Path.home() / ".nsu_mcp" / "supabase_token.txt"
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(debug_token)
        token_path.chmod(0o600)

        return {
            "status": "success",
            "message": "Debug admin session created",
            "access_token": debug_token[:20] + "...",
        }

    if not access_token or access_token == "fallback":
        return {"status": "error", "message": "Invalid token"}

    # Save token for MCP tools
    token_path = Path.home() / ".nsu_mcp" / "supabase_token.txt"
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(access_token)
    token_path.chmod(0o600)

    return {"status": "success", "message": "Admin session created"}
