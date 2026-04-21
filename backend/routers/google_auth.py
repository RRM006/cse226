from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from auth import get_current_user

router = APIRouter(prefix="/api/v1/google-auth", tags=["google-auth"])


class GoogleTokenRequest(BaseModel):
    google_token: str


@router.post("/exchange")
async def exchange_google_token(
    request: GoogleTokenRequest,
    current_user: str = None,
):
    """
    Exchange a Google OAuth token for a Supabase JWT.
    The Google token comes from MCP's Google OAuth flow.
    """
    from config import settings
    from supabase import create_client
    import httpx

    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

    try:
        response = supabase.auth.sign_in_with_id_token(
            {
                "provider": "google",
                "token": request.google_token,
            }
        )

        if not response.session:
            raise HTTPException(status_code=401, detail="Invalid Google token")

        return {
            "access_token": response.session.access_token,
            "user_id": response.user.id,
            "email": response.user.email,
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token exchange failed: {str(e)}")
