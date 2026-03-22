import json
import os
from pathlib import Path
from typing import Tuple

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]


def load_token(token_path: Path) -> Credentials | None:
    """Load OAuth2 token from file if it exists."""
    if not token_path.exists():
        return None
    
    try:
        with open(token_path, 'r') as f:
            token_data = json.load(f)
        return Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes'),
        )
    except Exception:
        return None


def save_token(token: Credentials, token_path: Path) -> None:
    """Save OAuth2 token to file."""
    token_path.parent.mkdir(parents=True, exist_ok=True)
    with open(token_path, 'w') as f:
        f.write(token.to_json())
    os.chmod(token_path, 0o600)


def authenticate(token_path: Path, credentials_path: Path) -> Credentials:
    """Perform browser-based OAuth2 authentication."""
    print("Opening browser for Google OAuth authentication...", flush=True)
    print("If no browser opens, please visit the URL shown in the browser.", flush=True)
    
    flow = InstalledAppFlow.from_client_secrets_file(
        str(credentials_path), 
        SCOPES
    )
    credentials = flow.run_local_server(
        port=8080, 
        open_browser=True,
        redirect_uri_pattern="http://localhost:8080/*"
    )
    save_token(credentials, token_path)
    print("Authentication successful! Token saved.", flush=True)
    return credentials


def get_google_services(
    token_path: Path,
    credentials_path: Path,
    reauth: bool = False
) -> Tuple[build, build]:
    """
    Get authenticated Google Drive and Gmail service instances.
    
    Handles OAuth2 flow on first run, token loading on subsequent runs,
    and automatic token refresh.
    
    Args:
        token_path: Path to token.json file
        credentials_path: Path to credentials.json file
        reauth: If True, force fresh OAuth2 authentication
    
    Returns:
        Tuple of (drive_service, gmail_service)
    """
    credentials = None
    
    if not reauth:
        credentials = load_token(token_path)
    
    if credentials and credentials.expired and credentials.refresh_token:
        print("Token expired, refreshing...", flush=True)
        try:
            credentials.refresh()
            save_token(credentials, token_path)
            print("Token refreshed successfully.", flush=True)
        except Exception as e:
            print(f"Token refresh failed: {e}", flush=True)
            credentials = None
    
    if not credentials or not credentials.valid:
        credentials = authenticate(token_path, credentials_path)
    
    drive_service = build('drive', 'v3', credentials=credentials)
    gmail_service = build('gmail', 'v1', credentials=credentials)
    
    return drive_service, gmail_service


def get_drive_service(
    token_path: Path,
    credentials_path: Path,
    reauth: bool = False
) -> build:
    """Get authenticated Google Drive service."""
    drive_service, _ = get_google_services(token_path, credentials_path, reauth)
    return drive_service


def get_gmail_service(
    token_path: Path,
    credentials_path: Path,
    reauth: bool = False
) -> build:
    """Get authenticated Gmail service."""
    _, gmail_service = get_google_services(token_path, credentials_path, reauth)
    return gmail_service
