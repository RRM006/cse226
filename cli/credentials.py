import json
from pathlib import Path

CREDENTIALS_DIR = Path.home() / ".nsu_audit"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"
NSU_EMAIL_DOMAIN = "northsouth.edu"


def save_credentials(access_token: str, refresh_token: str, email: str) -> None:
    """Save JWT and user info to local credentials file."""
    CREDENTIALS_DIR.mkdir(exist_ok=True)
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "email": email,
            },
            f,
        )


def load_credentials() -> dict | None:
    """Load saved credentials. Returns None if not found."""
    if not CREDENTIALS_FILE.exists():
        return None
    with open(CREDENTIALS_FILE, "r") as f:
        return json.load(f)


def delete_credentials() -> None:
    """Remove credentials file on logout."""
    if CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.unlink()


def is_logged_in() -> bool:
    """Check if user is logged in."""
    return CREDENTIALS_FILE.exists()


def validate_nsu_email(email: str) -> bool:
    """Return True only if email ends with @northsouth.edu."""
    return email.strip().lower().endswith(f"@{NSU_EMAIL_DOMAIN}")
