#!/usr/bin/env python3
"""
NSU Audit Core - Level 3: Audit Engine & Deficiency Reporter
Compares student transcript against program requirements and generates audit report.
Supports BSCSE, BSEEE, and LL.B Honors programs.
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
        'prerequisites': {},
        'is_law': False,
        'ged_group1': [],
        'ged_group2': [],
        'core_year1': [],
        'core_year2': [],
        'core_year3': [],
        'core_year4': [],
        'electives': []
    }
    
    lines = content.split('\n')
    i = 0
    current_section = None
    current_trail = None
    
    while i < len(lines):
        line = lines[i].strip()
        
        if 'LL.B' in line or 'LL.B Honors' in content:
            program['is_law'] = True
            
        if line.startswith('**Program Name:**'):
            program['name'] = line.split(':')[1].strip().replace('**', '')
        elif line.startswith('**Total Credits Required:**'):
            program['total_credits'] = int(line.split(':')[1].strip())
        elif line.startswith('**Waivable Courses:**'):
            waivables = line.split(':')[1].strip()
            program['waivable_courses'] = {c.strip() for c in waivables.split(',')}
        
        if program['is_law']:
            if 'GED Group 1' in line and 'Credits' in line:
                current_section = 'ged_group1'
            elif 'GED Group 2' in line and 'Credits' in line:
                current_section = 'ged_group2'
            elif 'Core Program Year 1' in line:
                current_section = 'core_year1'
            elif 'Core Program Year 2' in line:
                current_section = 'core_year2'
            elif 'Core Program Year 3' in line:
                current_section = 'core_year3'
            elif 'Core Program Year 4' in line:
                current_section = 'core_year4'
            elif 'Electives' in line and 'Credits' in line:
                current_section = 'electives'
            elif line.startswith('## '):
                current_section = None
        else:
            if line.startswith('## University Core'):
                current_section = 'university_core'
            elif 'SEPS' in line and 'Core' in line:
                current_section = 'seps_core'
            elif 'EEE Major Core' in line or line.startswith('## Major Core'):
                current_section = 'major_core'
            elif 'Capstone' in line:
                current_section = 'capstone'
            elif 'Elective Trails' in line or 'Specialized Elective' in line:
                current_section = 'elective_trails'
            elif 'Open Elective' in line:
                current_section = 'open_elective'
        
        if 'Prerequisites' in line and line.startswith('##'):
            current_section = 'prerequisites'
        
        if line.startswith('### ') and current_section == 'elective_trails':
            trail_name = line.replace('###', '').strip()
            current_trail = trail_name
            program['elective_trails'][current_trail] = []
        
        course_match = re.match(r'- ([A-Z]{2,}\d{3}[A-Z]?):\s*(.+?)\s*\((\d+)\s*credits?\)', line)
        if course_match:
            code = course_match.group(1)
            name = course_match.group(2)
            credits = int(course_match.group(3))
            course_entry = {'code': code, 'name': name, 'credits': credits}
            
            if program['is_law']:
                if current_section in ['ged_group1', 'ged_group2', 'core_year1', 'core_year2', 
                                       'core_year3', 'core_year4', 'electives']:
                    program[current_section].append(course_entry)
            else:
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


def audit_engineering_program(program, completed_courses, waivers):
    """Audit Engineering programs (BSCSE, BSEEE)."""
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


def audit_law_program(program, completed_courses, waivers):
    """Audit Law program (LL.B Honors)."""
    deficiencies = {
        'ged_group1_missing': [],
        'ged_group2_missing': False,
        'ged_group2_taken': [],
        'core_year1_missing': [],
        'core_year2_missing': [],
        'core_year3_missing': [],
        'core_year4_missing': [],
        'electives_missing': False,
        'electives_count': 0,
        'dissertation_missing': False,
        'missing_credits': 0,
        'total_missing': 0
    }
    
    ged_group1_required = [c['code'] for c in program['ged_group1'] 
                          if c['code'] in ['ENG102', 'ENG103', 'BEN205', 'HIS103']]
    ged_group1_science = ['BIO103', 'PHY107', 'CHE101', 'PBH101']
    
    for req in ged_group1_required:
        if req not in completed_courses and req not in waivers:
            deficiencies['ged_group1_missing'].append(req)
    
    science_count = sum(1 for s in ged_group1_science if s in completed_courses)
    if science_count < 1:
        deficiencies['ged_group1_missing'].append("Science course (need 1)")
    
    ged_group2_options = [c['code'] for c in program['ged_group2']]
    ged2_taken = [c for c in completed_courses if c in ged_group2_options]
    deficiencies['ged_group2_taken'] = ged2_taken
    
    if len(ged2_taken) < 3:
        deficiencies['ged_group2_missing'] = True
        deficiencies['missing_credits'] += (3 - len(ged2_taken)) * 3
    
    alternatives = [('ECO101', 'ECO104'), ('POL101', 'POL104')]
    for a1, a2 in alternatives:
        if a1 in ged2_taken and a2 in ged2_taken:
            deficiencies['ged_group2_missing'] = True
    
    for code in [c['code'] for c in program['core_year1']]:
        if code not in completed_courses and code not in waivers:
            deficiencies['core_year1_missing'].append(code)
            deficiencies['missing_credits'] += 3
    
    for code in [c['code'] for c in program['core_year2']]:
        if code not in completed_courses and code not in waivers:
            deficiencies['core_year2_missing'].append(code)
            deficiencies['missing_credits'] += 3
    
    for code in [c['code'] for c in program['core_year3']]:
        if code not in completed_courses and code not in waivers:
            deficiencies['core_year3_missing'].append(code)
            deficiencies['missing_credits'] += 3
    
    for code in [c['code'] for c in program['core_year4']]:
        if code not in completed_courses and code not in waivers:
            deficiencies['core_year4_missing'].append(code)
            deficiencies['missing_credits'] += 3
    
    llb_electives = [c['code'] for c in program['electives']]
    completed_electives = [c for c in completed_courses if c in llb_electives]
    deficiencies['electives_count'] = len(completed_electives)
    
    if len(completed_electives) < 8:
        deficiencies['electives_missing'] = True
        deficiencies['missing_credits'] += (8 - len(completed_electives)) * 3
    
    if 'LLB407' not in completed_courses:
        deficiencies['dissertation_missing'] = True
        deficiencies['missing_credits'] += 3
    
    deficiencies['total_missing'] = deficiencies['missing_credits']
    
    return deficiencies


def audit_program(program, completed_courses, cgpa, earned_credits, waivers):
    """Audit completed courses against program requirements."""
    if program.get('is_law'):
        return audit_law_program(program, completed_courses, waivers)
    else:
        return audit_engineering_program(program, completed_courses, waivers)


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
    
    if program.get('is_law'):
        print("DEFICIENCIES FOUND:")
        
        if deficiencies['ged_group1_missing']:
            print("\n  GED Group 1 Incomplete:")
            print(f"    Missing: {', '.join(deficiencies['ged_group1_missing'])}")
        
        if deficiencies['ged_group2_missing']:
            print("\n  GED Group 2 Incomplete:")
            print(f"    Taken: {len(deficiencies['ged_group2_taken'])}/3 courses")
            if deficiencies['ged_group2_taken']:
                print(f"    Courses: {', '.join(deficiencies['ged_group2_taken'])}")
        
        if deficiencies['core_year1_missing']:
            print(f"\n  Core Year 1 Missing: {len(deficiencies['core_year1_missing'])} courses")
        
        if deficiencies['core_year2_missing']:
            print(f"\n  Core Year 2 Missing: {len(deficiencies['core_year2_missing'])} courses")
        
        if deficiencies['core_year3_missing']:
            print(f"\n  Core Year 3 Missing: {len(deficiencies['core_year3_missing'])} courses")
        
        if deficiencies['core_year4_missing']:
            print(f"\n  Core Year 4 Missing: {len(deficiencies['core_year4_missing'])} courses")
            if 'LLB407' in deficiencies['core_year4_missing']:
                print("    *** LLB407 (Dissertation) REQUIRED ***")
        
        if deficiencies['electives_missing']:
            print(f"\n  Electives: {deficiencies['electives_count']}/8 required")
        
        if deficiencies['dissertation_missing']:
            print("\n  *** DISSERTATION (LLB407) REQUIRED FOR GRADUATION ***")
    else:
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
            print("    Requirement: Minimum 2 courses from ONE trail")
        
        if deficiencies['capstone_missing']:
            print("\n  Missing Capstone Projects:")
            for cap in deficiencies['capstone_missing']:
                print(f"    - {cap}")
    
    print(f"\n  Total Missing Credits: {deficiencies['total_missing']}")
    print()
    
    is_eligible = deficiencies['total_missing'] == 0 and cgpa >= 2.0
    
    if program.get('is_law'):
        is_eligible = is_eligible and not deficiencies['dissertation_missing']
    
    if is_eligible:
        print("GRADUATION STATUS: ✓ ELIGIBLE")
    else:
        print("GRADUATION STATUS: ✗ NOT ELIGIBLE")
        if cgpa < 2.0:
            print(f"  Reason: CGPA ({cgpa}) is below minimum requirement of 2.0")


def main():
    if len(sys.argv) < 3:
        print("Usage: python level3_audit_engine.py <transcript.csv> <program_knowledge.md> [program]")
        print("  program: BSCSE, BSEEE, or LLB (auto-detected if not specified)")
        sys.exit(1)

    transcript_path = sys.argv[1]
    program_path = sys.argv[2]
    program = sys.argv[3].upper() if len(sys.argv) > 3 else None

    if not Path(transcript_path).exists():
        print(f"Error: Transcript file not found: {transcript_path}")
        sys.exit(1)
    
    if not Path(program_path).exists():
        print(f"Error: Program knowledge file not found: {program_path}")
        sys.exit(1)

    courses = load_transcript(transcript_path)
    program_data = parse_program_knowledge(program_path)
    
    if program is None:
        program = detect_program(courses)
    
    completed_courses = process_transcript(courses)
    cgpa = calculate_cgpa(completed_courses)
    earned_credits = calculate_earned_credits(completed_courses)
    waivers = get_waivers_from_user()
    
    deficiencies = audit_program(program_data, completed_courses, cgpa, earned_credits, waivers)
    generate_audit_report(program_data, completed_courses, cgpa, earned_credits, deficiencies, transcript_path)


if __name__ == '__main__':
    main()
