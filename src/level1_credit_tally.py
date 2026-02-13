#!/usr/bin/env python3
"""
NSU Audit Core - Level 1: Credit Tally Engine
Calculates total valid earned credits from student transcript.
"""

import csv
import sys
from pathlib import Path


VALID_GRADES = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D'}
INVALID_GRADES = {'F', 'I', 'W', 'X'}


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


def generate_report(result, transcript_path):
    """Generate formatted credit audit report."""
    print("=" * 50)
    print("=== NSU AUDIT CORE - LEVEL 1 ===")
    print("=== CREDIT TALLY ENGINE ===")
    print("=" * 50)
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
    print(f"Total Earned Credits: {result['total_earned']}")
    print(f"0-Credit Labs Completed: {result['zero_credit_labs_completed']}")
    print()

    return result['total_earned']


def main():
    if len(sys.argv) < 2:
        print("Usage: python level1_credit_tally.py <transcript.csv>")
        sys.exit(1)

    transcript_path = sys.argv[1]

    if not Path(transcript_path).exists():
        print(f"Error: File not found: {transcript_path}")
        sys.exit(1)

    courses = load_transcript(transcript_path)
    result = calculate_credits(courses)
    generate_report(result, transcript_path)


if __name__ == '__main__':
    main()
