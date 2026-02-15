#!/usr/bin/env python3
"""
NSU Audit Core - Level 1: Credit Tally Engine
Calculates total valid earned credits from student transcript.
Supports BSCSE, BSEEE, and LL.B Honors programs.
"""

import csv
import sys
from pathlib import Path


VALID_GRADES = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D'}
INVALID_GRADES = {'F', 'I', 'W', 'X'}

GED_GROUP1_REQUIRED = ['ENG102', 'ENG103', 'BEN205', 'HIS103']
GED_GROUP1_SCIENCE = ['PBH101', 'CHE101', 'PHY107', 'BIO103']
GED_GROUP2_OPTIONS = ['ECO101', 'ECO104', 'POL101', 'POL104', 'ENG111', 'PHI101', 
                      'ENV203', 'GEO205', 'BUS112', 'SOC101', 'ANT101']

LLB_CORE_YEAR1 = ['LLB101', 'LLB102']
LLB_CORE_YEAR2 = ['LLB103', 'LLB104', 'LLB201', 'LLB202', 'LLB203', 'LLB204', 
                  'LLB205', 'LLB206', 'LLB207', 'LLB208', 'LLB209']
LLB_CORE_YEAR3 = ['LLB301', 'LLB302', 'LLB303', 'LLB304', 'LLB305', 'LLB306', 'LLB307']
LLB_CORE_YEAR4 = ['LLB401', 'LLB402', 'LLB403', 'LLB404', 'LLB405', 'LLB406', 'LLB407']

LLB_ELECTIVES = [f'LLB41{i}' for i in range(1, 10)] + [f'LLB42{i}' for i in range(10)]


def detect_program(courses):
    """Auto-detect program from course codes."""
    has_llb = any('LLB' in c['course_code'] for c in courses)
    has_cse = any('CSE' in c['course_code'] for c in courses)
    has_eee = any('EEE' in c['course_code'] for c in courses)
    
    if has_llb:
        return 'LLB'
    elif has_cse:
        return 'BSCSE'
    elif has_eee:
        return 'BSEEE'
    else:
        return 'BSCSE'


