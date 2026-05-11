import logging
import os
import re
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from auth import CurrentUser, get_current_user, hash_password
from config import settings
from services.audit_service import run_audit
from services.ocr_service import process_ocr, process_pdf_first_page
from services.scan_service import save_scan
from database import (
    create_audit_result,
    create_student,
    get_student_by_student_id,
)

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])
logger = logging.getLogger(__name__)


class SaveScanRequest(BaseModel):
    student_id: Optional[str] = ""
    program: str
    input_type: str
    raw_input: str = ""
    waivers: List[str] = []
    audit_level: int
    result_json: dict
    result_text: str


def _safe_get(d: Optional[dict], *keys, default: Any = None) -> Any:
    """Safely navigate nested dicts without crashing on None."""
    for k in keys:
        if d is None:
            return default
        d = d.get(k) if isinstance(d, dict) else None
    return d if d is not None else default


@router.post("/save")
async def save_audit_result(
    request: SaveScanRequest, current_user: CurrentUser = Depends(get_current_user)
):
    if not request.result_json:
        raise HTTPException(status_code=400, detail="result_json is required")

    result = {"result_json": request.result_json, "result_text": request.result_text}
    try:
        scan = await save_scan(
            current_user.id, result, request.input_type, request.raw_input
        )
    except Exception as e:
        logger.error(
            f"save_audit_result: save_scan failed for user {current_user.id}: {e}"
        )
        raise HTTPException(status_code=500, detail=f"Failed to save scan: {e}")

    if not scan:
        raise HTTPException(status_code=500, detail="Failed to save scan to database")

    return {"scan_id": scan["id"], "message": "Scan saved successfully"}


