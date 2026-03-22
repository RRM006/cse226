"""
NSU Audit Core - Unit Tests for Core Engine
Tests for Level 1, Level 2, and shared utilities.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.core.shared import (
    parse_transcript,
    detect_program,
    resolve_retakes,
    calculate_cgpa,
    get_standing,
    format_credits,
    VALID_GRADES,
    GRADE_POINTS,
)
from backend.core.level1_credit_tally import (
    compute_category_credits,
    run_level1,
)
from backend.core.level2_cgpa_calculator import (
    calculate_cgpa as level2_calculate_cgpa,
    resolve_retakes as level2_resolve_retakes,
)


SAMPLE_BSCSE_CSV = """# Student: TEST001
# Program: BSCSE
# Test: Basic passing grades
course_code,course_name,credits,grade,semester
ENG102,Introduction to Composition,3,A,Fall2021
ENG103,Intermediate Composition,3,B+,Fall2021
MAT116,Pre-Calculus,0,A,Fall2021
CSE115,Programming Language I,3,A,Fall2021
CSE115L,Programming Language I Lab,1,A,Fall2021
"""

SAMPLE_LLB_CSV = """# Student: TEST002
# Program: LLB
# Test: LLB program
course_code,course_name,credits,grade,semester
ENG102,Introduction to Composition,3,A,Fall2021
LLB101,Introduction to Law I,3,A,Fall2021
LLB102,Introduction to Law II,3,B+,Fall2021
LLB103,Constitutional Law,3,A,Spring2022
"""

SAMPLE_RETAKE_CSV = """# Student: TEST003
# Test: Retake scenario
course_code,course_name,credits,grade,semester
CSE115,Programming Language I,3,F,Fall2021
CSE115,Programming Language I,3,B,Spring2022
CSE225,Data Structures,3,A,Spring2022
"""

SAMPLE_INVALID_GRADES_CSV = """# Student: TEST004
# Test: Invalid grades
course_code,course_name,credits,grade,semester
CSE115,Programming Language I,3,A,Fall2021
CSE173,Discrete Mathematics,3,F,Fall2021
CSE225,Data Structures,3,W,Spring2022
"""


class TestSharedUtils:
    """Tests for shared utility functions."""

    def test_parse_transcript_basic(self):
        student_id, program, records = parse_transcript(SAMPLE_BSCSE_CSV)
        assert student_id == 'TEST001'
        assert program == 'BSCSE'
        assert len(records) == 5
        assert records[0]['code'] == 'ENG102'
        assert records[0]['grade'] == 'A'

    def test_parse_transcript_detects_llb(self):
        student_id, program, records = parse_transcript(SAMPLE_LLB_CSV)
        assert program == 'LLB'
        assert len(records) == 4

    def test_parse_transcript_missing_columns(self):
        with pytest.raises(ValueError, match="Missing required CSV columns"):
            parse_transcript("code,name,grade\nCSE115,A,Fall2021")

    def test_detect_program_bscse(self):
        records = [
            {'code': 'CSE311', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S1'},
            {'code': 'CSE327', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S2'},
        ]
        assert detect_program(records) == 'BSCSE'

    def test_detect_program_bseee(self):
        records = [
            {'code': 'EEE311', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S1'},
            {'code': 'EEE321', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S2'},
        ]
        assert detect_program(records) == 'BSEEE'

    def test_detect_program_llb(self):
        records = [
            {'code': 'LLB101', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S1'},
            {'code': 'LLB102', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S2'},
        ]
        assert detect_program(records) == 'LLB'

    def test_resolve_retakes_best_grade_kept(self):
        records = [
            {'code': 'CSE115', 'name': 'Test', 'credits': 3, 'grade': 'F', 'semester': 'S1'},
            {'code': 'CSE115', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S2'},
        ]
        resolved, retake_info, excluded = resolve_retakes(records)
        assert 'CSE115' in resolved
        assert resolved['CSE115']['grade'] == 'A'
        assert 'CSE115' in retake_info
        assert 'CSE115' in [r['code'] for r, _ in excluded]

    def test_resolve_retakes_no_retake(self):
        records = [
            {'code': 'CSE115', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S1'},
        ]
        resolved, retake_info, excluded = resolve_retakes(records)
        assert 'CSE115' in resolved
        assert len(retake_info) == 0

    def test_calculate_cgpa(self):
        resolved = {
            'CSE115': {'code': 'CSE115', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S1'},
            'CSE225': {'code': 'CSE225', 'name': 'Test', 'credits': 3, 'grade': 'B', 'semester': 'S2'},
        }
        total_credits, weighted_points, cgpa = calculate_cgpa(resolved)
        assert total_credits == 6.0
        assert abs(cgpa - 3.5) < 0.01

    def test_calculate_cgpa_with_waiver(self):
        resolved = {
            'ENG102': {'code': 'ENG102', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S1'},
            'CSE115': {'code': 'CSE115', 'name': 'Test', 'credits': 3, 'grade': 'B', 'semester': 'S2'},
        }
        total_credits, weighted_points, cgpa = calculate_cgpa(resolved, waivers=['ENG102'])
        assert total_credits == 3.0
        assert cgpa == 3.0

    def test_get_standing_honors(self):
        assert get_standing(3.95) == "Dean's Honor Roll"
        assert get_standing(3.75) == "First Class Honors"

    def test_get_standing_probation(self):
        assert get_standing(1.5) == "Academic Probation"

    def test_format_credits(self):
        assert format_credits(3.0) == 3
        assert format_credits(3.5) == 3.5
        assert format_credits(0) == 0


class TestLevel1CreditTally:
    """Tests for Level 1 credit tally functionality."""

    def test_run_level1_basic(self):
        result = run_level1(SAMPLE_BSCSE_CSV, 'BSCSE')
        assert 'result_text' in result
        assert 'result_json' in result
        assert result['result_json']['program'] == 'BSCSE'
        assert result['result_json']['audit_level'] == 1

    def test_run_level1_calculates_credits(self):
        result = run_level1(SAMPLE_BSCSE_CSV, 'BSCSE')
        assert result['result_json']['total_credits'] == 10.0

    def test_compute_category_credits_bscse(self):
        records = [
            {'code': 'ENG102', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S1'},
            {'code': 'ENG103', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S1'},
            {'code': 'ENG111', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S1'},
            {'code': 'BAN205', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S1'},
            {'code': 'CSE115', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S1'},
        ]
        resolved = {
            'ENG102': records[0], 'ENG103': records[1], 
            'ENG111': records[2], 'BAN205': records[3],
            'CSE115': records[4]
        }
        results = compute_category_credits(resolved, 'BSCSE')
        assert 'University Core - Languages' in results
        assert results['University Core - Languages']['complete'] is True
        assert results['University Core - Languages']['earned'] == 12


class TestLevel2CGPA:
    """Tests for Level 2 CGPA calculator."""

    def test_level2_resolve_retakes(self):
        records = [
            {'code': 'CSE115', 'name': 'Test', 'credits': 3, 'grade': 'F', 'semester': 'S1'},
            {'code': 'CSE115', 'name': 'Test', 'credits': 3, 'grade': 'B', 'semester': 'S2'},
        ]
        resolved, retake_info = level2_resolve_retakes(records)
        assert 'CSE115' in resolved
        assert resolved['CSE115']['grade'] == 'B'
        assert 'CSE115' in retake_info

    def test_level2_calculate_cgpa(self):
        resolved = {
            'CSE115': {'code': 'CSE115', 'name': 'Test', 'credits': 3, 'grade': 'A', 'semester': 'S1'},
        }
        cgpa, total_gp, total_creds = level2_calculate_cgpa(resolved, [])
        assert cgpa == 4.0
        assert total_creds == 3.0


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_csv(self):
        csv_text = "# Student: EMPTY\n# Program: BSCSE\ncourse_code,course_name,credits,grade,semester\n"
        student_id, program, records = parse_transcript(csv_text)
        assert student_id == 'EMPTY'
        assert records == []

    def test_grade_case_insensitive(self):
        csv_text = """# Student: TEST
# Program: BSCSE
course_code,course_name,credits,grade,semester
CSE115,Test,3,a,Fall2021
"""
        student_id, program, records = parse_transcript(csv_text)
        assert records[0]['grade'] == 'A'

    def test_credit_value_conversion(self):
        csv_text = """# Student: TEST
# Program: BSCSE
course_code,course_name,credits,grade,semester
CSE115,Test,3.0,A,Fall2021
"""
        student_id, program, records = parse_transcript(csv_text)
        assert records[0]['credits'] == 3.0

    def test_zero_credit_courses_excluded_from_cgpa(self):
        records = [
            {'code': 'MAT116', 'name': 'Test', 'credits': 0, 'grade': 'A', 'semester': 'S1'},
        ]
        total_creds, _, cgpa = calculate_cgpa({'MAT116': records[0]})
        assert total_creds == 0.0
        assert cgpa == 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
