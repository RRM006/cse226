import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'backend'))

from core.level1_credit_tally import run_level1
from core.level2_cgpa_calculator import run_level2
from core.level3_audit_engine import run_level3


def run_audit_offline(csv_text: str, program: str, audit_level: int, waivers: list = None) -> dict:
    """
    Run audit in offline mode using the Phase 1 audit engine.
    
    Args:
        csv_text: Raw CSV transcript content
        program: Program (BSCSE, BSEEE, LLB)
        audit_level: 1, 2, or 3
        waivers: Optional list of course codes to waive
    
    Returns:
        Standardized result dict with student_id, program, audit_level, cgpa,
        total_credits, eligible, deficiencies, result_text, result_json
    """
    if waivers is None:
        waivers = []
    
    program = program.upper()
    
    if audit_level == 1:
        result = run_level1(csv_text, program, waivers)
    elif audit_level == 2:
        result = run_level2(csv_text, program, waivers)
    elif audit_level == 3:
        knowledge_file = project_root / 'program_knowledge' / f'program_knowledge_{program}.md'
        if not knowledge_file.exists():
            knowledge_file = project_root / 'program_knowledge' / 'program_knowledge_BSCSE.md'
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            knowledge_content = f.read()
        result = run_level3(csv_text, program, waivers, knowledge_content)
    else:
        raise ValueError("Invalid audit level. Must be 1, 2, or 3.")
    
    rj = result['result_json']
    
    return {
        'student_id': rj.get('student_id', 'Unknown'),
        'program': rj.get('program', program),
        'audit_level': rj.get('audit_level', audit_level),
        'cgpa': rj.get('cgpa', 0.0),
        'total_credits': rj.get('total_credits', 0),
        'eligible': rj.get('eligible', False),
        'deficiencies': rj.get('missing_courses', []),
        'result_text': result['result_text'],
        'result_json': rj
    }
