from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from auth import (
    CurrentStudent,
    CurrentUser,
    get_current_student,
    get_current_user,
    require_admin,
)
from database import supabase, get_scans_by_student_id
from services.scan_service import delete_scan, get_scan_by_id, get_user_history

router = APIRouter(prefix="/api/v1/history", tags=["history"])


@router.get("")
async def get_history(
    current_user: CurrentUser = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    # Admin sees ALL scans, regular users see only their own
    if current_user.role == "admin":
        response = (
            supabase.table("scans")
            .select(
                "id, user_id, student_id, program, input_type, audit_level, result_json, result_text, created_at"
            )
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        total_response = supabase.table("scans").select("id", count="exact").execute()
    else:
        response = (
            supabase.table("scans")
            .select(
                "id, user_id, student_id, program, input_type, audit_level, result_json, result_text, created_at"
            )
            .eq("user_id", current_user.id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        total_response = (
            supabase.table("scans")
            .select("id", count="exact")
            .eq("user_id", current_user.id)
            .execute()
        )
    total = total_response.count or 0

    scans = []
    for scan in response.data:
        result_json = scan.get("result_json", {})
        input_type = scan.get("input_type", "")
        if input_type == "ocr_image":
            input_type = "OCR"

        summary = {
            "total_credits": result_json.get("total_credits"),
            "cgpa": result_json.get("cgpa"),
            "standing": result_json.get("standing"),
            "eligible": result_json.get("eligible"),
            "missing_courses": result_json.get("missing_courses"),
        }
        scans.append(
            {
                "scan_id": scan["id"],
                "input_type": input_type,
                "program": scan["program"],
                "audit_level": scan["audit_level"],
                "summary": summary,
                "created_at": scan["created_at"],
            }
        )

    return {"total": total, "scans": scans}


@router.get("/{scan_id}")
async def get_scan(
    scan_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    scan = await get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan["user_id"] != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this scan")

    result_json = scan.get("result_json", {})
    input_type = scan.get("input_type", "")
    if input_type == "ocr_image":
        input_type = "OCR"

    summary = {
        "total_credits": result_json.get("total_credits"),
        "cgpa": result_json.get("cgpa"),
        "standing": result_json.get("standing"),
        "eligible": result_json.get("eligible"),
        "missing_courses": result_json.get("missing_courses"),
    }

    return {
        "scan_id": scan["id"],
        "student_id": scan.get("student_id"),
        "program": scan["program"],
        "input_type": input_type,
        "audit_level": scan["audit_level"],
        "summary": summary,
        "result_text": scan.get("result_text"),
        "result_json": result_json,
        "created_at": scan["created_at"],
    }


@router.delete("/{scan_id}")
async def delete_scan_route(
    scan_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    scan = await get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan["user_id"] != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this scan"
        )

    success = await delete_scan(scan_id, current_user.id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete scan")

    return {"message": "Scan deleted successfully"}


@router.get("/user/{user_id}")
async def get_user_history_admin(
    user_id: str,
    current_user: CurrentUser = Depends(require_admin),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    response = (
        supabase.table("scans")
        .select(
            "id, user_id, student_id, program, input_type, audit_level, result_json, created_at"
        )
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )

    total_response = (
        supabase.table("scans")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .execute()
    )
    total = total_response.count or 0

    scans = []
    for scan in response.data:
        result_json = scan.get("result_json", {})
        input_type = scan.get("input_type", "")
        if input_type == "ocr_image":
            input_type = "OCR"

        summary = {
            "total_credits": result_json.get("total_credits"),
            "cgpa": result_json.get("cgpa"),
            "standing": result_json.get("standing"),
            "eligible": result_json.get("eligible"),
        }
        scans.append(
            {
                "scan_id": scan["id"],
                "input_type": input_type,
                "program": scan["program"],
                "audit_level": scan["audit_level"],
                "summary": summary,
                "created_at": scan["created_at"],
            }
        )

    return {"total": total, "scans": scans}


@router.get("/student/scans")
async def get_student_scans(
    student: CurrentStudent = Depends(get_current_student),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Student history endpoint - allows students to view their own scan history."""
    scans = await get_scans_by_student_id(student.student_id)
    total = len(scans)
    page = scans[offset : offset + limit]

    items = []
    for s in page:
        result_json = s.get("result_json", {})
        input_type = s.get("input_type", "")
        if input_type == "ocr_image":
            input_type = "OCR"

        summary = {
            "total_credits": result_json.get("total_credits"),
            "cgpa": result_json.get("cgpa"),
            "standing": result_json.get("standing"),
            "eligible": result_json.get("eligible"),
            "missing_courses": result_json.get("missing_courses", []),
        }
        items.append(
            {
                "scan_id": s["id"],
                "student_id": s.get("student_id"),
                "input_type": input_type,
                "program": s.get("program"),
                "audit_level": s.get("audit_level"),
                "summary": summary,
                "created_at": s.get("created_at"),
            }
        )

    return {"total": total, "scans": items}


@router.get("/student/scans/{scan_id}")
async def get_student_scan_by_id(
    scan_id: str,
    student: CurrentStudent = Depends(get_current_student),
):
    """Get a specific scan by ID for students."""
    scan = await get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan.get("student_id") != student.student_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this scan")

    result_json = scan.get("result_json", {})
    input_type = scan.get("input_type", "")
    if input_type == "ocr_image":
        input_type = "OCR"

    summary = {
        "total_credits": result_json.get("total_credits"),
        "cgpa": result_json.get("cgpa"),
        "standing": result_json.get("standing"),
        "eligible": result_json.get("eligible"),
        "missing_courses": result_json.get("missing_courses"),
    }

    return {
        "scan_id": scan["id"],
        "student_id": scan.get("student_id"),
        "input_type": input_type,
        "program": scan["program"],
        "audit_level": scan["audit_level"],
        "summary": summary,
        "result_text": scan.get("result_text"),
        "result_json": result_json,
        "created_at": scan["created_at"],
    }


@router.get("/all")
async def get_all_scans_admin(
    current_user: CurrentUser = Depends(require_admin),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Admin endpoint to view ALL scans across all users."""
    response = (
        supabase.table("scans")
        .select(
            "id, user_id, student_id, program, input_type, audit_level, result_json, created_at"
        )
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )

    total_response = supabase.table("scans").select("id", count="exact").execute()
    total = total_response.count or 0

    scans = []
    for scan in response.data:
        result_json = scan.get("result_json", {})
        input_type = scan.get("input_type", "")
        if input_type == "ocr_image":
            input_type = "OCR"

        summary = {
            "total_credits": result_json.get("total_credits"),
            "cgpa": result_json.get("cgpa"),
            "standing": result_json.get("standing"),
            "eligible": result_json.get("eligible"),
        }
        scans.append(
            {
                "scan_id": scan["id"],
                "user_id": scan.get("user_id"),
                "student_id": scan.get("student_id"),
                "input_type": input_type,
                "program": scan["program"],
                "audit_level": scan["audit_level"],
                "summary": summary,
                "created_at": scan["created_at"],
            }
        )

    return {"total": total, "scans": scans}
