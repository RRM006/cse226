import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from backend.auth import get_current_user
from backend.services.audit_service import run_audit
from backend.services.scan_service import save_scan

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])

@router.post("/csv")
async def audit_csv(
    file: UploadFile = File(...),
    program: str = Form(...),
    audit_level: int = Form(...),
    waivers: str = Form(""),
    knowledge_file: str = Form(None),
    current_user: dict = Depends(get_current_user)
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
