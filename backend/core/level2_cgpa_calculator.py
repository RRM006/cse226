#!/usr/bin/env python3
"""
NSU Audit Core - Level 2: CGPA Calculator & Waiver Handler
Calculates weighted CGPA, handles retakes and waivers, determines academic standing.
Usage: python src/level2_cgpa_calculator.py <transcript.csv>
"""

import csv
import os
import sys
from collections import defaultdict

# ─────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────

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
    (3.80, 4.00, 'Summa Cum Laude'),
    (3.65, 3.79, 'Magna Cum Laude'),
    (3.50, 3.64, 'Cum Laude'),
    (3.00, 3.49, 'First Class (Good Standing)'),
    (2.50, 2.99, 'Second Class (Good Standing)'),
    (2.00, 2.49, 'Third Class (Good Standing)'),
    (0.00, 1.99, 'PROBATION'),
]

HONORS_MAP = {
    'Summa Cum Laude': 'Summa Cum Laude',
    'Magna Cum Laude': 'Magna Cum Laude',
    'Cum Laude': 'Cum Laude',
}

# Allowed waiver courses per program
ALLOWED_WAIVERS = {
    'BSCSE': ['ENG102', 'MAT116'],
    'BSEEE': ['ENG102', 'MAT116'],
    'LLB': ['ENG102'],
}

# Course names for waiver display
COURSE_NAMES = {
    'ENG102': 'Introduction to Composition',
    'MAT116': 'Pre-Calculus',
}

# Course credits for waiver display
COURSE_CREDITS = {
    'ENG102': 3,
    'MAT116': 0,
}

PROGRAM_LABELS = {
    'BSCSE': 'BSc in Computer Science and Engineering',
    'BSEEE': 'BSc in Electrical and Electronic Engineering',
    'LLB': 'LL.B Honors',
}


# ─────────────────────────────────────────────────────────────────────
# PARSING
# ─────────────────────────────────────────────────────────────────────

def parse_transcript(csv_text):
    """Parse a transcript CSV file. Returns (student_id, program, records)."""
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


# ─────────────────────────────────────────────────────────────────────
# RETAKE & WAIVER LOGIC
# ─────────────────────────────────────────────────────────────────────

def resolve_retakes(records):
    """
    Group records by course code. For courses with multiple attempts,
    identify the best valid grade.
    Returns (resolved dict, retake_info dict).
    """
    groups = defaultdict(list)
    for r in records:
        groups[r['code']].append(r)

    resolved = {}
    retake_info = {}

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

    return resolved, retake_info


# prompt_waivers removed for API compatibility


# ─────────────────────────────────────────────────────────────────────
# CGPA CALCULATION
# ─────────────────────────────────────────────────────────────────────

def calculate_cgpa(resolved, waivers):
    """
    Calculate CGPA from resolved courses.
    Only grades A through D count.
    Waived courses are excluded.
    0-credit courses do not affect CGPA.
    Returns (cgpa, total_grade_points, total_credits_counted).
    """
    total_points = 0.0
    total_credits = 0.0

    for code, record in resolved.items():
        if code in waivers:
            continue
        grade = record['grade']
        credits = record['credits']
        if grade not in VALID_GRADES:
            continue
        if credits == 0:
            continue

        pts = GRADE_POINTS[grade]
        total_points += pts * credits
        total_credits += credits

    if total_credits == 0:
        return 0.0, 0.0, 0.0

    cgpa = total_points / total_credits
    return cgpa, total_points, total_credits


def get_standing(cgpa):
    """Determine academic standing from CGPA."""
    if cgpa >= 3.80: return 'Summa Cum Laude'
    if cgpa >= 3.65: return 'Magna Cum Laude'
    if cgpa >= 3.50: return 'Cum Laude'
    if cgpa >= 3.00: return 'First Class (Good Standing)'
    if cgpa >= 2.50: return 'Second Class (Good Standing)'
    if cgpa >= 2.00: return 'Third Class (Good Standing)'
    return 'PROBATION'


def get_honors(standing):
    """Get honors designation from standing."""
    return HONORS_MAP.get(standing, 'None')


# ─────────────────────────────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────────────────────────────

def format_credits(val):
    """Format credit value: integer if whole, else float."""
    return int(val) if val == int(val) else val


