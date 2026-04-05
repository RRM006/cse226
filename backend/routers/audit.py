import os
import re
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from auth import CurrentUser, get_current_user, hash_password
from services.audit_service import run_audit
from services.ocr_service import process_ocr, process_pdf_first_page
from services.scan_service import save_scan
from database import (
    create_audit_result,
    create_student,
    get_student_by_student_id,
)

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


class SaveScanRequest(BaseModel):
    student_id: Optional[str] = ""
    program: str
    input_type: str
    raw_input: str = ""
    waivers: List[str] = []
    audit_level: int
    result_json: dict
    result_text: str


@router.post("/save")
async def save_audit_result(
    request: SaveScanRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    result = {
        "result_json": request.result_json,
        "result_text": request.result_text
    }
    
    scan = await save_scan(
        current_user.id, 
        result, 
        request.input_type, 
        request.raw_input
    )
    
    if not scan:
        raise HTTPException(status_code=500, detail="Failed to save scan to database")
    
    return {
        "scan_id": scan["id"],
        "message": "Scan saved successfully"
    }


@router.post("/csv")
async def audit_csv(
    file: UploadFile = File(...),
    program: str = Form(...),
    audit_level: int = Form(...),
    waivers: str = Form(""),
    knowledge_file: str = Form(None),
    current_user: CurrentUser = Depends(get_current_user)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
        
    csv_bytes = await file.read()
    csv_text = csv_bytes.decode('utf-8')
    
    waivers_list = [w.strip() for w in waivers.split(',')] if waivers else []
    
    # Find knowledge file path
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    if not knowledge_file:
        kf_name = f"program_knowledge_{program}.md"
    else:
        kf_name = knowledge_file
        
    kf_path = os.path.join(base_dir, "program_knowledge", kf_name)
    
    if audit_level == 3 and not os.path.isfile(kf_path):
        raise HTTPException(status_code=422, detail=f"Knowledge file not found for program {program}")
        
    try:
        result = await run_audit(
            csv_text=csv_text,
            program=program,
            audit_level=audit_level,
            waivers=waivers_list,
            knowledge_file=kf_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # Save to db
    scan = await save_scan(current_user.id, result, "csv", csv_text)
    
    # Response match PRD format
    if not scan:
        raise HTTPException(status_code=500, detail="Failed to save scan to database")
        
    result_json = scan["result_json"]
    summary = {
        "total_credits": result_json.get("total_credits"),
        "cgpa": result_json.get("cgpa"),
        "standing": result_json.get("standing"),
        "eligible": result_json.get("eligible"),
        "missing_courses": len(result_json.get("missing_courses", []))
    }
    
    return {
        "scan_id": scan["id"],
        "student_id": scan["student_id"],
        "program": scan["program"],
        "audit_level": scan["audit_level"],
        "summary": summary,
        "result_text": scan["result_text"],
        "result_json": scan["result_json"],
        "created_at": scan["created_at"]
    }


@router.post("/ocr")
async def audit_ocr(
    file: UploadFile = File(...),
    program: str = Form(...),
    audit_level: int = Form(...),
    waivers: str = Form(""),
    current_user: CurrentUser = Depends(get_current_user)
):
    filename = file.filename.lower()
    
    if not filename.endswith(('.png', '.jpg', '.jpeg', '.pdf')):
        raise HTTPException(status_code=400, detail="File must be PNG, JPG, or PDF")
    
    image_bytes = await file.read()
    
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")
    
    if filename.endswith('.pdf'):
        try:
            image_bytes = await process_pdf_first_page(image_bytes)
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))
    
    try:
        ocr_result = await process_ocr(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
    
    if ocr_result.confidence_avg < 0.60:
        raise HTTPException(
            status_code=422,
            detail=f"OCR confidence too low ({ocr_result.confidence_avg:.2f}). Please upload a clearer image."
        )
    
    csv_text = ocr_result.csv_text
    
    if not csv_text.strip():
        raise HTTPException(status_code=422, detail="No valid course data could be extracted from the image")
    
    waivers_list = [w.strip() for w in waivers.split(',')] if waivers else []
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    kf_name = f"program_knowledge_{program}.md"
    kf_path = os.path.join(base_dir, "program_knowledge", kf_name)
    
    if audit_level == 3 and not os.path.isfile(kf_path):
        raise HTTPException(status_code=422, detail=f"Knowledge file not found for program {program}")
    
    try:
        result = await run_audit(
            csv_text=csv_text,
            program=program,
            audit_level=audit_level,
            waivers=waivers_list,
            knowledge_file=kf_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    raw_input = f"[OCR IMAGE] {filename}\n{ocr_result.csv_text[:500]}..."
    scan = await save_scan(current_user.id, result, "ocr_image", raw_input)
    
    if not scan:
        raise HTTPException(status_code=500, detail="Failed to save scan to database")
    
    result_json = scan["result_json"]
    summary = {
        "total_credits": result_json.get("total_credits"),
        "cgpa": result_json.get("cgpa"),
        "standing": result_json.get("standing"),
        "eligible": result_json.get("eligible"),
        "missing_courses": len(result_json.get("missing_courses", []))
    }
    
    return {
        "scan_id": scan["id"],
        "student_id": scan["student_id"],
        "program": scan["program"],
        "audit_level": scan["audit_level"],
        "summary": summary,
        "result_text": scan["result_text"],
        "result_json": scan["result_json"],
        "created_at": scan["created_at"],
        "ocr_confidence": ocr_result.confidence_avg,
        "ocr_extracted_rows": ocr_result.extracted_row_count,
        "ocr_warnings": ocr_result.warnings
    }


class SaveWithStudentIdRequest(BaseModel):
    student_id: str
    program: str
    input_type: str
    raw_input: str = ""
    waivers: List[str] = []
    audit_level: int
    result_json: dict
    result_text: str


@router.post("/save-with-student-id")
async def save_audit_with_student_id(
    request: SaveWithStudentIdRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Save audit result with confirmed student ID. Auto-creates student if not exists."""
    STUDENT_ID_PATTERN = re.compile(r"^2\d{9}$")

    student_id = request.student_id.strip()
    if not student_id:
        raise HTTPException(status_code=400, detail="Student ID is required")
    if not STUDENT_ID_PATTERN.match(student_id):
        raise HTTPException(status_code=400, detail="Invalid student ID format. Must be 10 digits starting with 2 (e.g., 2211234567)")

    # Auto-create student if not exists
    existing = await get_student_by_student_id(student_id)
    if not existing:
        password_hash = hash_password(student_id)
        created = await create_student(
            student_id=student_id,
            password_hash=password_hash,
            name="",
            email="",
        )
        if not created:
            raise HTTPException(status_code=500, detail="Failed to auto-create student account")

    # Update result_json with confirmed student_id
    result_json = dict(request.result_json)
    result_json["student_id"] = student_id

    # Save scan
    scan = await save_scan(
        current_user.id,
        {"result_json": result_json, "result_text": request.result_text},
        request.input_type,
        request.raw_input,
    )
    if not scan:
        raise HTTPException(status_code=500, detail="Failed to save scan")

    # Also save to audit_results so student can see it
    eligible = result_json.get("eligible", False)
    await create_audit_result(
        student_id=student_id,
        program=request.program,
        audit_level=request.audit_level,
        result_json=result_json,
        result_text=request.result_text,
        eligible=eligible,
        scan_id=scan["id"],
    )

    summary = {
        "total_credits": result_json.get("total_credits"),
        "cgpa": result_json.get("cgpa"),
        "standing": result_json.get("standing"),
        "eligible": eligible,
        "missing_courses": len(result_json.get("missing_courses", [])),
    }

    return {
        "scan_id": scan["id"],
        "student_id": student_id,
        "program": request.program,
        "audit_level": request.audit_level,
        "summary": summary,
        "result_text": request.result_text,
        "result_json": result_json,
        "created_at": scan["created_at"],
    }
