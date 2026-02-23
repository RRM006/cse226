#!/usr/bin/env python3
"""
NSU Audit Core - Level 1: Credit Tally Engine
Reads a student transcript CSV and calculates total valid earned credits.
Usage: python src/level1_credit_tally.py <transcript.csv>
"""

import sys
import csv
import os
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

# ─────────────────────────────────────────────────────────────────────
# PROGRAM KNOWLEDGE (embedded for L1 — no knowledge file input)
# Courses can appear in multiple categories. Each course's credits are
# counted ONCE toward the total but satisfy ALL matching categories.
# ─────────────────────────────────────────────────────────────────────

BSCSE_CATEGORIES = {
    'University Core - Languages': {
        'credits': 12,
        'courses': ['ENG102', 'ENG103', 'ENG111', 'BAN205'],
    },
    'University Core - Humanities': {
        'credits': 9,
        'courses': ['PHI104', 'HIS102', 'HIS103'],
    },
    'University Core - Social Sciences': {
        'credits': 9,
        'courses': ['ECO101', 'ECO104', 'POL101', 'POL104', 'SOC101', 'ANT101', 'ENV203', 'GEO205'],
        'pick': 3,
    },
    'University Core - Sciences': {
        'credits': 4,
        'courses': ['BIO103', 'PHY107', 'CHE101'],
        'pick': 1,
    },
    'SEPS Core': {
        'credits': 38,
        'courses': ['MAT116', 'MAT120', 'MAT130', 'MAT250', 'MAT361', 'MAT125', 'MAT350',
                     'PHY107', 'PHY108', 'CHE101', 'EEE452', 'CEE110', 'CSE115', 'CSE115L'],
    },
    'Major Core': {
        'credits': 42,
        'courses': ['CSE173', 'CSE215', 'CSE215L', 'CSE225', 'CSE225L', 'CSE231', 'CSE231L',
                     'EEE141', 'EEE141L', 'EEE111', 'EEE111L', 'CSE311', 'CSE311L',
                     'CSE323', 'CSE327', 'CSE331', 'CSE331L', 'CSE373', 'CSE332', 'CSE425'],
    },
    'Capstone': {
        'credits': 4,
        'courses': ['CSE299', 'CSE499A', 'CSE499B'],
    },
    'Elective Trails': {
        'credits': 9,
        'courses': [
            'CSE401', 'CSE417', 'CSE418', 'CSE426', 'CSE473', 'CSE491',
            'CSE411', 'CSE427', 'CSE428', 'CSE429', 'CSE492',
            'CSE422', 'CSE438', 'CSE482', 'CSE485', 'CSE486', 'CSE493',
            'CSE433', 'CSE435', 'CSE413', 'CSE414', 'CSE415', 'CSE494',
            'CSE440', 'CSE445', 'CSE465', 'CSE467', 'CSE470', 'CSE419',
            'CSE446', 'CSE447', 'CSE448', 'CSE449', 'CSE442', 'CSE496',
        ],
        'pick': 3,
    },
    'Open Elective': {
        'credits': 3,
        'courses': [],  # Any course not assigned elsewhere
        'is_open': True,
    },
}

BSEEE_CATEGORIES = {
    'University Core - Languages': {
        'credits': 12,
        'courses': ['ENG102', 'ENG103', 'ENG111', 'BAN205'],
    },
    'University Core - Humanities': {
        'credits': 9,
        'courses': ['PHI104', 'HIS102', 'HIS103'],
    },
    'University Core - Social Sciences': {
        'credits': 9,
        'courses': ['ECO101', 'ECO104', 'POL101', 'POL104', 'SOC101', 'ANT101', 'ENV203', 'GEO205'],
        'pick': 3,
    },
    'University Core - Sciences': {
        'credits': 4,
        'courses': ['BIO103', 'PHY107', 'CHE101'],
        'pick': 1,
    },
    'SEPS Core': {
        'credits': 38,
        'courses': ['MAT116', 'MAT120', 'MAT130', 'MAT250', 'MAT125', 'MAT350', 'MAT361',
                     'PHY107', 'PHY108', 'CHE101', 'EEE452', 'CEE110', 'CSE115', 'CSE115L'],
    },
    'EEE Major Core': {
        'credits': 42,
        'courses': ['EEE141', 'EEE141L', 'EEE111', 'EEE111L', 'EEE211', 'EEE211L',
                     'EEE241', 'EEE241L', 'EEE221', 'EEE311', 'EEE311L', 'EEE361',
                     'EEE312', 'EEE312L', 'EEE321', 'EEE321L', 'EEE342', 'EEE342L',
                     'EEE362', 'EEE362L', 'EEE363', 'EEE363L'],
    },
    'Capstone': {
        'credits': 4,
        'courses': ['EEE299', 'EEE499A', 'EEE499B'],
    },
    'Elective Trails': {
        'credits': 9,
        'courses': [
            'EEE410', 'EEE411', 'EEE413', 'EEE414', 'EEE415', 'EEE491',
            'EEE461', 'EEE462', 'EEE464', 'EEE465', 'EEE468', 'EEE492',
            'EEE422', 'EEE424', 'EEE426', 'EEE427', 'EEE428', 'EEE493',
            'EEE453', 'EEE432', 'EEE433', 'EEE436', 'EEE494',
            'EEE331', 'EEE421', 'EEE423', 'EEE451', 'EEE471', 'EEE495',
        ],
        'pick': 3,
    },
    'Open Elective': {
        'credits': 3,
        'courses': [],
        'is_open': True,
    },
}

