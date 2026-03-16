import base64
import time
from pathlib import Path
from typing import Any

from auth.google_oauth import get_drive_service
from config import get_config


MAX_RETRIES = 3
RETRY_DELAY = 2


def with_retry(func):
    """Decorator to retry Google API calls on rate limit errors."""
    def wrapper(*args, **kwargs):
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_str = str(e).lower()
                if 'rate limit' in error_str or '429' in error_str:
                    last_error = e
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                    continue
                raise
        if last_error:
            raise last_error
    return wrapper


@with_retry
def list_drive_folder(folder_name: str, file_types: list[str] | None = None) -> list[dict[str, Any]] | str:
    """
    List all files in a Google Drive folder.
    
    Args:
        folder_name: Name of the Drive folder to search
        file_types: Optional list of file types to filter (e.g. ["csv", "png", "pdf"])
    
    Returns:
        List of dicts with keys: file_id, file_name, mime_type, modified_date, size_bytes
        Returns error message string if folder not found
    """
    config = get_config()
    drive_service = get_drive_service(
        config['token_path'],
        config['credentials_path'],
        config['reauth']
    )
    
    folder_query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    folder_result = drive_service.files().list(q=folder_query, spaces='drive', fields='files(id, name)').execute()
    folders = folder_result.get('files', [])
    
    if not folders:
        return f"Folder '{folder_name}' not found in Drive"
    
    folder_id = folders[0]['id']
    
    query = f"'{folder_id}' in parents and trashed = false"
    if file_types and len(file_types) > 0:
        type_queries = []
        for ft in file_types:
            if ft == 'csv':
                type_queries.append("mimeType = 'text/csv'")
            elif ft == 'pdf':
                type_queries.append("mimeType = 'application/pdf'")
            elif ft in ['png', 'jpg', 'jpeg', 'gif']:
                type_queries.append(f"mimeType contains 'image/{ft}'")
        if type_queries:
            query += f" and ({' or '.join(type_queries)})"
    
    result = drive_service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType, modifiedTime, size)',
        orderBy='name'
    ).execute()
    
    files = result.get('files', [])
    return [
        {
            'file_id': f['id'],
            'file_name': f['name'],
            'mime_type': f['mimeType'],
            'modified_date': f.get('modifiedTime', ''),
            'size_bytes': int(f.get('size', 0))
        }
        for f in files
    ]


@with_retry
def get_transcript(file_id: str, file_name: str | None = None) -> dict[str, Any] | str:
    """
    Download a transcript file from Google Drive.
    
    Args:
        file_id: Drive file ID
        file_name: Optional human-readable name for logging
    
    Returns:
        Dict with keys: file_id, file_name, content_type ("csv" or "image"), content
        Returns error message string on failure
    """
    config = get_config()
    drive_service = get_drive_service(
        config['token_path'],
        config['credentials_path'],
        config['reauth']
    )
    
    try:
        file_metadata = drive_service.files().get(fileId=file_id, fields='name, mimeType, size').execute()
    except Exception as e:
        return f"File not found: {str(e)}"
    
    name = file_name or file_metadata.get('name', file_id)
    mime_type = file_metadata.get('mimeType', '')
    
    is_csv = mime_type == 'text/csv'
    is_image = mime_type.startswith('image/') or mime_type == 'application/pdf'
    
    if is_csv:
        content = drive_service.files().get_media(fileId=file_id).execute().decode('utf-8')
        return {
            'file_id': file_id,
            'file_name': name,
            'content_type': 'csv',
            'content': content
        }
    elif is_image:
        content_bytes = drive_service.files().get_media(fileId=file_id).execute()
        content_b64 = base64.b64encode(content_bytes).decode('utf-8')
        return {
            'file_id': file_id,
            'file_name': name,
            'content_type': 'image',
            'content': content_b64
        }
    else:
        return f"Unsupported file type: {mime_type}. Only CSV, PDF, and images are supported."


@with_retry
def search_drive(query: str, folder_name: str | None = None) -> list[dict[str, Any]]:
    """
    Search for files in Google Drive by name or content.
    
    Args:
        query: Search query (student ID, name, or filename keyword)
        folder_name: Optional folder name to limit search to
    
    Returns:
        List of dicts with keys: file_id, file_name, mime_type, modified_date, size_bytes
        Returns empty list if nothing found
    """
    config = get_config()
    drive_service = get_drive_service(
        config['token_path'],
        config['credentials_path'],
        config['reauth']
    )
    
    folder_id = None
    if folder_name:
        folder_query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        folder_result = drive_service.files().list(q=folder_query, spaces='drive', fields='files(id)').execute()
        folders = folder_result.get('files', [])
        if not folders:
            return []
        folder_id = folders[0]['id']
    
    search_query = f"(name contains '{query}' or fullText contains '{query}') and trashed = false"
    if folder_id:
        search_query += f" and '{folder_id}' in parents"
    
    result = drive_service.files().list(
        q=search_query,
        spaces='drive',
        fields='files(id, name, mimeType, modifiedTime, size)',
        orderBy='modifiedTime desc',
        pageSize=50
    ).execute()
    
    files = result.get('files', [])
    return [
        {
            'file_id': f['id'],
            'file_name': f['name'],
            'mime_type': f['mimeType'],
            'modified_date': f.get('modifiedTime', ''),
            'size_bytes': int(f.get('size', 0))
        }
        for f in files
    ]
