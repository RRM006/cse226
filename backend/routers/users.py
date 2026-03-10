from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.auth import require_admin, CurrentUser
from backend.database import supabase

router = APIRouter(prefix="/api/v1/users", tags=["users"])


class RoleUpdate(BaseModel):
    role: str


@router.get("")
async def get_all_users(
    current_user: CurrentUser = Depends(require_admin),
):
    profiles_response = supabase.table("profiles").select("*").execute()
    profiles = profiles_response.data

    users = []
    for profile in profiles:
        scans_response = supabase.table("scans").select("id", count="exact").eq("user_id", profile["id"]).execute()
        scan_count = scans_response.count or 0

        users.append({
            "id": profile["id"],
            "email": profile.get("email"),
            "full_name": profile.get("full_name"),
            "role": profile.get("role", "student"),
            "created_at": profile.get("created_at"),
            "scan_count": scan_count,
        })

    return {"total": len(users), "users": users}


@router.patch("/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_update: RoleUpdate,
    current_user: CurrentUser = Depends(require_admin),
):
    if role_update.role not in ["student", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'student' or 'admin'")

    existing = supabase.table("profiles").select("*").eq("id", user_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="User not found")

    response = supabase.table("profiles").update({"role": role_update.role}).eq("id", user_id).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to update role")

    return {
        "message": "Role updated successfully",
        "user_id": user_id,
        "new_role": role_update.role,
    }
