import httpx
from datetime import datetime
from typing import Optional, Any

from config import get_config
from history.local_log import get_records as get_local_records


def get_audit_history(
    limit: int = 20,
    program: Optional[str] = None,
    audit_level: Optional[int] = None,
    eligible_only: bool = False,
    since: Optional[str] = None
) -> list[dict[str, Any]]:
    """
    Get audit history records.
    
    Offline mode: reads from local history.json
    Remote mode: calls FastAPI backend
    
    Args:
        limit: Maximum number of records to return
        program: Filter by program (BSCSE, BSEEE, LLB)
        audit_level: Filter by audit level (1, 2, 3)
        eligible_only: If True, return only eligible records
        since: ISO date string to filter records after
    
    Returns:
        List of {scan_id, student_id, program, audit_level, cgpa, eligible, created_at}
    """
    config = get_config()
    
    if config['remote']:
        return _get_history_remote(
            limit, program, audit_level, eligible_only, since, config
        )
    else:
        return _get_history_local(
            limit, program, audit_level, eligible_only, since
        )


def _get_history_local(
    limit: int,
    program: Optional[str],
    audit_level: Optional[int],
    eligible_only: bool,
    since: Optional[str]
) -> list[dict[str, Any]]:
    """Get history from local JSON file."""
    records = get_local_records(
        limit=limit,
        program=program,
        audit_level=audit_level,
        eligible_only=eligible_only,
        since=since
    )
    
    return [
        {
            'scan_id': r.get('scan_id', r.get('student_id', '')),
            'student_id': r.get('student_id', 'Unknown'),
            'program': r.get('program', 'Unknown'),
            'audit_level': r.get('audit_level', 3),
            'cgpa': r.get('cgpa', 0.0),
            'eligible': r.get('eligible', False),
            'created_at': r.get('created_at', '')
        }
        for r in records
    ]


def _get_history_remote(
    limit: int,
    program: Optional[str],
    audit_level: Optional[int],
    eligible_only: bool,
    since: Optional[str],
    config: dict
) -> list[dict[str, Any]]:
    """Get history from FastAPI backend."""
    api_url = config['api_url']
    api_token_path = config['api_token_path']
    
    api_token = None
    if api_token_path.exists():
        with open(api_token_path, 'r') as f:
            api_token = f.read().strip()
    
    if not api_token:
        return []
    
    headers = {
        'Authorization': f'Bearer {api_token}'
    }
    
    params = {'limit': limit}
    if program:
        params['program'] = program
    if audit_level is not None:
        params['audit_level'] = audit_level
    if eligible_only:
        params['eligible_only'] = 'true'
    if since:
        params['since'] = since
    
    try:
        response = httpx.get(
            f'{api_url}/api/v1/history',
            headers=headers,
            params=params,
            timeout=30.0
        )
        
        if response.status_code == 200:
            records = response.json()
            return [
                {
                    'scan_id': r.get('scan_id', r.get('student_id', '')),
                    'student_id': r.get('student_id', 'Unknown'),
                    'program': r.get('program', 'Unknown'),
                    'audit_level': r.get('audit_level', 3),
                    'cgpa': r.get('cgpa', 0.0),
                    'eligible': r.get('eligible', False),
                    'created_at': r.get('created_at', '')
                }
                for r in records
            ]
        else:
            return []
    
    except Exception:
        return []
