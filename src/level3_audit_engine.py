#!/usr/bin/env python3
"""
NSU Audit Core - Level 3: Audit Engine & Deficiency Reporter
Compares student transcript against program requirements and generates audit report.
"""

import csv
import re
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


def load_transcript(transcript_path):
    """Load transcript CSV."""
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


def parse_program_knowledge(filepath):
    """Parse program knowledge markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    program = {
        'name': '',
        'total_credits': 130,
        'waivable_courses': set(),
        'university_core': [],
        'seps_core': [],
        'major_core': [],
        'capstone': [],
        'elective_trails': {},
        'open_elective': [],
        'prerequisites': {}
    }
    
    lines = content.split('\n')
    i = 0
    current_section = None
    current_trail = None
    
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('**Program Name:**'):
            program['name'] = line.split(':')[1].strip().replace('**', '')
        elif line.startswith('**Total Credits Required:**'):
            program['total_credits'] = int(line.split(':')[1].strip())
        elif line.startswith('**Waivable Courses:**'):
            waivables = line.split(':')[1].strip()
            program['waivable_courses'] = {c.strip() for c in waivables.split(',')}
        
        if line.startswith('## University Core'):
            current_section = 'university_core'
        elif line.startswith('## SEPS Core') or 'SEPS' in line:
            current_section = 'seps_core'
        elif line.startswith('## EEE Major Core') or line.startswith('## Major Core'):
            current_section = 'major_core'
        elif 'Capstone' in line:
            current_section = 'capstone'
        elif 'Elective Trails' in line or 'Specialized Elective' in line:
            current_section = 'elective_trails'
        elif 'Open Elective' in line:
            current_section = 'open_elective'
        elif 'Prerequisites' in line:
            current_section = 'prerequisites'
        
        if line.startswith('### ') and current_section == 'elective_trails':
            trail_name = line.replace('###', '').strip()
            current_trail = trail_name
            program['elective_trails'][current_trail] = []
        elif line.startswith('- ') and current_section and current_section != 'elective_trails':
            course_match = re.match(r'- ([A-Z]{2,}\d{3}[A-Z]?):\s*(.+?)\s*\((\d+)\s*credits?\)', line)
            if course_match:
                code = course_match.group(1)
                name = course_match.group(2)
                credits = int(course_match.group(3))
                course_entry = {'code': code, 'name': name, 'credits': credits}
                
                if current_section == 'elective_trails' and current_trail:
                    program['elective_trails'][current_trail].append(course_entry)
                elif current_section == 'university_core':
                    program['university_core'].append(course_entry)
                elif current_section == 'seps_core':
                    program['seps_core'].append(course_entry)
                elif current_section == 'major_core':
                    program['major_core'].append(course_entry)
                elif current_section == 'capstone':
                    program['capstone'].append(course_entry)
        
        if line.startswith('- ') and current_section == 'prerequisites':
            prereq_match = re.match(r'- ([A-Z]{2,}\d{3}):\s*Prerequisite:\s*(.+)', line)
            if prereq_match:
                code = prereq_match.group(1)
                prereq = prereq_match.group(2).strip()
                program['prerequisites'][code] = prereq
        
        i += 1
    
    return program


def process_transcript(courses):
    """Process transcript - handle retakes and map to categories."""
    course_attempts = {}
    for course in courses:
        code = course['course_code']
        if code not in course_attempts:
            course_attempts[code] = []
        course_attempts[code].append(course)
    
    completed_courses = {}
    for code, attempts in course_attempts.items():
        best = max(attempts, key=lambda x: GRADE_POINTS.get(x['grade'], 0.0))
        grade = best['grade']
        
        if grade not in CGPA_EXCLUDE_GRADES:
            completed_courses[code] = {
                'code': code,
                'name': best.get('course_name', code),
                'credits': best['credits'],
                'grade': grade,
                'grade_points': GRADE_POINTS.get(grade, 0.0)
            }
    
    return completed_courses


def calculate_cgpa(completed_courses):
    """Calculate CGPA from completed courses."""
    total_points = 0.0
    total_credits = 0
    
    for code, course in completed_courses.items():
        if course['credits'] > 0:
            total_points += course['grade_points'] * course['credits']
            total_credits += course['credits']
    
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0


def calculate_earned_credits(completed_courses):
    """Calculate total earned credits."""
    return sum(c['credits'] for c in completed_courses.values() if c['credits'] > 0)


def get_academic_standing(cgpa):
    """Determine academic standing."""
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
        return "PROBATION"


def get_waivers_from_user():
    """Prompt for waiver information."""
    print("\nEnter waived courses (comma-separated codes, or press Enter for NONE): ", end="")
    waiver_input = input().strip().upper()
    if not waiver_input or waiver_input.lower() == 'none':
        return set()
    return {code.strip() for code in waiver_input.split(',') if code.strip()}


def audit_program(program, completed_courses, cgpa, earned_credits, waivers):
    """Audit completed courses against program requirements."""
    deficiencies = {
        'missing_courses': [],
        'missing_credits': 0,
        'elective_trail_violation': False,
        'capstone_missing': [],
        'total_missing': 0
    }
    
    required_courses = []
    for c in program['university_core']:
        required_courses.append((c['code'], 'University Core', c['credits']))
    for c in program['seps_core']:
        required_courses.append((c['code'], 'SEPS Core', c['credits']))
    for c in program['major_core']:
        required_courses.append((c['code'], 'Major Core', c['credits']))
    
    for code, category, credits in required_courses:
        if code not in completed_courses and code not in waivers:
            deficiencies['missing_courses'].append({
                'code': code,
                'category': category,
                'credits': credits
            })
            deficiencies['missing_credits'] += credits
    
    capstone_codes = {c['code'] for c in program['capstone']}
    completed_capstone = {c for c in capstone_codes if c in completed_courses}
    for cap in program['capstone']:
        if cap['code'] not in completed_capstone:
            deficiencies['capstone_missing'].append(cap['code'])
    
    elective_courses = {}
    for trail_name, courses in program['elective_trails'].items():
        elective_courses[trail_name] = [c['code'] for c in courses]
    
    completed_electives = []
    for code in completed_courses:
        for trail_name, trail_codes in elective_courses.items():
            if code in trail_codes:
                completed_electives.append((code, trail_name))
                break
    
    if completed_electives:
        trail_counts = {}
        for code, trail in completed_electives:
            trail_counts[trail] = trail_counts.get(trail, 0) + 1
        
        max_trail = max(trail_counts.values()) if trail_counts else 0
        if max_trail < 2:
            deficiencies['elective_trail_violation'] = True
    
    deficiencies['total_missing'] = deficiencies['missing_credits']
    
    return deficiencies


def generate_audit_report(program, completed_courses, cgpa, earned_credits, deficiencies, transcript_path):
    """Generate comprehensive graduation audit report."""
    print("=" * 60)
    print("=== NSU AUDIT CORE - LEVEL 3 ===")
    print("=== GRADUATION AUDIT REPORT ===")
    print("=" * 60)
    print(f"Program: {program['name']}")
    print(f"Processing: {transcript_path}")
    print()
    
    standing = get_academic_standing(cgpa)
    print(f"Audit Results:")
    print(f"  Total Credits: {earned_credits} / {program['total_credits']} required")
    print(f"  CGPA: {cgpa}")
    print(f"  Academic Standing: {standing}")
    print()
    
    print("DEFICIENCIES FOUND:")
    
    if deficiencies['missing_courses']:
        print("\n  Missing Required Courses:")
        by_category = {}
        for mc in deficiencies['missing_courses']:
            cat = mc['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(mc)
        
        for cat, courses in by_category.items():
            print(f"    {cat}:")
            for c in courses:
                print(f"      - {c['code']} ({c['credits']} credits)")
    
    if deficiencies['elective_trail_violation']:
        print("\n  Elective Trail Requirement: VIOLATION")
        print("    Requirement: Minimum 2 courses (6 credits) from ONE trail")
        print("    Action: Take 1 more elective from existing trail")
    
    if deficiencies['capstone_missing']:
        print("\n  Missing Capstone Projects:")
        for cap in deficiencies['capstone_missing']:
            print(f"    - {cap}")
    
    print(f"\n  Total Missing Credits: {deficiencies['total_missing']}")
    print()
    
    is_eligible = (
        deficiencies['total_missing'] == 0 and
        not deficiencies['elective_trail_violation'] and
        not deficiencies['capstone_missing'] and
        cgpa >= 2.0
    )
    
    if is_eligible:
        print("GRADUATION STATUS: ✓ ELIGIBLE")
    else:
        print("GRADUATION STATUS: ✗ NOT ELIGIBLE")
        if cgpa < 2.0:
            print(f"  Reason: CGPA ({cgpa}) is below minimum requirement of 2.0")


def main():
    if len(sys.argv) < 3:
        print("Usage: python level3_audit_engine.py <transcript.csv> <program_knowledge.md>")
        sys.exit(1)

    transcript_path = sys.argv[1]
    program_path = sys.argv[2]

    if not Path(transcript_path).exists():
        print(f"Error: Transcript file not found: {transcript_path}")
        sys.exit(1)
    
    if not Path(program_path).exists():
        print(f"Error: Program knowledge file not found: {program_path}")
        sys.exit(1)

    courses = load_transcript(transcript_path)
    program = parse_program_knowledge(program_path)
    completed_courses = process_transcript(courses)
    cgpa = calculate_cgpa(completed_courses)
    earned_credits = calculate_earned_credits(completed_courses)
    waivers = get_waivers_from_user()
    
    deficiencies = audit_program(program, completed_courses, cgpa, earned_credits, waivers)
    generate_audit_report(program, completed_courses, cgpa, earned_credits, deficiencies, transcript_path)


if __name__ == '__main__':
    main()
