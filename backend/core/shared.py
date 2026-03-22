"""
NSU Audit Core - Shared Utilities Module
Common functions shared across Level 1, Level 2, and Level 3 audit engines.
"""

import csv
from collections import defaultdict
from typing import Optional, List

VALID_GRADES = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D'}
INVALID_GRADE_LABELS = {
    'F': 'FAILED',
    'W': 'WITHDRAWN',
    'I': 'INCOMPLETE',
    'X': 'MARKED',
}

GRADE_POINTS = {
    'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7,
    'D+': 1.3, 'D': 1.0,
    'F': 0.0, 'I': 0.0, 'W': 0.0, 'X': 0.0,
}

ACADEMIC_STANDING = [
    (3.90, "Dean's Honor Roll"),
    (3.70, "First Class Honors"),
    (3.50, "Second Class First Division"),
    (3.00, "Second Class Second Division"),
    (2.00, "Pass"),
    (0.00, "Academic Probation"),
]


def parse_transcript(csv_text):
    """
    Parse a transcript CSV text. Returns (student_id, program, records).
    Validates required columns before parsing.
    """
    student_id = 'Unknown'
    program = None
    records = []

    lines = csv_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            if 'Student:' in line:
                student_id = line.split('Student:')[1].strip()
            elif 'Program:' in line:
                prog = line.split('Program:')[1].strip().upper()
                if 'LLB' in prog or 'LAW' in prog:
                    program = 'LLB'
                elif 'BSEEE' in prog or 'EEE' in prog:
                    program = 'BSEEE'
                elif 'BSCSE' in prog or 'CSE' in prog:
                    program = 'BSCSE'
            continue
        break

    data_lines = [l for l in lines if not l.strip().startswith('#')]
    reader = csv.DictReader(data_lines)
    
    required_columns = {'course_code', 'course_name', 'credits', 'grade', 'semester'}
    if reader.fieldnames:
        missing = required_columns - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required CSV columns: {missing}")
    
    for row in reader:
        code = row['course_code'].strip().upper()
        name = row['course_name'].strip()
        try:
            credits = float(row['credits'].strip())
        except ValueError:
            credits = 0.0
        grade = row['grade'].strip().upper()
        semester = row['semester'].strip()
        records.append({
            'code': code,
            'name': name,
            'credits': credits,
            'grade': grade,
            'semester': semester,
        })

    if program is None:
        program = detect_program(records)

    return student_id, program, records


def detect_program(records):
    """Heuristically detect the program from course codes."""
    codes = [r['code'] for r in records]
    has_llb = any(c.startswith('LLB') for c in codes)
    has_eee_major = any(c.startswith('EEE2') or c.startswith('EEE3') or c.startswith('EEE4') for c in codes)
    has_cse_major = any(c.startswith('CSE2') or c.startswith('CSE3') or c.startswith('CSE4') for c in codes)

    if has_llb:
        return 'LLB'
    elif has_eee_major and not has_cse_major:
        return 'BSEEE'
    else:
        return 'BSCSE'


def resolve_retakes(records):
    """
    Group records by course code. For courses with multiple attempts,
    keep the best valid grade attempt for credit counting.
    Returns (resolved_courses dict, retake_info dict, excluded list).
    """
    groups = defaultdict(list)
    for r in records:
        groups[r['code']].append(r)

    resolved = {}
    retake_info = {}
    excluded = []

    for code, attempts in groups.items():
        if len(attempts) > 1:
            retake_info[code] = attempts

        best = None
        best_points = -1
        for attempt in attempts:
            grade = attempt['grade']
            if grade in VALID_GRADES:
                pts = GRADE_POINTS.get(grade, 0)
                if pts > best_points:
                    best = attempt
                    best_points = pts

        if best is not None:
            resolved[code] = best
        
        for attempt in attempts:
            if attempt['grade'] in INVALID_GRADE_LABELS:
                excluded.append((attempt, INVALID_GRADE_LABELS[attempt['grade']]))

    return resolved, retake_info, excluded


def calculate_cgpa(resolved, waivers: Optional[List[str]] = None):
    """
    Calculate weighted CGPA from resolved records.
    Returns (total_credits, weighted_points, cgpa).
    """
    total_credits = 0.0
    weighted_points = 0.0
    waivers = waivers or []

    for code, record in resolved.items():
        if code in waivers:
            continue
        grade = record['grade']
        credits = record['credits']
        
        if grade not in VALID_GRADES:
            continue
        
        points = GRADE_POINTS.get(grade, 0)
        total_credits += credits
        weighted_points += points * credits

    if total_credits == 0:
        return total_credits, weighted_points, 0.0

    cgpa = weighted_points / total_credits
    return total_credits, weighted_points, cgpa


def get_standing(cgpa):
    """Determine academic standing based on CGPA."""
    for threshold, standing in ACADEMIC_STANDING:
        if cgpa >= threshold:
            return standing
    return "Academic Probation"


def format_credits(val):
    """Format credit value: integer if whole, else float."""
    return int(val) if val == int(val) else val
