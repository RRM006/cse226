from typing import Any, Optional

from supabase import Client, create_client

from config import settings

url: str = settings.SUPABASE_URL
key: str = settings.SUPABASE_SERVICE_KEY
supabase: Client = create_client(url, key)


async def get_profile(user_id: str) -> Optional[dict]:
    response = (
        supabase.table("profiles").select("*").eq("id", user_id).execute()
    )
    return response.data[0] if response.data else None


async def create_profile(user_id: str, email: str, role: str = "admin") -> Optional[dict]:
    response = supabase.table("profiles").insert({
        "id": user_id,
        "email": email,
        "role": role
    }).execute()
    return response.data[0] if response.data else None


async def update_profile_role(user_id: str, role: str) -> Optional[dict]:
    response = supabase.table("profiles").update({"role": role}).eq("id", user_id).execute()
    return response.data[0] if response.data else None


async def create_scan(scan_data: dict) -> Optional[dict]:
    response = supabase.table("scans").insert(scan_data).execute()
    return response.data[0] if response.data else None


async def get_scans_by_user(user_id: str) -> list:
    response = (
        supabase.table("scans").select("*").eq("user_id", user_id).execute()
    )
    return response.data


async def get_all_scans() -> list:
    response = supabase.table("scans").select("*").execute()
    return response.data


async def delete_scan(scan_id: str, user_id: str) -> bool:
    response = (
        supabase.table("scans")
        .delete()
        .eq("id", scan_id)
        .eq("user_id", user_id)
        .execute()
    )
    return len(response.data) > 0


# =====================
# STUDENT DB FUNCTIONS
# =====================

async def get_student_by_student_id(student_id: str) -> Optional[dict]:
    response = (
        supabase.table("students").select("*").eq("student_id", student_id).execute()
    )
    return response.data[0] if response.data else None


async def create_student(
    student_id: str,
    password_hash: str,
    name: str = "",
    email: str = "",
) -> Optional[dict]:
    response = supabase.table("students").insert({
        "student_id": student_id,
        "password_hash": password_hash,
        "name": name,
        "email": email,
        "is_first_login": True,
    }).execute()
    return response.data[0] if response.data else None


async def update_student_password(student_id: str, password_hash: str, is_first_login: bool = False) -> Optional[dict]:
    response = (
        supabase.table("students")
        .update({
            "password_hash": password_hash,
            "is_first_login": is_first_login,
            "updated_at": "now()",
        })
        .eq("student_id", student_id)
        .execute()
    )
    return response.data[0] if response.data else None


async def update_student(student_id: str, data: dict) -> Optional[dict]:
    data["updated_at"] = "now()"
    response = (
        supabase.table("students")
        .update(data)
        .eq("student_id", student_id)
        .execute()
    )
    return response.data[0] if response.data else None


async def delete_student(student_id: str) -> bool:
    response = (
        supabase.table("students")
        .delete()
        .eq("student_id", student_id)
        .execute()
    )
    return len(response.data) > 0


async def get_all_students() -> list:
    response = supabase.table("students").select("*").execute()
    return response.data


# =====================
# AUDIT RESULT DB FUNCTIONS
# =====================

async def create_audit_result(
    student_id: str,
    program: str,
    audit_level: int,
    result_json: dict,
    result_text: str,
    eligible: bool,
    scan_id: str = None,
) -> Optional[dict]:
    data = {
        "student_id": student_id,
        "program": program,
        "audit_level": audit_level,
        "result_json": result_json,
        "result_text": result_text,
        "eligible": eligible,
    }
    if scan_id:
        data["scan_id"] = scan_id
    response = supabase.table("audit_results").insert(data).execute()
    return response.data[0] if response.data else None


async def get_audit_results_by_student(student_id: str) -> list:
    response = (
        supabase.table("audit_results")
        .select("*")
        .eq("student_id", student_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


async def get_audit_result_by_id(result_id: str) -> Optional[dict]:
    response = (
        supabase.table("audit_results")
        .select("*")
        .eq("id", result_id)
        .execute()
    )
    return response.data[0] if response.data else None


async def get_all_audit_results() -> list:
    response = (
        supabase.table("audit_results")
        .select("*, students!inner(name, student_id)")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


# =====================
# REQUEST DB FUNCTIONS
# =====================

async def create_request(
    student_id: str,
    message: str,
    audit_result_id: str = None,
) -> Optional[dict]:
    data = {
        "student_id": student_id,
        "message": message,
        "status": "pending",
    }
    if audit_result_id:
        data["audit_result_id"] = audit_result_id
    response = supabase.table("requests").insert(data).execute()
    return response.data[0] if response.data else None


async def get_requests_by_student(student_id: str) -> list:
    response = (
        supabase.table("requests")
        .select("*")
        .eq("student_id", student_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


async def get_request_by_id(request_id: str) -> Optional[dict]:
    response = (
        supabase.table("requests")
        .select("*")
        .eq("id", request_id)
        .execute()
    )
    return response.data[0] if response.data else None


async def update_request(request_id: str, data: dict) -> Optional[dict]:
    data["updated_at"] = "now()"
    response = (
        supabase.table("requests")
        .update(data)
        .eq("id", request_id)
        .execute()
    )
    return response.data[0] if response.data else None


async def get_all_requests() -> list:
    response = (
        supabase.table("requests")
        .select("*, students!inner(name, student_id)")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data
