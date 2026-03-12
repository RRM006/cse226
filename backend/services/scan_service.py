from backend.database import create_scan
from backend.database import delete_scan as db_delete_scan
from backend.database import get_all_scans, get_scans_by_user, supabase


async def save_scan(user_id: str, result: dict, input_type: str, raw_input: str) -> dict:
    result_json = result.get("result_json", {})
    scan_data = {
        "user_id": user_id,
        "student_id": result_json.get("student_id"),
        "program": result_json.get("program"),
        "input_type": input_type,
        "raw_input": raw_input,
        "waivers": result_json.get("waivers_applied", []),
        "audit_level": result_json.get("audit_level"),
        "result_json": result_json,
        "result_text": result.get("result_text")
    }
    return await create_scan(scan_data)

async def get_user_history(user_id: str) -> list:
    return await get_scans_by_user(user_id)

async def get_scan_by_id(scan_id: str) -> dict:
    response = supabase.table("scans").select("*").eq("id", scan_id).execute()
    return response.data[0] if response.data else None

async def delete_scan(scan_id: str, user_id: str) -> bool:
    return await db_delete_scan(scan_id, user_id)