def print_output(student_id, program, filename, records, resolved, retake_info,
                 waivers, cgpa, total_points, total_credits):
    """Print the Level 2 output in the exact box-drawing format."""
    program_label = PROGRAM_LABELS.get(program, program)
    standing = get_standing(cgpa)
    honors = get_honors(standing)
    is_probation = cgpa < 2.0

    print()
    print(f"=== NSU AUDIT CORE - LEVEL 2 ===")
    print(f"Student: {student_id}")
    print(f"Program: {program_label}")
    print(f"Processing: {filename}")
    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                     CGPA CALCULATION                         ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    # Waivers
    waiver_credits = sum(COURSE_CREDITS.get(w, 0) for w in waivers)
    print(f"Waivers Applied: {len(waivers)} course ({format_credits(waiver_credits)} credits)")
    if waivers:
        for i, w in enumerate(waivers):
            name = COURSE_NAMES.get(w, w)
            cr = COURSE_CREDITS.get(w, 0)
            connector = "└─" if i == len(waivers) - 1 else "├─"
            print(f"  {connector} {w}: {name} ({format_credits(cr)} credits)")
    print()

    # Retakes
    retake_display = []
    for code, attempts in retake_info.items():
        # Find old and new grades
        valid_attempts = [a for a in attempts if a['grade'] in VALID_GRADES]
        invalid_attempts = [a for a in attempts if a['grade'] not in VALID_GRADES]

        if code in resolved:
            best = resolved[code]
            best_grade = best['grade']
            best_pts = GRADE_POINTS[best_grade]

            for a in attempts:
                if a is not best:
                    old_grade = a['grade']
                    old_pts = GRADE_POINTS.get(old_grade, 0.0)
                    retake_display.append({
                        'code': code,
                        'name': best['name'],
                        'old_grade': old_grade,
                        'old_pts': old_pts,
                        'new_grade': best_grade,
                        'new_pts': best_pts,
                    })

    # Deduplicate retake display (show one line per retaken course)
    seen_retakes = set()
    unique_retakes = []
    for rd in retake_display:
        if rd['code'] not in seen_retakes:
            # For courses with multiple non-best attempts, show worst old grade
            all_old = [r for r in retake_display if r['code'] == rd['code']]
            worst_old = min(all_old, key=lambda x: x['old_pts'])
            unique_retakes.append(worst_old)
            seen_retakes.add(rd['code'])

    print(f"Retakes Processed: {len(unique_retakes)} courses")
    for i, rd in enumerate(unique_retakes):
        connector = "└─" if i == len(unique_retakes) - 1 else "├─"
        print(f"  {connector} {rd['code']}: {rd['old_grade']} ({rd['old_pts']:.1f}) → "
              f"{rd['new_grade']} ({rd['new_pts']:.1f})  ✓ IMPROVED")
    print()

    # Calculation
    print("Calculation:")
    print(f"  Total Grade Points:    {total_points:.1f}")
    print(f"  Total Credits Counted: {format_credits(total_credits)}")
    print()
    print(f"  CGPA = {total_points:.1f} / {format_credits(total_credits)} = {cgpa:.2f}")
    print()

    # Academic Standing
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                   ACADEMIC STANDING                          ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    print(f"CGPA:             {cgpa:.2f}")
    print(f"Standing:         {standing}")
    print(f"Honors:           {honors}")
    status_str = "⚠ PROBATION" if is_probation else "✓ GOOD STANDING"
    print(f"Status:           {status_str}")
    print()

    result_str = "❌ FAILED" if is_probation else "✓ PASSED"
    print(f"RESULT: {result_str} (CGPA = {cgpa:.2f})")


# ─────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────

