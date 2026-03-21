#!/usr/bin/env python3
"""
NSU Audit Core - Department Transfer Handler
Handles students transferring between departments (e.g., CSE to LLB).
"""

from collections import defaultdict

PROGRAM_CATEGORIES = {
    'BSCSE': 'BSc in Computer Science and Engineering',
    'BSEEE': 'BSc in Electrical and Electronic Engineering',
    'LLB': 'LL.B Honors',
}

EQUIVALENT_COURSES = {
    ('BSCSE', 'LLB'): {
        'ENG102': 'ENG102',
        'ENG103': 'ENG103',
        'ENG111': 'ENG111',
        'PHI104': 'PHI101',
        'HIS102': 'HIS103',
        'HIS103': 'HIS103',
        'ECO101': 'ECO101',
        'POL101': 'POL101',
        'SOC101': 'SOC101',
    },
    ('BSEEE', 'LLB'): {
        'ENG102': 'ENG102',
        'ENG103': 'ENG103',
        'ENG111': 'ENG111',
        'PHI104': 'PHI101',
        'HIS102': 'HIS103',
        'HIS103': 'HIS103',
        'ECO101': 'ECO101',
        'POL101': 'POL101',
        'SOC101': 'SOC101',
    },
    ('LLB', 'BSCSE'): {},
    ('LLB', 'BSEEE'): {},
    ('BSCSE', 'BSEEE'): {
        'MAT116': 'MAT116',
        'MAT120': 'MAT120',
        'MAT130': 'MAT130',
        'PHY107': 'PHY107',
        'PHY108': 'PHY108',
        'CHE101': 'CHE101',
    },
    ('BSEEE', 'BSCSE'): {
        'MAT116': 'MAT116',
        'MAT120': 'MAT120',
        'MAT130': 'MAT130',
        'PHY107': 'PHY107',
        'PHY108': 'PHY108',
        'CHE101': 'CHE101',
    },
}

GED_COURSES = {
    'ENG102', 'ENG103', 'ENG111', 'BAN205', 'BEN205',
    'PHI104', 'PHI101', 'HIS102', 'HIS103',
    'ECO101', 'ECO104', 'POL101', 'POL104', 'SOC101', 'ANT101',
    'ENV203', 'GEO205', 'PBH101', 'PHY107', 'CHE101', 'BIO103',
}


def detect_transfer(records, target_program):
    """
    Detect if a student has transferred from another program.
    Returns (is_transfer, source_program, transferred_courses)
    """
    course_codes = [r['code'] for r in records]

    has_llb = any(c.startswith('LLB') for c in course_codes)
    has_cse = any(c.startswith('CSE2') or c.startswith('CSE3') or c.startswith('CSE4') for c in course_codes)
    has_eee = any(c.startswith('EEE2') or c.startswith('EEE3') or c.startswith('EEE4') for c in course_codes)

    if target_program == 'LLB':
        if has_cse or has_eee:
            source = 'BSCSE' if has_cse else 'BSEEE'
            return True, source, _get_transferred_courses(records, source, target_program)

    elif target_program in ('BSCSE', 'BSEEE'):
        if has_llb:
            return True, 'LLB', _get_transferred_courses(records, 'LLB', target_program)

    return False, None, []


def _get_transferred_courses(records, source_program, target_program):
    """Get courses that can be transferred from source to target program."""
    transferred = []

    key = (source_program, target_program)
    equivalent_map = EQUIVALENT_COURSES.get(key, {})

    for record in records:
        code = record['code']

        if code in equivalent_map:
            target_code = equivalent_map[code]
            transferred.append({
                'original_code': code,
                'target_code': target_code,
                'credits': record['credits'],
                'grade': record['grade'],
                'semester': record['semester'],
                'name': record['name'],
            })

        elif code in GED_COURSES and source_program == 'LLB' and target_program in ('BSCSE', 'BSEEE'):
            transferred.append({
                'original_code': code,
                'target_code': code,
                'credits': record['credits'],
                'grade': record['grade'],
                'semester': record['semester'],
                'name': record['name'],
                'is_ged': True,
            })

    return transferred


def create_transfer_report(records, target_program):
    """
    Create a comprehensive transfer report for a student.
    Accepts a list of parsed course records.
    """
    is_transfer, source_program, transferred_courses = detect_transfer(records, target_program)

    if not is_transfer:
        return None

    report = {
        'is_transfer': True,
        'source_program': source_program,
        'target_program': target_program,
        'source_label': PROGRAM_CATEGORIES.get(source_program, source_program),
        'target_label': PROGRAM_CATEGORIES.get(target_program, target_program),
        'transferred_courses': transferred_courses,
        'total_transferred_credits': sum(c['credits'] for c in transferred_courses),
    }

    return report


def print_transfer_report(report):
    """Print the transfer report in a formatted way."""
    if not report or not report['is_transfer']:
        return

    print()
    print("=" * 66)
    print("                   DEPARTMENT TRANSFER                         ")
    print("=" * 66)
    print()
    print(f"From: {report['source_label']}")
    print(f"To:   {report['target_label']}")
    print()
    print(f"Transferred Courses: {len(report['transferred_courses'])}")
    print(f"Total Transferred Credits: {report['total_transferred_credits']}")
    print()

    if report['transferred_courses']:
        for i, course in enumerate(report['transferred_courses']):
            connector = "L " if i == len(report['transferred_courses']) - 1 else "+ "
            target = course['target_code']
            original = course['original_code']
            if target != original:
                mapping = f" ({original} -> {target})"
            else:
                mapping = ""
            print(f"  {connector} {course['original_code']}: {course['name']} "
                  f"[{course['grade']}] ({course['credits']} cr){mapping}")

    print()
