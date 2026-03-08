import os
from backend.core.level1_credit_tally import run_level1
from backend.core.level2_cgpa_calculator import run_level2
from backend.core.level3_audit_engine import run_level3

async def run_audit(
    csv_text: str,
    program: str,
    audit_level: int,
    waivers: list[str],
    knowledge_file: str
) -> dict:
    if audit_level == 1:
        return run_level1(csv_text, program, waivers)
    elif audit_level == 2:
        return run_level2(csv_text, program, waivers)
    elif audit_level == 3:
        if not os.path.isfile(knowledge_file):
            raise ValueError(f"Knowledge file not found: {knowledge_file}")
            
        with open(knowledge_file, "r", encoding="utf-8") as f:
            knowledge_content = f.read()
            
        return run_level3(csv_text, program, waivers, knowledge_content)
    else:
        raise ValueError("Invalid audit level. Must be 1, 2, or 3.")