@router.post("/csv")
async def audit_csv(
    file: UploadFile = File(...),
    program: str = Form(...),
    audit_level: str = Form(...),
    waivers: str = Form(""),
    knowledge_file: str = Form(None),
    current_user: CurrentUser = Depends(get_current_user),
):
    logger.info(
        f"audit_csv: user={current_user.id}, program={program}, level={audit_level}"
    )

    try:
        audit_level_int = int(audit_level)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=422, detail="audit_level must be a valid number (1, 2, or 3)"
        )

    filename = (file.filename or "").lower()
    if not filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    csv_bytes = await file.read()
    csv_text = csv_bytes.decode("utf-8")

    waivers_list = [w.strip() for w in waivers.split(",")] if waivers else []

    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    if not knowledge_file:
        kf_name = f"program_knowledge_{program}.md"
    else:
        kf_name = knowledge_file

    kf_path = os.path.join(base_dir, "program_knowledge", kf_name)

    if audit_level_int == 3 and not os.path.isfile(kf_path):
        raise HTTPException(
            status_code=422, detail=f"Knowledge file not found for program {program}"
        )

    try:
        result = await run_audit(
            csv_text=csv_text,
            program=program,
            audit_level=audit_level_int,
            waivers=waivers_list,
            knowledge_file=kf_path,
        )
    except Exception as e:
        logger.error(f"audit_csv: run_audit failed for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    if not result or not result.get("result_json"):
        logger.error(
            f"audit_csv: run_audit returned empty result for user {current_user.id}"
        )
        raise HTTPException(
            status_code=500, detail="Audit engine returned empty result"
        )

    try:
        scan = await save_scan(current_user.id, result, "csv", csv_text)
    except Exception as e:
        logger.error(f"audit_csv: save_scan failed for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save scan: {e}")

    if not scan:
        raise HTTPException(status_code=500, detail="Failed to save scan to database")

    result_json = _safe_get(scan, "result_json", default={})
    result_text = _safe_get(scan, "result_text", default="")
    summary = {
        "total_credits": _safe_get(result_json, "total_credits", default=0),
        "cgpa": _safe_get(result_json, "cgpa", default=0.0),
        "standing": _safe_get(result_json, "standing", default="N/A"),
        "eligible": _safe_get(result_json, "eligible", default=False),
        "missing_courses": len(_safe_get(result_json, "missing_courses") or []),
    }

    return {
        "scan_id": _safe_get(scan, "id", default=""),
        "student_id": _safe_get(scan, "student_id", default=""),
        "program": _safe_get(scan, "program", default=""),
        "audit_level": _safe_get(scan, "audit_level", default=audit_level_int),
        "summary": summary,
        "result_text": result_text,
        "result_json": result_json,
        "created_at": _safe_get(scan, "created_at", default=""),
    }


@router.post("/ocr")
async def audit_ocr(
    file: UploadFile = File(...),
    program: str = Form(...),
    audit_level: str = Form(...),
    waivers: str = Form(""),
    current_user: CurrentUser = Depends(get_current_user),
):
    logger.info(
        f"audit_ocr: user={current_user.id}, program={program}, level={audit_level}, file={file.filename}"
    )

    try:
        audit_level_int = int(audit_level)
    except (ValueError, TypeError):
        logger.warning(f"audit_ocr: invalid audit_level={audit_level}")
        raise HTTPException(
            status_code=422, detail="audit_level must be a valid number (1, 2, or 3)"
        )

    filename = (file.filename or "").lower()
    logger.debug(f"audit_ocr: filename={filename}")

    if not filename.endswith((".png", ".jpg", ".jpeg", ".pdf")):
        logger.warning(f"audit_ocr: invalid file type: {filename}")
        raise HTTPException(status_code=400, detail="File must be PNG, JPG, or PDF")

    image_bytes = await file.read()
    logger.debug(f"audit_ocr: file size={len(image_bytes)} bytes")

    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")

    if filename.endswith(".pdf"):
        try:
            logger.debug("audit_ocr: converting PDF to image")
            image_bytes = await process_pdf_first_page(image_bytes)
            logger.debug("audit_ocr: PDF conversion successful")
        except Exception as e:
            logger.error(f"audit_ocr: PDF conversion failed: {e}")
            raise HTTPException(status_code=422, detail=f"PDF conversion failed: {e}")

    try:
        logger.debug("audit_ocr: starting OCR processing")
        ocr_result = await process_ocr(image_bytes)
        logger.info(
            f"audit_ocr: OCR done. confidence={ocr_result.confidence_avg:.3f}, rows={ocr_result.extracted_row_count}"
        )
    except Exception as e:
        logger.error(f"audit_ocr: OCR processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

    if ocr_result.confidence_avg < 0.10 and ocr_result.extracted_row_count == 0:
        raise HTTPException(
            status_code=422,
            detail="OCR failed: no text detected. Please export transcript as CSV from NSU portal and use CSV upload option.",
        )

    if ocr_result.extracted_row_count == 0:
        raise HTTPException(
            status_code=422,
            detail="No courses found. Please use CSV upload with columns: course_code,course_name,credits,grade,semester",
        )

    csv_text = ocr_result.csv_text
    if not csv_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No valid course data could be extracted from the image",
        )

    waivers_list = [w.strip() for w in waivers.split(",")] if waivers else []

    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    kf_name = f"program_knowledge_{program}.md"
    kf_path = os.path.join(base_dir, "program_knowledge", kf_name)

    if audit_level_int == 3 and not os.path.isfile(kf_path):
        raise HTTPException(
            status_code=422, detail=f"Knowledge file not found for program {program}"
        )

    try:
        logger.debug("audit_ocr: starting audit engine")
        result = await run_audit(
            csv_text=csv_text,
            program=program,
            audit_level=audit_level_int,
            waivers=waivers_list,
            knowledge_file=kf_path,
        )
        logger.info(f"audit_ocr: audit complete for user {current_user.id}")
    except Exception as e:
        logger.error(f"audit_ocr: run_audit failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")

    if not result or not result.get("result_json"):
        logger.error(f"audit_ocr: run_audit returned empty result")
        raise HTTPException(
            status_code=500, detail="Audit engine returned empty result"
        )

    raw_input = f"[OCR IMAGE] {filename}\n{ocr_result.csv_text[:500]}..."
    try:
        scan = await save_scan(current_user.id, result, "ocr_image", raw_input)
    except Exception as e:
        logger.error(f"audit_ocr: save_scan failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save scan: {e}")

    if not scan:
        raise HTTPException(status_code=500, detail="Failed to save scan to database")

    result_json = _safe_get(scan, "result_json", default={})
    result_text = str(_safe_get(scan, "result_text") or "")
    if result_text and len(result_text) > 500:
        result_text = result_text[:500] + "..."

    summary = {
        "total_credits": _safe_get(result_json, "total_credits", default=0),
        "cgpa": _safe_get(result_json, "cgpa", default=0.0),
        "standing": _safe_get(result_json, "standing", default="N/A"),
        "eligible": _safe_get(result_json, "eligible", default=False),
        "missing_courses": len(_safe_get(result_json, "missing_courses") or []),
    }

    response = {
        "scan_id": _safe_get(scan, "id", default=""),
        "student_id": _safe_get(scan, "student_id", default=""),
        "program": _safe_get(scan, "program", default=""),
        "audit_level": _safe_get(scan, "audit_level", default=audit_level_int),
        "summary": summary,
        "result_text": result_text,
        "created_at": _safe_get(scan, "created_at", default=""),
        "ocr_confidence": ocr_result.confidence_avg,
        "ocr_extracted_rows": ocr_result.extracted_row_count,
    }

    if ocr_result.warnings:
        response["ocr_warnings"] = ocr_result.warnings

    logger.info(f"audit_ocr: success, scan_id={response['scan_id']}")
    return response


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
    current_user: CurrentUser = Depends(get_current_user),
):
    """Save audit result with confirmed student ID. Auto-creates student if not exists."""
    STUDENT_ID_PATTERN = re.compile(r"^2\d{9}$")

    student_id = request.student_id.strip()
    if not student_id:
        raise HTTPException(status_code=400, detail="Student ID is required")
    if not STUDENT_ID_PATTERN.match(student_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid student ID format. Must be 10 digits starting with 2 (e.g., 2211234567)",
        )

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
            raise HTTPException(
                status_code=500, detail="Failed to auto-create student account"
            )

    result_json = dict(request.result_json)
    result_json["student_id"] = student_id

    scan = await save_scan(
        current_user.id,
        {"result_json": result_json, "result_text": request.result_text},
        request.input_type,
        request.raw_input,
    )
    if not scan:
        raise HTTPException(status_code=500, detail="Failed to save scan")

    scan_id_str: Optional[str] = (
        str(_safe_get(scan, "id")) if _safe_get(scan, "id") is not None else None
    )
    eligible = result_json.get("eligible", False)
    await create_audit_result(
        student_id=student_id,
        program=request.program,
        audit_level=request.audit_level,
        result_json=result_json,
        result_text=request.result_text,
        eligible=eligible,
        scan_id=scan_id_str,
    )

    summary = {
        "total_credits": result_json.get("total_credits", 0),
        "cgpa": result_json.get("cgpa", 0.0),
        "standing": result_json.get("standing", "N/A"),
        "eligible": eligible,
        "missing_courses": len(result_json.get("missing_courses", [])),
    }

    return {
        "scan_id": _safe_get(scan, "id", default=""),
        "student_id": student_id,
        "program": request.program,
        "audit_level": request.audit_level,
        "summary": summary,
        "result_text": request.result_text,
        "result_json": result_json,
        "created_at": _safe_get(scan, "created_at", default=""),
    }