def load_transcript(transcript_path):
    """Load transcript CSV and return list of course records."""
    courses = []
    with open(transcript_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            courses.append({
                'course_code': row['course_code'].strip(),
                'course_name': row.get('course_name', '').strip(),
                'credits': float(row['credits']),
                'grade': row['grade'].strip().upper(),
                'semester': row['semester'].strip()
            })
    return courses


def calculate_credits(courses):
    """Calculate earned credits excluding invalid grades and 0-credit labs."""
    total_earned = 0
    excluded_courses = []
    valid_courses_count = 0
    zero_credit_labs_completed = 0

    course_codes_seen = {}

    for course in courses:
        code = course['course_code']
        grade = course['grade']
        credits = course['credits']

        if grade in INVALID_GRADES:
            excluded_courses.append((code, grade, credits))
            continue

        if grade in VALID_GRADES:
            if code not in course_codes_seen:
                course_codes_seen[code] = []
            course_codes_seen[code].append((grade, credits))

    for code, attempts in course_codes_seen.items():
        best_attempt = max(attempts, key=lambda x: get_grade_points(x[0]))
        grade, credits = best_attempt

        if credits == 0:
            zero_credit_labs_completed += 1
        else:
            total_earned += credits
            valid_courses_count += 1

    return {
        'total_earned': total_earned,
        'valid_courses_count': valid_courses_count,
        'zero_credit_labs_completed': zero_credit_labs_completed,
        'excluded_courses': excluded_courses
    }


def validate_law_ged(courses):
    """Validate GED requirements for Law program."""
    course_codes = {c['course_code'] for c in courses if c['grade'] in VALID_GRADES}
    
    ged1_complete = True
    ged1_missing = []
    
    for req in GED_GROUP1_REQUIRED:
        if req not in course_codes:
            ged1_complete = False
            ged1_missing.append(req)
    
    science_count = sum(1 for s in GED_GROUP1_SCIENCE if s in course_codes)
    if science_count != 1:
        ged1_complete = False
        ged1_missing.append(f"Science course (need 1, have {science_count})")
    
    ged2_taken = [c for c in course_codes if c in GED_GROUP2_OPTIONS]
    
    alternatives = [('ECO101', 'ECO104'), ('POL101', 'POL104'), 
                     ('ENV203', 'GEO205'), ('SOC101', 'ANT101')]
    alt_violation = False
    for a1, a2 in alternatives:
        if a1 in ged2_taken and a2 in ged2_taken:
            alt_violation = True
            break
    
    ged2_complete = len(ged2_taken) == 3 and not alt_violation
    
    return {
        'ged1_complete': ged1_complete,
        'ged1_missing': ged1_missing,
        'ged1_credits': sum(4 if c in GED_GROUP1_SCIENCE else 3 
                           for c in course_codes if c in GED_GROUP1_REQUIRED + GED_GROUP1_SCIENCE),
        'ged2_complete': ged2_complete,
        'ged2_taken': ged2_taken,
        'ged2_credits': len(ged2_taken) * 3,
        'alt_violation': alt_violation
    }


def calculate_law_credits_by_category(courses):
    """Calculate Law program credits by category."""
    course_codes = {c['course_code'] for c in courses if c['grade'] in VALID_GRADES}
    
    ged1_credits = sum(4 if c in GED_GROUP1_SCIENCE else 3 
                       for c in course_codes if c in GED_GROUP1_REQUIRED + GED_GROUP1_SCIENCE)
    
    ged2_credits = sum(3 for c in course_codes if c in GED_GROUP2_OPTIONS)
    
    year1 = sum(3 for c in course_codes if c in LLB_CORE_YEAR1)
    year2 = sum(3 for c in course_codes if c in LLB_CORE_YEAR2)
    year3 = sum(3 for c in course_codes if c in LLB_CORE_YEAR3)
    year4 = sum(3 for c in course_codes if c in LLB_CORE_YEAR4)
    
    electives = sum(3 for c in course_codes if c.startswith('LLB41') or c.startswith('LLB42'))
    
    return {
        'ged1': ged1_credits,
        'ged2': ged2_credits,
        'year1': year1,
        'year2': year2,
        'year3': year3,
        'year4': year4,
        'electives': electives
    }


def get_grade_points(grade):
    """Map letter grade to grade points using NSU scale."""
    grade_map = {
        'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0,
        'F': 0.0, 'I': 0.0, 'W': 0.0, 'X': 0.0
    }
    return grade_map.get(grade, 0.0)


def generate_report(result, transcript_path, program='BSCSE'):
    """Generate formatted credit audit report."""
    print("=" * 50)
    print("=== NSU AUDIT CORE - LEVEL 1 ===")
    print("=== CREDIT TALLY ENGINE ===")
    print("=" * 50)
    print(f"Program: {program}")
    print(f"Processing: {transcript_path}")
    print()

    print("Credit Analysis:")
    print(f"  Valid Course Count (A-D): {result['valid_courses_count']}")
    print(f"  Excluded Courses (F/I/W/X): {len(result['excluded_courses'])}")

    if result['excluded_courses']:
        print("  Excluded Course Details:")
        for code, grade, credits in result['excluded_courses']:
            print(f"    - {code} ({grade}) - {credits} credits")

    print()
    
    if program == 'LLB':
        if 'law_ged' in result:
            ged = result['law_ged']
            print("GED Group 1 (16 credits required):")
            if ged['ged1_complete']:
                print(f"  ✓ Complete - {ged['ged1_credits']}/16 credits")
            else:
                print(f"  ✗ Incomplete - {ged['ged1_credits']}/16 credits")
                print(f"    Missing: {', '.join(ged['ged1_missing'])}")
            
            print()
            print("GED Group 2 (9 credits - choose 3):")
            if ged['ged2_complete']:
                print(f"  ✓ Complete - {ged['ged2_credits']}/9 credits")
            elif ged['alt_violation']:
                print(f"  ✗ Alternative course conflict!")
            else:
                print(f"  ✗ Incomplete - {ged['ged2_credits']}/9 credits")
                print(f"    Taken: {', '.join(ged['ged2_taken']) if ged['ged2_taken'] else 'None'}")
            
            print()
            print("Core Program Credits:")
            cat = result.get('law_categories', {})
            print(f"  Year 1: {cat.get('year1', 0)}/6 credits")
            print(f"  Year 2: {cat.get('year2', 0)}/27 credits")
            print(f"  Year 3: {cat.get('year3', 0)}/21 credits")
            print(f"  Year 4: {cat.get('year4', 0)}/27 credits")
            print(f"  Electives: {cat.get('electives', 0)}/24 credits")

    print()
    print(f"Total Earned Credits: {result['total_earned']}")
    print(f"0-Credit Labs Completed: {result['zero_credit_labs_completed']}")
    print()

    return result['total_earned']


def main():
    if len(sys.argv) < 2:
        print("Usage: python level1_credit_tally.py <transcript.csv> [program]")
        print("  program: BSCSE, BSEEE, or LLB (auto-detected if not specified)")
        sys.exit(1)

    transcript_path = sys.argv[1]
    program = sys.argv[2].upper() if len(sys.argv) > 2 else None

    if not Path(transcript_path).exists():
        print(f"Error: File not found: {transcript_path}")
        sys.exit(1)

    courses = load_transcript(transcript_path)
    
    if program is None:
        program = detect_program(courses)
    
    result = calculate_credits(courses)
    
    if program == 'LLB':
        result['law_ged'] = validate_law_ged(courses)
        result['law_categories'] = calculate_law_credits_by_category(courses)
    
    generate_report(result, transcript_path, program)


if __name__ == '__main__':
    main()
