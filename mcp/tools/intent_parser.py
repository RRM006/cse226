import re
from typing import Any, Optional


VALID_PROGRAMS = ['BSCSE', 'BSEEE', 'LLB']
VALID_AUDIT_LEVELS = [1, 2, 3]


def parse_audit_query(query: str, available_folders: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """
    Parse natural language query for audit intent.
    
    Returns a dict with extracted parameters:
    - folder_name: str (required)
    - program: str (required)  
    - audit_level: int (default: 3)
    - file_name: str (optional, for single file)
    - send_email: bool (default: False)
    - student_email: str (optional)
    - waivers: list (optional)
    - confidence: float (0-1, how certain the parsing is)
    - missing_info: list (what info couldn't be determined)
    """
    query_lower = query.lower()
    
    result = {
        'folder_name': None,
        'program': None,
        'audit_level': 3,
        'file_name': None,
        'send_email': False,
        'student_email': None,
        'waivers': [],
        'confidence': 0.0,
        'missing_info': [],
        'raw_query': query
    }
    
    missing_info = []
    confidence_parts = []
    
    # ========== FOLDER NAME ==========
    if available_folders:
        folder_name = None
        best_match_len = 0
        
        for folder in available_folders:
            folder_lower = folder['folder_name'].lower()
            
            if folder_lower in query_lower:
                if len(folder_lower) > best_match_len:
                    folder_name = folder['folder_name']
                    best_match_len = len(folder_lower)
        
        if not folder_name:
            for folder in available_folders:
                folder_lower = folder['folder_name'].lower()
                words = folder_lower.split()
                if any(word in query_lower for word in words if len(word) > 2):
                    folder_name = folder['folder_name']
                    break
        
        if folder_name:
            result['folder_name'] = folder_name
            confidence_parts.append(0.3)
        else:
            missing_info.append("folder name")
    else:
        folder_patterns = [
            r'(?:in|from|folder|directory)\s+["\']?(\w+)["\']?',
            r'(?:folder|directory)\s+["\']?(\w+)["\']?',
        ]
        for pattern in folder_patterns:
            match = re.search(pattern, query_lower)
            if match:
                result['folder_name'] = match.group(1)
                confidence_parts.append(0.2)
                break
    
    if not result['folder_name']:
        missing_info.append("folder name (use folder name like 'mcptest', 'mcp2.0', etc.)")
    
    # ========== PROGRAM ==========
    program_patterns = {
        'bscse': 'BSCSE',
        'bscse': 'BSCSE',
        'computer science': 'BSCSE',
        'cse': 'BSCSE',
        'bseee': 'BSEEE',
        'electrical': 'BSEEE',
        'eee': 'BSEEE',
        'llb': 'LLB',
        'law': 'LLB',
    }
    
    for pattern, program in program_patterns.items():
        if pattern in query_lower:
            result['program'] = program
            confidence_parts.append(0.25)
            break
    
    if not result['program']:
        missing_info.append("program (BSCSE, BSEEE, or LLB)")
    
    # ========== AUDIT LEVEL ==========
    level_patterns = {
        r'\bl1\b': 1,
        r'\blevel\s*1\b': 1,
        r'\bcredit\b.*\btally\b': 1,
        r'\bcredits?\b': 1,
        r'\bl2\b': 2,
        r'\blevel\s*2\b': 2,
        r'\bcgpa\b': 2,
        r'\bgpa\b': 2,
        r'\bl3\b': 3,
        r'\blevel\s*3\b': 3,
        r'\bfull\b.*\baudit\b': 3,
        r'\bgraduation\b': 3,
    }
    
    for pattern, level in level_patterns.items():
        if re.search(pattern, query_lower):
            result['audit_level'] = level
            confidence_parts.append(0.2)
            break
    
    # ========== FILE NAME ==========
    file_patterns = [
        r'file\s+["\']?([^"\']+)["\']?',
        r'(?:transcript|csv)["\']?\s+["\']?([^"\']+)["\']?',
        r'(?:for|of)\s+["\']?([^"\']+)["\']?(?:\s|$)',
    ]
    
    for pattern in file_patterns:
        match = re.search(pattern, query_lower)
        if match:
            potential_file = match.group(1).strip()
            if potential_file and len(potential_file) > 2:
                result['file_name'] = potential_file
                confidence_parts.append(0.15)
                break
    
    # ========== EMAIL ==========
    email_patterns = [
        r'email\s+(?:to\s+)?([^,\s]+@[^,\s]+)',
        r'send\s+(?:email\s+)?(?:to\s+)?([^,\s]+@[^,\s]+)',
        r'mail\s+to\s+([^,\s]+@[^,\s]+)',
    ]
    
    for pattern in email_patterns:
        match = re.search(pattern, query_lower)
        if match:
            result['send_email'] = True
            result['student_email'] = match.group(1)
            confidence_parts.append(0.15)
            break
    
    if 'email' in query_lower or 'mail' in query_lower:
        if not result['send_email']:
            result['send_email'] = True
            result['missing_info'].append("student email address")
            confidence_parts.append(0.1)
    
    # ========== WAIVERS ==========
    waiver_pattern = r'waive[s]?\s+([A-Za-z0-9,\s]+)'
    match = re.search(waiver_pattern, query_lower)
    if match:
        waiver_courses = [w.strip().upper() for w in match.group(1).split(',')]
        waiver_courses = [w for w in waiver_courses if w]
        if waiver_courses:
            result['waivers'] = waiver_courses
            confidence_parts.append(0.1)
    
    # ========== STUDENT ID ==========
    student_id_pattern = r'\b\d{10,}\b'
    match = re.search(student_id_pattern, query)
    if match:
        result['student_id'] = match.group(0)
        confidence_parts.append(0.1)
    
    # ========== CALCULATE CONFIDENCE ==========
    if confidence_parts:
        result['confidence'] = min(sum(confidence_parts), 1.0)
    
    result['missing_info'] = missing_info
    
    return result


def format_clarification_request(parsed: dict) -> Optional[str]:
    """Generate a clarification request for missing information."""
    missing = parsed.get('missing_info', [])
    if not missing:
        return None
    
    parts = []
    if 'folder name' in missing:
        parts.append("folder name (e.g., 'mcptest', 'mcp2.0', 'mcptest2')")
    if 'program' in missing:
        parts.append("program (BSCSE, BSEEE, or LLB)")
    if 'student email address' in missing:
        parts.append("student email address (to send results)")
    
    if parts:
        return f"I need more information to complete this audit. Please specify: {', '.join(parts)}"
    return ""


def validate_parsed_query(parsed: dict) -> tuple[bool, Optional[str]]:
    """
    Validate that parsed query has required fields.
    
    Returns (is_valid, error_message)
    """
    if not parsed.get('folder_name'):
        return False, "No folder name found. Please specify a folder name."
    
    if not parsed.get('program'):
        return False, "No program found. Please specify BSCSE, BSEEE, or LLB."
    
    if parsed.get('program') not in VALID_PROGRAMS:
        return False, f"Invalid program '{parsed['program']}'. Must be BSCSE, BSEEE, or LLB."
    
    audit_level = parsed.get('audit_level', 3)
    if audit_level not in VALID_AUDIT_LEVELS:
        return False, f"Invalid audit level '{audit_level}'. Must be 1, 2, or 3."
    
    return True, None
