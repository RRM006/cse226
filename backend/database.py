from supabase import Client, create_client

from config import settings

url: str = settings.SUPABASE_URL
key: str = settings.SUPABASE_SERVICE_KEY
supabase: Client = create_client(url, key)


async def get_profile(user_id: str) -> dict:
    response = (
        supabase.table("profiles").select("*").eq("id", user_id).execute()
    )
    return response.data[0] if response.data else None


async def create_scan(scan_data: dict) -> dict:
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