LLB_CATEGORIES = {
    'GED Group 1': {
        'credits': 16,
        'courses': ['ENG102', 'ENG103', 'BEN205', 'HIS103', 'PBH101', 'CHE101', 'PHY107', 'BIO103'],
        'required': ['ENG102', 'ENG103', 'BEN205', 'HIS103'],
        'science_pick': 1,
        'science_options': ['PBH101', 'CHE101', 'PHY107', 'BIO103'],
    },
    'GED Group 2': {
        'credits': 9,
        'courses': ['ECO101', 'ECO104', 'POL101', 'POL104', 'ENG111', 'PHI101', 'ENV203',
                     'GEO205', 'BUS112', 'SOC101', 'ANT101'],
        'pick': 3,
    },
    'Core Year 1': {
        'credits': 6,
        'courses': ['LLB101', 'LLB102'],
    },
    'Core Year 2': {
        'credits': 33,
        'courses': ['LLB103', 'LLB104', 'LLB201', 'LLB202', 'LLB203',
                     'LLB204', 'LLB205', 'LLB206', 'LLB207', 'LLB208', 'LLB209'],
    },
    'Core Year 3': {
        'credits': 21,
        'courses': ['LLB301', 'LLB302', 'LLB304', 'LLB306', 'LLB303', 'LLB305', 'LLB307'],
    },
    'Core Year 4': {
        'credits': 21,
        'courses': ['LLB401', 'LLB402', 'LLB403', 'LLB404', 'LLB405', 'LLB406', 'LLB407'],
    },
    'Electives': {
        'credits': 24,
        'courses': ['LLB411', 'LLB412', 'LLB413', 'LLB414', 'LLB415', 'LLB416', 'LLB417',
                     'LLB418', 'LLB419', 'LLB420', 'LLB421', 'LLB422', 'LLB423', 'LLB424',
                     'LLB425', 'LLB426', 'LLB427', 'LLB428', 'LLB429'],
        'pick': 8,
    },
}

PROGRAM_CATEGORIES = {
    'BSCSE': BSCSE_CATEGORIES,
    'BSEEE': BSEEE_CATEGORIES,
    'LLB': LLB_CATEGORIES,
}

PROGRAM_LABELS = {
    'BSCSE': 'BSc in Computer Science and Engineering',
    'BSEEE': 'BSc in Electrical and Electronic Engineering',
    'LLB': 'LL.B Honors',
}


# ─────────────────────────────────────────────────────────────────────
# PARSING
# ─────────────────────────────────────────────────────────────────────

def parse_transcript(filepath):
    """Parse a transcript CSV file. Returns (student_id, program, records)."""
    student_id = 'Unknown'
    program = None
    records = []

    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        for line in f:
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

    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        lines = [l for l in f if not l.strip().startswith('#')]
        reader = csv.DictReader(lines)
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
# CREDIT TALLY LOGIC
# ─────────────────────────────────────────────────────────────────────

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
        # Collect all invalid-grade attempts for display
        for attempt in attempts:
            if attempt['grade'] in INVALID_GRADE_LABELS:
                excluded.append((attempt, INVALID_GRADE_LABELS[attempt['grade']]))

    return resolved, retake_info, excluded


def compute_category_credits(resolved, program):
    """
    Compute earned credits per category for the given program.
    Courses may appear in multiple categories and satisfy all of them.
    Each course's credits are only counted ONCE toward total earned credits.
    """
    categories = PROGRAM_CATEGORIES.get(program, BSCSE_CATEGORIES)
    category_results = {}

    # Build a set of all codes that are in ANY named category
    all_categorized_codes = set()
    for cat_name, cat_info in categories.items():
        if not cat_info.get('is_open'):
            all_categorized_codes.update(cat_info['courses'])

    for cat_name, cat_info in categories.items():
        if cat_info.get('is_open'):
            # Open Elective: any completed course NOT in any named category
            earned = 0.0
            completed = []
            for code, record in resolved.items():
                if code not in all_categorized_codes and record['credits'] > 0:
                    earned += record['credits']
                    completed.append(record)
                    if earned >= cat_info['credits']:
                        break
            category_results[cat_name] = {
                'earned': min(earned, cat_info['credits']),
                'required': cat_info['credits'],
                'completed': completed,
                'complete': earned >= cat_info['credits'],
            }
            continue

        required_credits = cat_info['credits']
        cat_courses = cat_info['courses']
        pick = cat_info.get('pick', None)

        earned = 0.0
        completed = []

        for code in cat_courses:
            if code in resolved:
                earned += resolved[code]['credits']
                completed.append(resolved[code])
                if pick and len(completed) >= pick:
                    break

        category_results[cat_name] = {
            'earned': earned,
            'required': required_credits,
            'completed': completed,
            'complete': earned >= required_credits,
        }

    return category_results


