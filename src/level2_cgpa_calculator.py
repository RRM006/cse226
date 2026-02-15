#!/usr/bin/env python3
"""
NSU Audit Core - Level 2: CGPA Calculator & Waiver Handler
Calculates weighted CGPA using NSU grading scale, handles retakes and waivers.
Supports BSCSE, BSEEE, and LL.B Honors programs.
"""

import csv
import sys
from pathlib import Path


GRADE_POINTS = {
    'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7,
    'D+': 1.3, 'D': 1.0,
    'F': 0.0, 'I': 0.0, 'W': 0.0, 'X': 0.0
}

CGPA_EXCLUDE_GRADES = {'F', 'I', 'W', 'X'}


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


def get_waivers_from_user():
    """Prompt admin for waiver information."""
    print("\nEnter waived courses (comma-separated course codes, or press Enter for NONE): ", end="")
    waiver_input = input().strip().upper()
    
    if not waiver_input or waiver_input.lower() == 'none':
        return set()
    
    return {code.strip() for code in waiver_input.split(',') if code.strip()}


def process_retakes(courses):
    """Identify retaken courses and return best grades only."""
    course_attempts = {}
    
    for course in courses:
        code = course['course_code']
        if code not in course_attempts:
            course_attempts[code] = []
        course_attempts[code].append(course)
    
    processed_courses = []
    retake_info = []
    
    for code, attempts in course_attempts.items():
        if len(attempts) == 1:
            processed_courses.append(attempts[0])
        else:
            best_attempt = max(attempts, key=lambda x: GRADE_POINTS.get(x['grade'], 0.0))
            processed_courses.append(best_attempt)
            
            grades = [(a['grade'], GRADE_POINTS.get(a['grade'], 0.0)) for a in attempts]
            retake_info.append({
                'code': code,
                'attempts': grades,
                'best_grade': best_attempt['grade'],
                'best_points': GRADE_POINTS.get(best_attempt['grade'], 0.0)
            })
    
    return processed_courses, retake_info


def calculate_cgpa(courses, waivers):
    """Calculate weighted CGPA excluding invalid grades and waived courses."""
    total_grade_points = 0.0
    total_credits = 0.0
    waiver_credits = 0
    
    for course in courses:
        code = course['course_code']
        grade = course['grade']
        credits = course['credits']
        
        if code in waivers:
            waiver_credits += credits
            continue
        
        if grade in CGPA_EXCLUDE_GRADES:
            continue
        
        grade_point = GRADE_POINTS.get(grade, 0.0)
        
        if credits > 0:
            total_grade_points += grade_point * credits
            total_credits += credits
    
    cgpa = round(total_grade_points / total_credits, 2) if total_credits > 0 else 0.0
    
    return {
        'cgpa': cgpa,
        'total_grade_points': round(total_grade_points, 2),
        'total_credits': total_credits,
        'waiver_credits': waiver_credits,
        'waivers': waivers
    }


def get_academic_standing(cgpa):
    """Determine academic standing based on CGPA."""
    if cgpa >= 3.80:
        return "Summa Cum Laude"
    elif cgpa >= 3.65:
        return "Magna Cum Laude"
    elif cgpa >= 3.50:
        return "Cum Laude"
    elif cgpa >= 3.00:
        return "First Class (Good Standing)"
    elif cgpa >= 2.50:
        return "Second Class (Good Standing)"
    elif cgpa >= 2.00:
        return "Third Class (Good Standing)"
    else:
        return "PROBATION - Not Eligible for Graduation"


def generate_report(result, retake_info, waivers, transcript_path, program='BSCSE'):
    """Generate formatted CGPA calculation report."""
    print("=" * 50)
    print("=== NSU AUDIT CORE - LEVEL 2 ===")
    print("=== CGPA CALCULATOR & WAIVER HANDLER ===")
    print("=" * 50)
    print(f"Program: {program}")
    print(f"Processing: {transcript_path}")
    
    if waivers:
        print(f"\nWaivers Applied: {len(waivers)} ({result['waiver_credits']} credits)")
        for code in sorted(waivers):
            print(f"  - {code}")
    
    if retake_info:
        print(f"\nRetaken Courses: {len(retake_info)}")
        for rt in retake_info:
            grades_str = " -> ".join([f"{g}({p})" for g, p in rt['attempts']])
            print(f"  - {rt['code']}: {grades_str} (used: {rt['best_grade']})")
    
    print("\nCGPA Calculation:")
    print(f"  Total Grade Points: {result['total_grade_points']}")
    print(f"  Total Credits Counted: {int(result['total_credits'])}")
    
    academic_standing = get_academic_standing(result['cgpa'])
    print(f"\nFinal CGPA: {result['cgpa']}")
    print(f"Academic Standing: {academic_standing}")
    
    return result['cgpa']


def main():
    if len(sys.argv) < 2:
        print("Usage: python level2_cgpa_calculator.py <transcript.csv> [program]")
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
    
    waivers = get_waivers_from_user()
    processed_courses, retake_info = process_retakes(courses)
    result = calculate_cgpa(processed_courses, waivers)
    generate_report(result, retake_info, waivers, transcript_path, program)


if __name__ == '__main__':
    main()
