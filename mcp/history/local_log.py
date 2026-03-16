import json
from pathlib import Path
from typing import Optional, Any


def _get_history_path() -> Path:
    """Get path to history.json file."""
    from config import get_config
    config = get_config()
    return config['history_path']


def append_record(record_dict: dict[str, Any]) -> None:
    """
    Append a record to the local history file.
    
    Args:
        record_dict: Record to append (audit result or email log)
    """
    history_path = _get_history_path()
    
    history_path.parent.mkdir(parents=True, exist_ok=True)
    
    if history_path.exists():
        with open(history_path, 'r') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    else:
        history = []
    
    history.append(record_dict)
    
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)


def get_records(
    limit: int = 20,
    program: Optional[str] = None,
    audit_level: Optional[int] = None,
    eligible_only: bool = False,
    since: Optional[str] = None
) -> list[dict[str, Any]]:
    """
    Get audit history records with optional filters.
    
    Args:
        limit: Maximum number of records to return
        program: Filter by program (BSCSE, BSEEE, LLB)
        audit_level: Filter by audit level (1, 2, 3)
        eligible_only: If True, return only eligible records
        since: ISO date string to filter records after
    
    Returns:
        List of audit record dicts
    """
    history_path = _get_history_path()
    
    if not history_path.exists():
        return []
    
    try:
        with open(history_path, 'r') as f:
            history = json.load(f)
    except (json.JSONDecodeError, IOError):
        return []
    
    filtered = []
    for record in history:
        if record.get('type') != 'audit':
            continue
        
        if program and record.get('program', '').upper() != program.upper():
            continue
        
        if audit_level is not None and record.get('audit_level') != audit_level:
            continue
        
        if eligible_only and not record.get('eligible', False):
            continue
        
        if since:
            created_at = record.get('created_at', '')
            if created_at < since:
                continue
        
        filtered.append(record)
    
    filtered.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return filtered[:limit]
