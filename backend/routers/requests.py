from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from auth import CurrentStudent, CurrentUser, get_current_student, get_current_user, require_admin
from database import (
    create_request,
    get_audit_result_by_id,
    get_request_by_id,
    get_requests_by_student,
    get_all_requests,
    update_request,
)

router = APIRouter(prefix="/api/v1", tags=["requests"])


class CreateRequestRequest(BaseModel):
    message: str
    audit_result_id: Optional[str] = None


class UpdateRequestStatus(BaseModel):
    status: str
    admin_notes: Optional[str] = None


# =====================
# STUDENT ENDPOINTS
# =====================


@router.post("/student/requests", status_code=201)
async def student_submit_request(
    request: CreateRequestRequest,
    student: CurrentStudent = Depends(get_current_student),
):
    if len(request.message.strip()) < 10:
        raise HTTPException(
            status_code=400, detail="Message must be at least 10 characters"
        )

    if request.audit_result_id:
        result = await get_audit_result_by_id(request.audit_result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Audit result not found")
        if result["student_id"] != student.student_id:
            raise HTTPException(
                status_code=403, detail="Audit result does not belong to you"
            )

    req = await create_request(
        student_id=student.student_id,
        message=request.message,
        audit_result_id=request.audit_result_id,
    )

    if not req:
        raise HTTPException(status_code=500, detail="Failed to submit request")

    return {
        "message": "Request submitted successfully",
        "request_id": req["id"],
        "status": "pending",
    }


@router.get("/student/requests")
async def student_get_requests(
    student: CurrentStudent = Depends(get_current_student),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    requests = await get_requests_by_student(student.student_id)
    total = len(requests)
    page = requests[offset:offset + limit]

    items = []
    for r in page:
        items.append({
            "id": r["id"],
            "message": r.get("message"),
            "status": r.get("status"),
            "admin_notes": r.get("admin_notes"),
            "created_at": r.get("created_at"),
            "updated_at": r.get("updated_at"),
        })

    return {"total": total, "requests": items}


# =====================
# ADMIN ENDPOINTS
# =====================


@router.get("/requests")
async def admin_get_all_requests(
    admin: CurrentUser = Depends(require_admin),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    requests = await get_all_requests()
    total = len(requests)
    page = requests[offset:offset + limit]

    items = []
    for r in page:
        student_info = r.get("students", {})
        items.append({
            "id": r["id"],
            "student_id": r["student_id"],
            "student_name": student_info.get("name", ""),
            "message": r.get("message"),
            "status": r.get("status"),
            "admin_notes": r.get("admin_notes"),
            "created_at": r.get("created_at"),
            "updated_at": r.get("updated_at"),
        })

    return {"total": total, "requests": items}


@router.get("/requests/{request_id}")
async def admin_get_request(
    request_id: str,
    admin: CurrentUser = Depends(require_admin),
):
    req = await get_request_by_id(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    return {
        "id": req["id"],
        "student_id": req["student_id"],
        "message": req.get("message"),
        "status": req.get("status"),
        "admin_notes": req.get("admin_notes"),
        "audit_result_id": req.get("audit_result_id"),
        "created_at": req.get("created_at"),
        "updated_at": req.get("updated_at"),
    }


@router.patch("/requests/{request_id}")
async def admin_update_request(
    request_id: str,
    body: UpdateRequestStatus,
    admin: CurrentUser = Depends(require_admin),
):
    req = await get_request_by_id(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    valid_statuses = {"pending", "reviewed", "approved", "rejected"}
    if body.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        )

    update_data = {"status": body.status}
    if body.admin_notes is not None:
        update_data["admin_notes"] = body.admin_notes

    updated = await update_request(request_id, update_data)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update request")

    return {
        "message": "Request updated",
        "request_id": request_id,
        "status": body.status,
    }
