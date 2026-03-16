import sys
from pathlib import Path
from typing import Optional, Any

_mcp_dir = Path(__file__).parent.parent
sys.path.insert(0, str(_mcp_dir))

from datetime import datetime

from tools.drive_tools import list_drive_folder, get_transcript
from tools.audit_tools import run_audit
from tools.email_tools import send_email
from history.local_log import append_record


def batch_audit_folder(
    folder_name: str,
    program: str,
    audit_level: int,
    send_emails: bool = False,
    email_domain: Optional[str] = None,
    waivers: Optional[list] = None
) -> dict[str, Any]:
    """
    Audit all transcripts in a Google Drive folder.
    
    Steps:
    1. List files in the folder
    2. For each file: download, audit, optionally email
    3. Return summary
    
    Args:
        folder_name: Name of the Drive folder
        program: BSCSE, BSEEE, or LLB
        audit_level: 1, 2, or 3
        send_emails: If True, send email to each student
        email_domain: Domain to construct student emails (e.g. "northsouth.edu")
        waivers: Optional list of course codes to waive
    
    Returns:
        {total_processed, eligible_count, ineligible_count, error_count, errors, results}
    """
    if waivers is None:
        waivers = []
    
    result = {
        'total_processed': 0,
        'eligible_count': 0,
        'ineligible_count': 0,
        'error_count': 0,
        'errors': [],
        'results': [],
        'progress': []
    }
    
    files = list_drive_folder(folder_name, ['csv'])
    
    if isinstance(files, str):
        result['errors'].append({'file_name': folder_name, 'error': files})
        result['error_count'] = 1
        return result
    
    if not files:
        result['progress'].append(f"No CSV files found in folder '{folder_name}'")
        return result
    
    for i, file_info in enumerate(files, 1):
        file_id = file_info['file_id']
        file_name = file_info['file_name']
        
        try:
            transcript_result = get_transcript(file_id, file_name)
            
            if isinstance(transcript_result, str):
                error_msg = f"Failed to download: {transcript_result}"
                result['errors'].append({'file_name': file_name, 'error': error_msg})
                result['error_count'] += 1
                result['progress'].append(f"✗ [{i}/{len(files)}] {file_name} — ERROR")
                continue
            
            if transcript_result.get('content_type') != 'csv':
                result['errors'].append({'file_name': file_name, 'error': 'Not a CSV file'})
                result['error_count'] += 1
                result['progress'].append(f"✗ [{i}/{len(files)}] {file_name} — SKIPPED (not CSV)")
                continue
            
            csv_content = transcript_result['content']
            
            audit_result = run_audit(csv_content, program, audit_level, waivers)
            
            result['total_processed'] += 1
            
            if audit_result.get('eligible'):
                result['eligible_count'] += 1
                status = "ELIGIBLE"
            else:
                result['ineligible_count'] += 1
                status = "NOT ELIGIBLE"
            
            student_id = audit_result.get('student_id', 'Unknown')
            cgpa = audit_result.get('cgpa', 0.0)
            
            progress_msg = f"✓ [{i}/{len(files)}] Student {student_id} — {status} (CGPA: {cgpa:.2f})"
            result['progress'].append(progress_msg)
            
            if send_emails and email_domain:
                student_email = f"{student_id}@{email_domain}"
                email_result = send_email(student_email, audit_result)
                if email_result.get('status') == 'sent':
                    result['progress'][-1] += " [EMAIL SENT]"
                else:
                    result['progress'][-1] += f" [EMAIL FAILED: {email_result.get('error')}]"
            
            record = {
                'type': 'audit',
                'scan_id': f"{student_id}_{datetime.utcnow().isoformat()}",
                'student_id': student_id,
                'program': program,
                'audit_level': audit_level,
                'cgpa': cgpa,
                'total_credits': audit_result.get('total_credits', 0),
                'eligible': audit_result.get('eligible', False),
                'deficiencies': audit_result.get('deficiencies', []),
                'created_at': datetime.utcnow().isoformat() + 'Z'
            }
            append_record(record)
            
            result['results'].append(audit_result)
        
        except Exception as e:
            error_msg = str(e)
            result['errors'].append({'file_name': file_name, 'error': error_msg})
            result['error_count'] += 1
            result['progress'].append(f"✗ [{i}/{len(files)}] {file_name} — ERROR: {error_msg}")
    
    return result
