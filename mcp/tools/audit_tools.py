import httpx
from typing import Any, Optional

from config import get_config
from offline.engine_bridge import run_audit_offline


VALID_PROGRAMS = ['BSCSE', 'BSEEE', 'LLB']
VALID_AUDIT_LEVELS = [1, 2, 3]


def run_audit(
    transcript_content: str,
    program: str,
    audit_level: int,
    waivers: list = None,
    student_email: Optional[str] = None
) -> dict[str, Any]:
    """
    Run a graduation audit on a transcript.
    
    Operates in two modes:
    - Offline (default): Uses embedded Phase 1 engine
    - Remote: POSTs to FastAPI backend on Railway
    
    Args:
        transcript_content: Raw CSV text (from get_transcript) or base64 for images
        program: BSCSE, BSEEE, or LLB
        audit_level: 1, 2, or 3
        waivers: Optional list of course codes to waive
        student_email: Stored in result for email tool
    
    Returns:
        Standardized result dict with student_id, program, audit_level, cgpa,
        total_credits, eligible, deficiencies, result_text, result_json
    """
    if waivers is None:
        waivers = []
    
    program = program.upper()
    
    if program not in VALID_PROGRAMS:
        return {
            'error': f"Invalid program. Must be one of: {VALID_PROGRAMS}",
            'student_id': 'Unknown'
        }
    
    if audit_level not in VALID_AUDIT_LEVELS:
        return {
            'error': f"Invalid audit_level. Must be one of: {VALID_AUDIT_LEVELS}",
            'student_id': 'Unknown'
        }
    
    config = get_config()
    
    if config['remote']:
        return _run_audit_remote(
            transcript_content,
            program,
            audit_level,
            waivers,
            student_email,
            config
        )
    else:
        return _run_audit_offline_wrapper(
            transcript_content,
            program,
            audit_level,
            waivers,
            student_email
        )


def _run_audit_offline_wrapper(
    transcript_content: str,
    program: str,
    audit_level: int,
    waivers: list,
    student_email: str = None
) -> dict[str, Any]:
    """Run audit using the offline engine."""
    try:
        result = run_audit_offline(transcript_content, program, audit_level, waivers)
        result['student_email'] = student_email
        return result
    except Exception as e:
        return {
            'error': f"Offline audit failed: {str(e)}",
            'student_id': 'Unknown',
            'program': program,
            'audit_level': audit_level,
            'cgpa': 0.0,
            'total_credits': 0,
            'eligible': False,
            'deficiencies': [],
            'result_text': '',
            'result_json': {}
        }


def _run_audit_remote(
    transcript_content: str,
    program: str,
    audit_level: int,
    waivers: list,
    student_email: str,
    config: dict
) -> dict[str, Any]:
    """Run audit via the FastAPI backend."""
    api_url = config['api_url']
    api_token_path = config['api_token_path']
    
    api_token = None
    if api_token_path.exists():
        with open(api_token_path, 'r') as f:
            api_token = f.read().strip()
    
    if not api_token:
        return {
            'error': "API token not found. Set up via web app or run in offline mode.",
            'student_id': 'Unknown'
        }
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    is_image = isinstance(transcript_content, str) and len(transcript_content) > 1000 and not '\n' in transcript_content[:100]
    
    try:
        if is_image:
            response = httpx.post(
                f'{api_url}/api/v1/audit/ocr',
                headers=headers,
                json={
                    'image_content': transcript_content,
                    'program': program,
                    'audit_level': audit_level,
                    'waivers': waivers
                },
                timeout=60.0
            )
        else:
            response = httpx.post(
                f'{api_url}/api/v1/audit/csv',
                headers=headers,
                json={
                    'csv_content': transcript_content,
                    'program': program,
                    'audit_level': audit_level,
                    'waivers': waivers
                },
                timeout=30.0
            )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'student_id': result.get('student_id', 'Unknown'),
                'program': result.get('program', program),
                'audit_level': result.get('audit_level', audit_level),
                'cgpa': result.get('cgpa', 0.0),
                'total_credits': result.get('total_credits', 0),
                'eligible': result.get('eligible', False),
                'deficiencies': result.get('missing_courses', []),
                'result_text': result.get('result_text', ''),
                'result_json': result,
                'student_email': student_email
            }
        else:
            return _fallback_to_offline(
                transcript_content, program, audit_level, waivers, student_email,
                f"Remote API error ({response.status_code}): {response.text}"
            )
    
    except Exception as e:
        return _fallback_to_offline(
            transcript_content, program, audit_level, waivers, student_email,
            f"Remote call failed: {str(e)}"
        )


def _fallback_to_offline(
    transcript_content: str,
    program: str,
    audit_level: int,
    waivers: list,
    student_email: str,
    error_message: str
) -> dict[str, Any]:
    """Fallback to offline mode with a warning."""
    try:
        result = run_audit_offline(transcript_content, program, audit_level, waivers)
        result['student_email'] = student_email
        result['_warning'] = f"{error_message}. Fell back to offline mode."
        return result
    except Exception as e:
        return {
            'error': f"Both remote and offline failed. Remote: {error_message}. Offline: {str(e)}",
            'student_id': 'Unknown',
            'program': program,
            'audit_level': audit_level,
            'cgpa': 0.0,
            'total_credits': 0,
            'eligible': False,
            'deficiencies': [],
            'result_text': '',
            'result_json': {}
        }