# ─────────────────────────────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────────────────────────────

def format_credits(val):
    """Format credit value: integer if whole, else float."""
    return int(val) if val == int(val) else val


def print_output(student_id, program, filename, records, resolved, retake_info, excluded, category_results):
    """Print the Level 1 output in the exact box-drawing format."""
    program_label = PROGRAM_LABELS.get(program, program)

    total_attempted = len(records)
    valid_count = len(resolved)
    excluded_count = len(excluded)
    total_earned = sum(r['credits'] for r in resolved.values())

    print(f"=== NSU AUDIT CORE - LEVEL 1 ===")
    print(f"Student: {student_id}")
    print(f"Program: {program_label}")
    print(f"Processing: {filename}")
    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                     CREDIT ANALYSIS                          ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    print(f"Total Courses Attempted: {total_attempted}")
    print(f"Valid Courses (A-D): {valid_count}")
    print(f"Excluded Courses: {excluded_count}")

    for i, (rec, reason) in enumerate(excluded):
        cr = format_credits(rec['credits'])
        connector = "└─" if i == excluded_count - 1 else "├─"
        print(f"  {connector} {rec['code']} ({rec['grade']}) - {cr} credits [{reason}]")

    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                   CREDITS BY CATEGORY                        ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    if program == 'LLB':
        _print_llb_categories(category_results)
    else:
        _print_engineering_categories(category_results)

    total_required = 130
    earned_display = format_credits(total_earned)
    status = "✓ COMPLETE" if total_earned >= total_required else "⚠ IN PROGRESS"
    print(f"Total Earned Credits:  {earned_display} / {total_required} credits")
    print()
    print(f"RESULT: {status} ({earned_display} credits completed)")


def _print_engineering_categories(category_results):
    """Print credit breakdown for BSCSE/BSEEE programs."""
    for cat_name, info in category_results.items():
        earned = format_credits(info['earned'])
        required = format_credits(info['required'])
        status = "✓ COMPLETE" if info['complete'] else "⚠ IN PROGRESS"
        print(f"{cat_name + ':':30s} {earned:>3} / {required:>3} credits  {status}")
    print()


def _print_llb_categories(category_results):
    """Print credit breakdown for LL.B with year sub-breakdown."""
    for cat_name in ['GED Group 1', 'GED Group 2']:
        if cat_name in category_results:
            info = category_results[cat_name]
            earned = format_credits(info['earned'])
            required = format_credits(info['required'])
            status = "✓ COMPLETE" if info['complete'] else "⚠ IN PROGRESS"
            print(f"{cat_name + ':':30s} {earned:>3} / {required:>3} credits  {status}")

    core_years = ['Core Year 1', 'Core Year 2', 'Core Year 3', 'Core Year 4']
    total_core_earned = 0
    total_core_required = 0
    year_details = []
    for yr in core_years:
        if yr in category_results:
            info = category_results[yr]
            total_core_earned += info['earned']
            total_core_required += info['required']
            year_details.append((yr, info))

    core_complete = total_core_earned >= total_core_required
    ce = format_credits(total_core_earned)
    cr_req = format_credits(total_core_required)
    core_status = "✓ COMPLETE" if core_complete else "⚠ IN PROGRESS"
    print(f"{'Core Program:':30s} {ce:>3} / {cr_req:>3} credits  {core_status}")

    for i, (yr, info) in enumerate(year_details):
        earned = format_credits(info['earned'])
        required = format_credits(info['required'])
        yr_label = yr.replace('Core ', '')
        status_mark = "✓" if info['complete'] else f"⚠ (Missing {format_credits(required - earned)})"
        connector = "└─" if i == len(year_details) - 1 else "├─"
        print(f"  {connector} {yr_label + ':':22s} {earned:>3} / {required:>3} credits  {status_mark}")

    if 'Electives' in category_results:
        info = category_results['Electives']
        earned = format_credits(info['earned'])
        required = format_credits(info['required'])
        status = "✓ COMPLETE" if info['complete'] else "⚠ IN PROGRESS"
        print(f"{'Electives:':30s} {earned:>3} / {required:>3} credits  {status}")

    print()


# ─────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/level1_credit_tally.py <transcript.csv>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    filename = os.path.basename(filepath)
    student_id, program, records = parse_transcript(filepath)
    resolved, retake_info, excluded = resolve_retakes(records)
    category_results = compute_category_credits(resolved, program)
    print_output(student_id, program, filename, records, resolved, retake_info, excluded, category_results)


if __name__ == '__main__':
    main()