def run_level2(csv_text: str, program: str, waivers: list[str] = None) -> dict:
    import io
    import sys
    
    if waivers is None:
        waivers = []
        
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    try:
        student_id, detect_prog, records = parse_transcript(csv_text)
        prog = program if program else detect_prog
        
        print(f"=== NSU AUDIT CORE - LEVEL 2 ===")
        print(f"Student: {student_id}")
        print(f"Program: {PROGRAM_LABELS.get(prog, prog)}")
        print(f"Processing: API Upload")
        print()
        
        resolved, retake_info = resolve_retakes(records)
        
        allowed = ALLOWED_WAIVERS.get(prog, [])
        valid_waivers = [w.strip().upper() for w in waivers if w.strip().upper() in allowed]
        
        cgpa, total_points, total_credits = calculate_cgpa(resolved, valid_waivers)
        
        print_cgpa_output(student_id, prog, "API Upload", records, resolved, retake_info,
                          valid_waivers, cgpa, total_points, total_credits)
        
        result_text = sys.stdout.getvalue()
        
        standing = get_standing(cgpa)
        is_probation = cgpa < 2.0
        
        result_json = {
            "student_id": student_id,
            "program": prog,
            "audit_level": 2,
            "total_credits": total_credits,
            "cgpa": round(cgpa, 2),
            "standing": standing,
            "eligible": not is_probation,
            "missing_courses": [],
            "excluded_courses": [],
            "waivers_applied": valid_waivers
        }
    finally:
        sys.stdout = old_stdout
        
    return {
        "result_text": result_text,
        "result_json": result_json
    }

def print_cgpa_output(student_id, program, filename, records, resolved, retake_info,
                      waivers, cgpa, total_points, total_credits):
    """Print CGPA output (called after waiver prompt so header is already shown)."""
    program_label = PROGRAM_LABELS.get(program, program)
    standing = get_standing(cgpa)
    honors = get_honors(standing)
    is_probation = cgpa < 2.0

    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                     CGPA CALCULATION                         ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    # Waivers
    waiver_credits = sum(COURSE_CREDITS.get(w, 0) for w in waivers)
    print(f"Waivers Applied: {len(waivers)} course ({format_credits(waiver_credits)} credits)")
    if waivers:
        for i, w in enumerate(waivers):
            name = COURSE_NAMES.get(w, w)
            cr = COURSE_CREDITS.get(w, 0)
            connector = "└─" if i == len(waivers) - 1 else "├─"
            print(f"  {connector} {w}: {name} ({format_credits(cr)} credits)")
    print()

    # Retakes
    unique_retakes = _build_retake_display(retake_info, resolved)
    print(f"Retakes Processed: {len(unique_retakes)} courses")
    for i, rd in enumerate(unique_retakes):
        connector = "└─" if i == len(unique_retakes) - 1 else "├─"
        print(f"  {connector} {rd['code']}: {rd['old_grade']} ({rd['old_pts']:.1f}) → "
              f"{rd['new_grade']} ({rd['new_pts']:.1f})  ✓ IMPROVED")
    print()

    # Calculation
    print("Calculation:")
    print(f"  Total Grade Points:    {total_points:.1f}")
    print(f"  Total Credits Counted: {format_credits(total_credits)}")
    print()
    print(f"  CGPA = {total_points:.1f} / {format_credits(total_credits)} = {cgpa:.2f}")
    print()

    # Academic Standing
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                   ACADEMIC STANDING                          ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    print(f"CGPA:             {cgpa:.2f}")
    print(f"Standing:         {standing}")
    print(f"Honors:           {honors}")
    status_str = "⚠ PROBATION" if is_probation else "✓ GOOD STANDING"
    print(f"Status:           {status_str}")
    print()

    result_str = "❌ FAILED" if is_probation else "✓ PASSED"
    print(f"RESULT: {result_str} (CGPA = {cgpa:.2f})")


def _build_retake_display(retake_info, resolved):
    """Build retake display list showing old→new grade improvements."""
    retake_display = []
    for code, attempts in retake_info.items():
        if code in resolved:
            best = resolved[code]
            best_grade = best['grade']
            best_pts = GRADE_POINTS[best_grade]

            # Find the worst attempt that isn't the best
            worst_grade = None
            worst_pts = 999
            for a in attempts:
                if a is not best:
                    g = a['grade']
                    p = GRADE_POINTS.get(g, 0.0)
                    if p < worst_pts:
                        worst_grade = g
                        worst_pts = p

            if worst_grade is not None:
                retake_display.append({
                    'code': code,
                    'name': best['name'],
                    'old_grade': worst_grade,
                    'old_pts': worst_pts,
                    'new_grade': best_grade,
                    'new_pts': best_pts,
                })

    return retake_display


if __name__ == '__main__':
    pass
