"""
Local offline history for CLI audits.
Stores audit records to ~/.nsu_audit/offline_history.json
so offline-mode audits appear in the History view.
"""

import json
from datetime import datetime
from pathlib import Path

HISTORY_DIR = Path.home() / ".nsu_audit"
HISTORY_FILE = HISTORY_DIR / "offline_history.json"


def _ensure_dir():
    HISTORY_DIR.mkdir(exist_ok=True)


def _load_records() -> list:
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def _save_records(records: list):
    _ensure_dir()
    with open(HISTORY_FILE, "w") as f:
        json.dump(records, f, indent=2)


def append_offline_record(result: dict, input_type: str = "csv"):
    """Append an offline audit record to local history."""
    records = _load_records()
    result_json = result.get("result_json", result)

    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "student_id": result_json.get("student_id", ""),
        "program": result_json.get("program", ""),
        "audit_level": result_json.get("audit_level", 0),
        "total_credits": result_json.get("total_credits"),
        "cgpa": result_json.get("cgpa"),
        "eligible": result_json.get("eligible"),
        "input_type": input_type,
        "source": "local",
    }

    records.insert(0, record)
    # Keep max 200 local records
    records = records[:200]
    _save_records(records)
    return record


def get_offline_records(limit: int = 100, student_id: str = "") -> list:
    """Return local offline records sorted newest-first. Optionally filter by student_id."""
    records = _load_records()
    if student_id:
        records = [r for r in records if r.get("student_id", "") == student_id]
    records.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
    return records[:limit]


def get_offline_student_ids() -> list:
    """Return unique student IDs found in offline history."""
    records = _load_records()
    ids = set()
    for r in records:
        sid = r.get("student_id", "")
        if sid:
            ids.add(sid)
    return sorted(ids)


def clear_offline_history():
    """Remove the offline history file."""
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
