import re
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from auth import (
    CurrentStudent,
    CurrentUser,
    create_student_token,
    get_current_student,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)
from database import (
    create_audit_result,
    create_student,
    delete_student,
    get_all_audit_results,
    get_all_students,
    get_audit_results_by_student,
    get_student_by_student_id,
    update_student,
    update_student_password,
)

router = APIRouter(prefix="/api/v1", tags=["students"])

STUDENT_ID_PATTERN = re.compile(r"^2\d{9}$")


class StudentLoginRequest(BaseModel):
    student_id: str
    password: str


class CreateStudentRequest(BaseModel):
    student_id: str
    name: str = ""
    email: str = ""


class UpdateStudentRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class AdminResetPasswordRequest(BaseModel):
    new_password: str


class StudentLoginResponse(BaseModel):
    access_token: str
    token_type: str
    student_id: str
    name: str
    is_first_login: bool


@router.post("/student/login", response_model=StudentLoginResponse)
async def student_login(request: StudentLoginRequest):
    if not STUDENT_ID_PATTERN.match(request.student_id):
        raise HTTPException(
            status_code=400, detail="Invalid student ID format. Must be 10 digits starting with 2."
        )

    student = await get_student_by_student_id(request.student_id)
    if not student:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(request.password, student["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_student_token(student["student_id"], student["id"])

    return StudentLoginResponse(
        access_token=token,
        token_type="bearer",
        student_id=student["student_id"],
        name=student.get("name", ""),
        is_first_login=student.get("is_first_login", False),
    )


@router.post("/student/change-password")
async def change_password(
    request: ChangePasswordRequest,
    student: CurrentStudent = Depends(get_current_student),
):
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=400, detail="Password must be at least 6 characters"
        )

    db_student = await get_student_by_student_id(student.student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    if not verify_password(request.current_password, db_student["password_hash"]):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    new_hash = hash_password(request.new_password)
    await update_student_password(student.student_id, new_hash, is_first_login=False)

    return {"message": "Password changed successfully"}


@router.get("/student/me")
async def get_student_profile(student: CurrentStudent = Depends(get_current_student)):
    db_student = await get_student_by_student_id(student.student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "id": db_student["id"],
        "student_id": db_student["student_id"],
        "name": db_student.get("name", ""),
        "email": db_student.get("email", ""),
        "is_first_login": db_student.get("is_first_login", False),
        "created_at": db_student.get("created_at"),
    }


# =====================
# ADMIN ENDPOINTS
# =====================


@router.post("/students", status_code=201)
async def create_student_account(
    request: CreateStudentRequest,
    admin: CurrentUser = Depends(require_admin),
):
    if not STUDENT_ID_PATTERN.match(request.student_id):
        raise HTTPException(
            status_code=400, detail="Invalid student ID format. Must be 10 digits starting with 2."
        )

    existing = await get_student_by_student_id(request.student_id)
    if existing:
        raise HTTPException(status_code=409, detail="Student ID already exists")

    # Default password = student_id
    password_hash = hash_password(request.student_id)
    student = await create_student(
        student_id=request.student_id,
        password_hash=password_hash,
        name=request.name,
        email=request.email,
    )

    if not student:
        raise HTTPException(status_code=500, detail="Failed to create student account")

    return {
        "message": "Student account created",
        "student_id": student["student_id"],
        "default_password": request.student_id,
    }


@router.get("/students")
async def list_students(
    admin: CurrentUser = Depends(require_admin),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    students = await get_all_students()
    total = len(students)
    page = students[offset:offset + limit]

    result = []
    for s in page:
        result.append({
            "id": s["id"],
            "student_id": s["student_id"],
            "name": s.get("name", ""),
            "email": s.get("email", ""),
            "is_first_login": s.get("is_first_login", False),
            "created_at": s.get("created_at"),
        })

    return {"total": total, "students": result}


@router.get("/students/{student_id}")
async def get_student_detail(
    student_id: str,
    admin: CurrentUser = Depends(require_admin),
):
    student = await get_student_by_student_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    audit_results = await get_audit_results_by_student(student_id)

    return {
        "id": student["id"],
        "student_id": student["student_id"],
        "name": student.get("name", ""),
        "email": student.get("email", ""),
        "is_first_login": student.get("is_first_login", False),
        "created_at": student.get("created_at"),
        "audit_results_count": len(audit_results),
    }


@router.patch("/students/{student_id}")
async def update_student_account(
    student_id: str,
    request: UpdateStudentRequest,
    admin: CurrentUser = Depends(require_admin),
):
    student = await get_student_by_student_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.email is not None:
        update_data["email"] = request.email

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated = await update_student(student_id, update_data)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update student")

    return {"message": "Student updated", "student_id": student_id}


@router.patch("/students/{student_id}/reset-password")
async def admin_reset_password(
    student_id: str,
    request: AdminResetPasswordRequest,
    admin: CurrentUser = Depends(require_admin),
):
    student = await get_student_by_student_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=400, detail="Password must be at least 6 characters"
        )

    new_hash = hash_password(request.new_password)
    await update_student_password(student_id, new_hash, is_first_login=True)

    return {"message": "Password reset successfully"}


@router.delete("/students/{student_id}")
async def delete_student_account(
    student_id: str,
    admin: CurrentUser = Depends(require_admin),
):
    student = await get_student_by_student_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    success = await delete_student(student_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete student")

    return {"message": "Student deleted", "student_id": student_id}
