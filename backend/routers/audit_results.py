from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from auth import CurrentStudent, CurrentUser, get_current_user, get_current_student, require_admin
from database import (
    create_audit_result,
    get_audit_result_by_id,
    get_audit_results_by_student,
    get_all_audit_results,
    get_student_by_student_id,
)

router = APIRouter(prefix="/api/v1", tags=["audit-results"])


class CreateAuditResultRequest(BaseModel):
    student_id: str
    program: str
    audit_level: int
    result_json: dict
    result_text: str
    eligible: bool
    scan_id: Optional[str] = None


# =====================
# STUDENT ENDPOINTS
# =====================


@router.get("/student/audit-results")
async def student_get_audit_results(
    student: CurrentStudent = Depends(get_current_student),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    results = await get_audit_results_by_student(student.student_id)
    total = len(results)
    page = results[offset:offset + limit]

    items = []
    for r in page:
        items.append({
            "id": r["id"],
            "student_id": r["student_id"],
            "program": r.get("program"),
            "audit_level": r.get("audit_level"),
            "eligible": r.get("eligible"),
            "created_at": r.get("created_at"),
        })

    return {"total": total, "results": items}


@router.get("/student/audit-results/{result_id}")
async def student_get_audit_result(
    result_id: str,
    student: CurrentStudent = Depends(get_current_student),
):
    result = await get_audit_result_by_id(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Audit result not found")

    if result["student_id"] != student.student_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this result")

    return {
        "id": result["id"],
        "student_id": result["student_id"],
        "program": result.get("program"),
        "audit_level": result.get("audit_level"),
        "result_json": result.get("result_json"),
        "result_text": result.get("result_text"),
        "eligible": result.get("eligible"),
        "created_at": result.get("created_at"),
    }


# =====================
# ADMIN ENDPOINTS
# =====================


@router.post("/audit-results", status_code=201)
async def create_audit_result_endpoint(
    request: CreateAuditResultRequest,
    admin: CurrentUser = Depends(require_admin),
):
    student = await get_student_by_student_id(request.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    result = await create_audit_result(
        student_id=request.student_id,
        program=request.program,
        audit_level=request.audit_level,
        result_json=request.result_json,
        result_text=request.result_text,
        eligible=request.eligible,
        scan_id=request.scan_id,
    )

    if not result:
        raise HTTPException(status_code=500, detail="Failed to create audit result")

    return {
        "message": "Audit result created",
        "id": result["id"],
        "student_id": result["student_id"],
        "eligible": result["eligible"],
    }


@router.get("/audit-results")
async def admin_get_all_audit_results(
    admin: CurrentUser = Depends(require_admin),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    results = await get_all_audit_results()
    total = len(results)
    page = results[offset:offset + limit]

    items = []
    for r in page:
        student_info = r.get("students", {})
        items.append({
            "id": r["id"],
            "student_id": r["student_id"],
            "student_name": student_info.get("name", ""),
            "program": r.get("program"),
            "audit_level": r.get("audit_level"),
            "eligible": r.get("eligible"),
            "created_at": r.get("created_at"),
        })

    return {"total": total, "results": items}
