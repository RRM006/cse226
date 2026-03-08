#!/usr/bin/env python3
"""
NSU Audit Core - Level 3: Audit & Deficiency Reporter
Full graduation audit: loads program knowledge, compares transcript against
all requirements, handles retakes, verifies electives/prerequisites, and
produces a complete deficiency report with graduation eligibility verdict.
Usage: python src/level3_audit_engine.py <transcript.csv> <program_knowledge.md>
"""

import sys
import csv
import os
import re
import math
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

PROGRAM_LABELS = {
    'BSCSE': 'BSc in Computer Science and Engineering',
    'BSEEE': 'BSc in Electrical and Electronic Engineering',
    'LLB': 'LL.B Honors',
}

ALLOWED_WAIVERS = {
    'BSCSE': ['ENG102', 'MAT116'],
    'BSEEE': ['ENG102', 'MAT116'],
    'LLB': ['ENG102'],
}


# ─────────────────────────────────────────────────────────────────────
# PARSING — TRANSCRIPT
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
# PARSING — PROGRAM KNOWLEDGE FILE
# ─────────────────────────────────────────────────────────────────────

def parse_knowledge_content(content, program):
    """
    Parse a program_knowledge.md file content into a structured dict.
    Returns a dict with keys: categories, prerequisites, trails, capstone, graduation_reqs
    """
    knowledge = {
        'categories': {},       # cat_name -> {courses: [{code, name, credits}], required_credits, pick}
        'prerequisites': {},    # course_code -> prerequisite_code or description
        'trails': {},           # trail_name -> [course_codes]
        'capstone_courses': [], # [course_codes]
        'total_credits': 130,
        'min_cgpa': 2.0,
    }

    # Parse prerequisites
    prereq_pattern = re.compile(r'-\s+(\w+):\s+Prerequisite:\s+(.+)', re.IGNORECASE)
    for match in prereq_pattern.finditer(content):
        course = match.group(1).strip().upper()
        prereq = match.group(2).strip()
        if prereq.lower() != 'no prerequisite' and prereq.lower() != 'none':
            knowledge['prerequisites'][course] = prereq

    # Parse courses with credits: "- CODE: Name (N)" or "- **CODE: Name (N)**" pattern
    course_pattern = re.compile(r'-\s+\*{0,2}(\w+):\s+(.+?)\s+\((\d+(?:\.\d+)?)\)\*{0,2}')

    # Detect program type and parse categories accordingly
    if program == 'LLB':
        _parse_llb_knowledge(content, knowledge, course_pattern)
    elif program == 'BSEEE':
        _parse_bseee_knowledge(content, knowledge, course_pattern)
    else:
        _parse_bscse_knowledge(content, knowledge, course_pattern)

    return knowledge


def _parse_section_courses(content, section_header, course_pattern):
    """Extract courses from a section of the knowledge file."""
    courses = []
    # Find the section
    pattern = re.compile(re.escape(section_header) + r'(.*?)(?=\n#|\Z)', re.DOTALL | re.IGNORECASE)
    match = pattern.search(content)
    if match:
        section_text = match.group(1)
        for m in course_pattern.finditer(section_text):
            code = m.group(1).strip().upper()
            name = m.group(2).strip().rstrip(' –—-')
            try:
                credits = float(m.group(3))
            except ValueError:
                credits = 0.0
            courses.append({'code': code, 'name': name, 'credits': credits})
    return courses


def _parse_bscse_knowledge(content, knowledge, course_pattern):
    """Parse BSCSE-specific categories from knowledge file."""
    # University Core - Languages
    lang_courses = _extract_courses_between(content, 'Languages', 'Humanities', course_pattern)
    knowledge['categories']['University Core - Languages'] = {
        'courses': lang_courses, 'required_credits': 12,
    }

    # University Core - Humanities
    hum_courses = _extract_courses_between(content, 'Humanities', 'Social Sciences', course_pattern)
    knowledge['categories']['University Core - Humanities'] = {
        'courses': hum_courses, 'required_credits': 9,
    }

    # University Core - Social Sciences
    ss_courses = _extract_courses_between(content, 'Social Sciences', 'Sciences', course_pattern)
    knowledge['categories']['University Core - Social Sciences'] = {
        'courses': ss_courses, 'required_credits': 9, 'pick': 3,
    }

    # University Core - Sciences
    sci_courses = _extract_courses_between(content, '## Sciences', 'SEPS CORE', course_pattern)
    knowledge['categories']['University Core - Sciences'] = {
        'courses': sci_courses, 'required_credits': 4, 'pick': 1,
    }

    # SEPS Core
    seps_courses = _extract_courses_between(content, 'SEPS CORE', 'MAJOR CORE', course_pattern)
    knowledge['categories']['SEPS Core'] = {
        'courses': seps_courses, 'required_credits': 38,
    }

    # Major Core
    major_courses = _extract_courses_between(content, 'MAJOR CORE', 'CAPSTONE', course_pattern)
    knowledge['categories']['Major Core'] = {
        'courses': major_courses, 'required_credits': 42,
    }

    # Capstone
    cap_courses = _extract_courses_between(content, 'CAPSTONE', 'ELECTIVE TRAILS', course_pattern)
    knowledge['categories']['Capstone'] = {
        'courses': cap_courses, 'required_credits': 4,
    }
    knowledge['capstone_courses'] = [c['code'] for c in cap_courses]

    # Elective Trails
    trail_section = _get_section(content, 'ELECTIVE TRAILS', 'OPEN ELECTIVE')
    all_trail_courses = []
    trail_names = re.findall(r'##\s+(.*?Trail)', trail_section, re.IGNORECASE)
    for trail_name in trail_names:
        trail_courses = []
        # Find courses after trail name
        trail_start = trail_section.find(trail_name)
        if trail_start >= 0:
            remaining = trail_section[trail_start:]
            next_trail = re.search(r'\n##\s+', remaining[len(trail_name):])
            if next_trail:
                trail_text = remaining[:len(trail_name) + next_trail.start()]
            else:
                trail_text = remaining
            for m in course_pattern.finditer(trail_text):
                tc = {'code': m.group(1).upper(), 'name': m.group(2).strip(), 'credits': float(m.group(3))}
                trail_courses.append(tc)
            # Also find simple course code only format: "- CSE401 (3)"
            simple_pattern = re.compile(r'-\s+(\w+)\s+\((\d+)\)')
            for m in simple_pattern.finditer(trail_text):
                code = m.group(1).upper()
                if not any(tc['code'] == code for tc in trail_courses):
                    trail_courses.append({'code': code, 'name': code, 'credits': float(m.group(2))})

        knowledge['trails'][trail_name.strip()] = [c['code'] for c in trail_courses]
        all_trail_courses.extend(trail_courses)

    # Deduplicate trail courses
    seen = set()
    unique_trail = []
    for c in all_trail_courses:
        if c['code'] not in seen:
            unique_trail.append(c)
            seen.add(c['code'])

    knowledge['categories']['Elective Trails'] = {
        'courses': unique_trail, 'required_credits': 9, 'pick': 3,
    }

    # Open Elective
    knowledge['categories']['Open Elective'] = {
        'courses': [], 'required_credits': 3, 'is_open': True,
    }


def _parse_bseee_knowledge(content, knowledge, course_pattern):
    """Parse BSEEE-specific categories from knowledge file."""
    # University Core - Languages
    lang_courses = _extract_courses_between(content, 'Languages', 'Humanities', course_pattern)
    knowledge['categories']['University Core - Languages'] = {
        'courses': lang_courses, 'required_credits': 12,
    }

    # University Core - Humanities
    hum_courses = _extract_courses_between(content, 'Humanities', 'Social Sciences', course_pattern)
    knowledge['categories']['University Core - Humanities'] = {
        'courses': hum_courses, 'required_credits': 9,
    }

    # University Core - Social Sciences
    ss_courses = _extract_courses_between(content, 'Social Sciences', '## Science', course_pattern)
    knowledge['categories']['University Core - Social Sciences'] = {
        'courses': ss_courses, 'required_credits': 9, 'pick': 3,
    }

    # University Core - Sciences
    sci_courses = _extract_courses_between(content, '## Science', 'SEPS CORE', course_pattern)
    knowledge['categories']['University Core - Sciences'] = {
        'courses': sci_courses, 'required_credits': 4, 'pick': 1,
    }

    # SEPS Core
    seps_courses = _extract_courses_between(content, 'SEPS CORE', 'EEE MAJOR CORE', course_pattern)
    knowledge['categories']['SEPS Core'] = {
        'courses': seps_courses, 'required_credits': 38,
    }

    # EEE Major Core
    major_courses = _extract_courses_between(content, 'EEE MAJOR CORE', 'CAPSTONE', course_pattern)
    knowledge['categories']['EEE Major Core'] = {
        'courses': major_courses, 'required_credits': 42,
    }

    # Capstone
    cap_courses = _extract_courses_between(content, 'CAPSTONE', 'SPECIALIZED ELECTIVE', course_pattern)
    knowledge['categories']['Capstone'] = {
        'courses': cap_courses, 'required_credits': 4,
    }
    knowledge['capstone_courses'] = [c['code'] for c in cap_courses]

    # Elective Trails
    trail_section = _get_section(content, 'SPECIALIZED ELECTIVE', 'OPEN ELECTIVE')
    all_trail_courses = []
    trail_names = re.findall(r'##\s+Trail\s+\d+:\s*(.*)', trail_section, re.IGNORECASE)
    for trail_name in trail_names:
        trail_courses = []
        trail_start = trail_section.find(trail_name)
        if trail_start >= 0:
            remaining = trail_section[trail_start:]
            next_trail = re.search(r'\n##\s+', remaining[len(trail_name):])
            if next_trail:
                trail_text = remaining[:len(trail_name) + next_trail.start()]
            else:
                trail_text = remaining
            simple_pattern = re.compile(r'-\s+(\w+)\s+\((\d+)\)')
            for m in simple_pattern.finditer(trail_text):
                trail_courses.append({'code': m.group(1).upper(), 'name': m.group(1).upper(), 'credits': float(m.group(2))})
            for m in course_pattern.finditer(trail_text):
                code = m.group(1).upper()
                if not any(tc['code'] == code for tc in trail_courses):
                    trail_courses.append({'code': code, 'name': m.group(2).strip(), 'credits': float(m.group(3))})

        knowledge['trails'][trail_name.strip()] = [c['code'] for c in trail_courses]
        all_trail_courses.extend(trail_courses)

    seen = set()
    unique_trail = []
    for c in all_trail_courses:
        if c['code'] not in seen:
            unique_trail.append(c)
            seen.add(c['code'])

    knowledge['categories']['Elective Trails'] = {
        'courses': unique_trail, 'required_credits': 9, 'pick': 3,
    }

    knowledge['categories']['Open Elective'] = {
        'courses': [], 'required_credits': 3, 'is_open': True,
    }


def _parse_llb_knowledge(content, knowledge, course_pattern):
    """Parse LLB-specific categories from knowledge file."""
    # Use '### GED Group 1' to skip the Credit Distribution Summary table
    ged1_courses = _extract_courses_between(content, '### GED Group 1', '### GED Group 2', course_pattern)
    knowledge['categories']['GED Group 1'] = {
        'courses': ged1_courses, 'required_credits': 16,
        'required_codes': ['ENG102', 'ENG103', 'BEN205', 'HIS103'],
        'science_pick': 1,
        'science_options': ['PBH101', 'CHE101', 'PHY107', 'BIO103'],
    }

    ged2_courses = _extract_courses_between(content, '### GED Group 2', '## Core Program', course_pattern)
    knowledge['categories']['GED Group 2'] = {
        'courses': ged2_courses, 'required_credits': 9, 'pick': 3,
    }

    # Core years: scope to "## Core Program Courses" section to avoid
    # matching year headers in the Semester-Wise Recommended Schedule
    core_section = _get_section(content, '## Core Program Courses', '## Elective Courses')

    y1_courses = _extract_courses_between(core_section, '### Year 1', '### Year 2', course_pattern)
    knowledge['categories']['Core Year 1'] = {
        'courses': y1_courses, 'required_credits': 6,
    }

    y2_courses = _extract_courses_between(core_section, '### Year 2', '### Year 3', course_pattern)
    knowledge['categories']['Core Year 2'] = {
        'courses': y2_courses, 'required_credits': 33,
    }

    y3_courses = _extract_courses_between(core_section, '### Year 3', '### Year 4', course_pattern)
    knowledge['categories']['Core Year 3'] = {
        'courses': y3_courses, 'required_credits': 21,
    }

    y4_courses = _extract_courses_between(core_section, '### Year 4', 'Validation', course_pattern)
    knowledge['categories']['Core Year 4'] = {
        'courses': y4_courses, 'required_credits': 21,
    }
    knowledge['capstone_courses'] = ['LLB407']

    # Electives: use numbered format "1. LLB411: Name (3)"
    elec_courses = _extract_courses_between(content, '## Elective Courses', '## Prerequisite', course_pattern)
    num_pattern = re.compile(r'\d+\.\s+(\w+):\s+(.+?)\s+\((\d+)\)')
    elec_section = _get_section(content, '## Elective Courses', '## Prerequisite')
    for m in num_pattern.finditer(elec_section):
        code = m.group(1).upper()
        if not any(c['code'] == code for c in elec_courses):
            elec_courses.append({'code': code, 'name': m.group(2).strip(), 'credits': float(m.group(3))})

    knowledge['categories']['Electives'] = {
        'courses': elec_courses, 'required_credits': 24, 'pick': 8,
    }


def _extract_courses_between(content, start_marker, end_marker, course_pattern):
    """Extract courses from content between two markers."""
    section = _get_section(content, start_marker, end_marker)
    courses = []
    for m in course_pattern.finditer(section):
        code = m.group(1).strip().upper()
        name = m.group(2).strip().rstrip(' –—-')
        try:
            credits = float(m.group(3))
        except ValueError:
            credits = 0.0
        courses.append({'code': code, 'name': name, 'credits': credits})
    return courses


def _get_section(content, start_marker, end_marker):
    """Get text between two markers in the content."""
    start = content.find(start_marker)
    if start < 0:
        # Try case-insensitive
        lower = content.lower()
        start = lower.find(start_marker.lower())
    if start < 0:
        return ''

    end = content.find(end_marker, start + len(start_marker))
    if end < 0:
        lower = content.lower()
        end = lower.find(end_marker.lower(), start + len(start_marker))
    if end < 0:
        return content[start:]

    return content[start:end]


# ─────────────────────────────────────────────────────────────────────
# RETAKE & CGPA LOGIC
# ─────────────────────────────────────────────────────────────────────

def resolve_retakes(records):
    """Resolve retakes: group by code, find best valid grade."""
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


def calculate_cgpa(resolved, waivers=None):
    """Calculate CGPA from resolved courses (only A-D, exclude waivers)."""
    if waivers is None:
        waivers = []
    total_points = 0.0
    total_credits = 0.0

    for code, record in resolved.items():
        if code in waivers:
            continue
        grade = record['grade']
        credits = record['credits']
        if grade not in VALID_GRADES or credits == 0:
            continue
        total_points += GRADE_POINTS[grade] * credits
        total_credits += credits

    if total_credits == 0:
        return 0.0, total_points, total_credits
    return total_points / total_credits, total_points, total_credits


def get_standing(cgpa):
    """Determine academic standing from CGPA."""
    if cgpa >= 3.80: return 'Summa Cum Laude'
    if cgpa >= 3.65: return 'Magna Cum Laude'
    if cgpa >= 3.50: return 'Cum Laude'
    if cgpa >= 3.00: return 'First Class (Good Standing)'
    if cgpa >= 2.50: return 'Second Class (Good Standing)'
    if cgpa >= 2.00: return 'Third Class (Good Standing)'
    return 'PROBATION'


# ─────────────────────────────────────────────────────────────────────
# SEMESTER ORDERING
# ─────────────────────────────────────────────────────────────────────

SEMESTER_ORDER = {'SPRING': 0, 'SUMMER': 1, 'FALL': 2}

def parse_semester(semester_str):
    """Parse semester string into (year, term_order) for comparison."""
    s = semester_str.upper()
    year_match = re.search(r'(\d{4})', s)
    year = int(year_match.group(1)) if year_match else 0

    term_order = 0
    for term, order in SEMESTER_ORDER.items():
        if term in s:
            term_order = order
            break

    return (year, term_order)


def semester_before(sem_a, sem_b):
    """Check if semester A is before or same as semester B (concurrent enrollment allowed)."""
    return parse_semester(sem_a) <= parse_semester(sem_b)


# ─────────────────────────────────────────────────────────────────────
# AUDIT ENGINE
# ─────────────────────────────────────────────────────────────────────

def run_audit(resolved, retake_info, knowledge, program, records, waivers=None):
    """
    Run the full graduation audit.
    Returns an audit_result dict with all analysis data.
    """
    if waivers is None:
        waivers = []

    categories = knowledge['categories']
    prerequisites = knowledge['prerequisites']
    capstone_courses = knowledge['capstone_courses']

    # Build course name lookup from knowledge and transcript
    course_names = {}
    for cat_info in categories.values():
        for c in cat_info.get('courses', []):
            course_names[c['code']] = c['name']
    for r in records:
        if r['code'] not in course_names:
            course_names[r['code']] = r['name']

    # Build course credits lookup from knowledge
    course_credits = {}
    for cat_info in categories.values():
        for c in cat_info.get('courses', []):
            course_credits[c['code']] = c['credits']
    for r in records:
        if r['code'] not in course_credits:
            course_credits[r['code']] = r['credits']

    # All categorized course codes (for Open Elective detection)
    all_categorized = set()
    for cat_info in categories.values():
        if not cat_info.get('is_open'):
            for c in cat_info.get('courses', []):
                all_categorized.add(c['code'])

    # ── Per-category analysis ──
    category_analysis = {}
    all_missing = []
    all_incomplete = []

    for cat_name, cat_info in categories.items():
        if cat_info.get('is_open'):
            # Open Elective
            open_earned = 0.0
            open_completed = []
            for code, record in resolved.items():
                if code not in all_categorized and record['credits'] > 0:
                    open_earned += record['credits']
                    open_completed.append(code)
                    if open_earned >= cat_info['required_credits']:
                        break
            category_analysis[cat_name] = {
                'required_credits': cat_info['required_credits'],
                'earned_credits': min(open_earned, cat_info['required_credits']),
                'complete': open_earned >= cat_info['required_credits'],
                'completed_courses': open_completed,
                'missing_courses': [],
            }
            if open_earned < cat_info['required_credits']:
                all_missing.append({
                    'code': 'OPEN_ELECTIVE',
                    'name': 'Open Elective Course',
                    'credits': cat_info['required_credits'] - open_earned,
                    'category': cat_name,
                })
            continue

        cat_courses = cat_info.get('courses', [])
        pick = cat_info.get('pick', None)
        required_credits = cat_info['required_credits']

        # Handle science_pick for GED Group 1 (mix of required + pick-N science)
        science_options = set(cat_info.get('science_options', []))
        science_pick = cat_info.get('science_pick', 0)

        completed = []
        missing = []
        incomplete = []

        science_completed = 0

        for c in cat_courses:
            code = c['code']
            is_science = code in science_options
            if code in waivers:
                completed.append(code)
                if is_science:
                    science_completed += 1
                continue
            if code in resolved:
                completed.append(code)
                if is_science:
                    science_completed += 1
            elif code in retake_info:
                if code not in resolved:
                    incomplete.append(c)
                    all_incomplete.append({**c, 'category': cat_name})
            else:
                # Never attempted
                if is_science:
                    # Don't mark as missing yet; handle after loop
                    pass
                elif pick is None:
                    missing.append(c)
                    all_missing.append({**c, 'category': cat_name})

        # Handle science pick-N shortfall
        if science_options and science_completed < science_pick:
            needed = science_pick - science_completed
            for c in cat_courses:
                if c['code'] in science_options and c['code'] not in completed:
                    if needed > 0:
                        missing.append(c)
                        all_missing.append({**c, 'category': cat_name})
                        needed -= 1
                    if needed <= 0:
                        break

        # For pick-type categories, check if enough were completed
        if pick is not None:
            if len(completed) < pick:
                needed = pick - len(completed)
                for c in cat_courses:
                    if c['code'] not in completed and c['code'] not in [ic['code'] for ic in incomplete]:
                        if needed > 0:
                            missing.append(c)
                            all_missing.append({**c, 'category': cat_name})
                            needed -= 1
                        if needed <= 0:
                            break

        earned_credits = sum(
            resolved[code]['credits'] if code in resolved
            else (course_credits.get(code, 0) if code in waivers else 0)
            for code in completed
        )

        category_analysis[cat_name] = {
            'required_credits': required_credits,
            'earned_credits': earned_credits,
            'complete': earned_credits >= required_credits if pick is None else len(completed) >= (pick or len(cat_courses)),
            'completed_courses': completed,
            'missing_courses': missing,
            'incomplete_courses': incomplete,
        }

    # ── Retake analysis ──
    retake_analysis = []
    for code, attempts in retake_info.items():
        entry = {
            'code': code,
            'name': course_names.get(code, code),
            'attempts': len(attempts),
            'grades': [a['grade'] for a in attempts],
            'semesters': [a['semester'] for a in attempts],
            'resolved': code in resolved,
            'best_grade': resolved[code]['grade'] if code in resolved else None,
        }
        retake_analysis.append(entry)

    # ── Prerequisite check ──
    prereq_violations = []
    # Build semester map for completed courses
    course_semesters = {}
    for r in records:
        if r['grade'] in VALID_GRADES:
            code = r['code']
            if code not in course_semesters or parse_semester(r['semester']) < parse_semester(course_semesters[code]):
                course_semesters[code] = r['semester']

    for course, prereq_raw in prerequisites.items():
        if course not in resolved:
            continue
        # Parse prerequisite (could be a course code or description)
        prereq_code = prereq_raw.strip().upper()
        # Handle "Completion of N credits" type
        credit_match = re.match(r'COMPLETION OF (\d+) CREDITS', prereq_code, re.IGNORECASE)
        if credit_match:
            continue  # Skip credit-based prerequisites for now

        # Check if prerequisite was completed before the course
        if prereq_code in course_semesters and course in course_semesters:
            if not semester_before(course_semesters[prereq_code], course_semesters[course]):
                prereq_violations.append({
                    'course': course,
                    'course_name': course_names.get(course, course),
                    'prerequisite': prereq_code,
                    'prereq_name': course_names.get(prereq_code, prereq_code),
                    'course_semester': course_semesters[course],
                    'prereq_semester': course_semesters.get(prereq_code, 'N/A'),
                    'prereq_completed': prereq_code in resolved,
                })
        elif prereq_code not in resolved and prereq_code not in waivers:
            # Prerequisite was never completed
            if course in resolved:
                prereq_violations.append({
                    'course': course,
                    'course_name': course_names.get(course, course),
                    'prerequisite': prereq_code,
                    'prereq_name': course_names.get(prereq_code, prereq_code),
                    'course_semester': course_semesters.get(course, 'N/A'),
                    'prereq_semester': 'NOT TAKEN',
                    'prereq_completed': False,
                })

    # ── Capstone check ──
    missing_capstone = []
    for cap in capstone_courses:
        if cap not in resolved:
            missing_capstone.append({
                'code': cap,
                'name': course_names.get(cap, cap),
                'credits': course_credits.get(cap, 0),
            })

    # ── Elective trail validation ──
    trail_result = None
    if knowledge['trails'] and program != 'LLB':
        trail_result = _check_trail_requirement(resolved, knowledge['trails'])

    # ── Missing 0-credit labs ──
    missing_labs = []
    for cat_info in categories.values():
        for c in cat_info.get('courses', []):
            if c['credits'] == 0 and c['code'] not in resolved:
                missing_labs.append(c)

    # ── Total credits ──
    total_earned = sum(r['credits'] for r in resolved.values())
    # Add waived credits
    for w in waivers:
        if w not in resolved:
            total_earned += course_credits.get(w, 0)

    # ── CGPA ──
    cgpa, total_points, total_credits_counted = calculate_cgpa(resolved, waivers)
    standing = get_standing(cgpa)

    # ── Graduation eligibility ──
    reasons_not_eligible = []
    total_missing = len(all_missing) + len(all_incomplete)

    if total_earned < 130:
        reasons_not_eligible.append(f"Insufficient credits ({format_credits(total_earned)} / 130)")
    if cgpa < 2.0:
        reasons_not_eligible.append(f"CGPA below minimum ({cgpa:.2f} < 2.00) — PROBATION")
    if missing_capstone:
        for cap in missing_capstone:
            reasons_not_eligible.append(f"Missing capstone: {cap['code']} ({cap['name']})")
    if all_missing:
        missing_cr = sum(m.get('credits', 0) for m in all_missing)
        reasons_not_eligible.append(f"Missing {len(all_missing)} required course(s) ({format_credits(missing_cr)} credits)")
    if all_incomplete:
        reasons_not_eligible.append(f"{len(all_incomplete)} course(s) attempted but not passed")

    eligible = len(reasons_not_eligible) == 0

    return {
        'category_analysis': category_analysis,
        'retake_analysis': retake_analysis,
        'prereq_violations': prereq_violations,
        'missing_capstone': missing_capstone,
        'trail_result': trail_result,
        'missing_labs': missing_labs,
        'all_missing': all_missing,
        'all_incomplete': all_incomplete,
        'total_earned': total_earned,
        'cgpa': cgpa,
        'standing': standing,
        'eligible': eligible,
        'reasons': reasons_not_eligible,
        'course_names': course_names,
        'course_credits': course_credits,
    }


def _check_trail_requirement(resolved, trails):
    """Check if elective trail requirement is met (min 2 from one trail)."""
    best_trail = None
    best_count = 0
    trail_details = {}

    for trail_name, trail_codes in trails.items():
        completed = [c for c in trail_codes if c in resolved]
        trail_details[trail_name] = completed
        if len(completed) > best_count:
            best_count = len(completed)
            best_trail = trail_name

    return {
        'satisfied': best_count >= 2,
        'best_trail': best_trail,
        'best_count': best_count,
        'details': trail_details,
    }


# ─────────────────────────────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────────────────────────────

def format_credits(val):
    """Format credit value: integer if whole, else float."""
    if isinstance(val, float) and val == int(val):
        return int(val)
    return val


def print_audit_output(student_id, program, filename, knowledge_file, audit, knowledge):
    """Print the Level 3 output in the exact box-drawing format."""
    program_label = PROGRAM_LABELS.get(program, program)

    print(f"=== NSU AUDIT CORE - LEVEL 3 ===")
    print(f"Student: {student_id}")
    print(f"Program: {program_label}")
    print(f"Processing: {filename}")
    print(f"Knowledge Base: {knowledge_file}")
    print()

    # ── GRADUATION AUDIT HEADER ──
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                    GRADUATION AUDIT                          ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    print(f"Credits:          {format_credits(audit['total_earned'])} / 130 required")
    print(f"CGPA:             {audit['cgpa']:.2f}")
    print(f"Standing:         {audit['standing']}")

    # Probation warning
    if audit['cgpa'] < 2.0:
        print()
        print("  ⚠⚠⚠ WARNING: STUDENT IS ON ACADEMIC PROBATION (CGPA < 2.00) ⚠⚠⚠")

    print()

    # ── REQUIREMENT ANALYSIS ──
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                   REQUIREMENT ANALYSIS                       ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    if program == 'LLB':
        _print_llb_requirements(audit)
    else:
        _print_engineering_requirements(audit, program)

    # ── Retake History ──
    if audit['retake_analysis']:
        print()
        print(f"Retake History: {len(audit['retake_analysis'])} course(s)")
        for i, r in enumerate(audit['retake_analysis']):
            status = "✅ RESOLVED" if r['resolved'] else "❌ STILL DEFICIENT"
            connector = "└─" if i == len(audit['retake_analysis']) - 1 else "├─"
            grade_history = " → ".join(r['grades'])
            best = f" (Best: {r['best_grade']})" if r['best_grade'] else ""
            print(f"  {connector} {r['code']}: {r['name']}")
            print(f"      Attempts: {r['attempts']} | Grades: {grade_history}{best} | {status}")

    # ── Prerequisite Violations ──
    if audit['prereq_violations']:
        print()
        print(f"⚠ Prerequisite Violations: {len(audit['prereq_violations'])}")
        for i, pv in enumerate(audit['prereq_violations']):
            connector = "└─" if i == len(audit['prereq_violations']) - 1 else "├─"
            prereq_status = "✓ Complete" if pv['prereq_completed'] else "❌ Missing"
            print(f"  {connector} {pv['course']} ({pv['course_name']}) taken in {pv['course_semester']}")
            print(f"      Prerequisite: {pv['prerequisite']} ({pv['prereq_name']}) — {prereq_status}")

    print()

    # ── DEFICIENCY REPORT ──
    all_deficient = audit['all_missing'] + audit['all_incomplete']
    missing_specific_labs = [l for l in audit['missing_labs']
                            if not any(m['code'] == l['code'] for m in all_deficient)]
    all_deficient.extend([{**l, 'category': 'Required Labs'} for l in missing_specific_labs])

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                   DEFICIENCY REPORT                          ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    total_missing_cr = sum(d.get('credits', 0) for d in all_deficient)
    print(f"Missing Courses: {len(all_deficient)} ({format_credits(total_missing_cr)} credits)")
    print()

    if all_deficient:
        # Group by category
        by_category = defaultdict(list)
        for d in all_deficient:
            by_category[d.get('category', 'Other')].append(d)

        for cat, items in by_category.items():
            print(f"{cat}:")
            for j, item in enumerate(items, 1):
                cr = format_credits(item.get('credits', 0))
                capstone_tag = " [CAPSTONE - REQUIRED]" if item['code'] in audit.get('missing_capstone_codes', set()) else ""
                print(f"  {j}. {item['code']}: {item.get('name', item['code'])} ({cr} cr){capstone_tag}")

                # Prerequisite info
                prereqs = knowledge['prerequisites']
                if item['code'] in prereqs:
                    prereq = prereqs[item['code']]
                    prereq_done = prereq.upper() in [c.upper() for c in audit['category_analysis'].get('_resolved_codes', [])]
                    # Check if prereq is in resolved
                    prereq_status = "✓ Complete" if any(
                        r['code'] == prereq.upper() for cat_a in audit['category_analysis'].values()
                        for r_code in cat_a.get('completed_courses', [])
                        for r in [{'code': r_code}]
                    ) else "❌ Missing"
                    print(f"       └─ Prerequisite: {prereq} ({prereq_status})")
            print()

    # ── ACTION ITEMS ──
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                   ACTION ITEMS                               ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    if all_deficient:
        print("To graduate, you must:")
        for j, item in enumerate(all_deficient, 1):
            cr = format_credits(item.get('credits', 0))
            tag = " [REQUIRED]" if item['code'] in knowledge['capstone_courses'] else ""
            print(f"  {j}. Complete {item['code']} ({cr} credits){tag}")

        credits_needed = total_missing_cr
        if audit['total_earned'] < 130:
            credits_needed = max(credits_needed, 130 - audit['total_earned'])

        print()
        print(f"Total credits needed: {format_credits(credits_needed)}")
        semesters = max(1, math.ceil(len(all_deficient) / 6))
        print(f"Estimated completion: {semesters} semester(s)")
    else:
        print("No action items — all requirements met!")

    if audit['cgpa'] < 2.0:
        print()
        print("  ⚠ CRITICAL: Raise CGPA above 2.00 to be eligible for graduation")

    print()

    # ── GRADUATION ELIGIBILITY ──
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                  GRADUATION ELIGIBILITY                      ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    if audit['eligible']:
        print("RESULT: ✅ ELIGIBLE FOR GRADUATION")
        print()
        print("Status: Congratulations! All graduation requirements have been met.")
    else:
        print("RESULT: ❌ NOT ELIGIBLE FOR GRADUATION")
        print()
        print("Reasons:")
        for i, reason in enumerate(audit['reasons']):
            connector = "└─" if i == len(audit['reasons']) - 1 else "├─"
            print(f"  {connector} {reason}")
        print()
        print("Status: Continue enrollment to complete remaining requirements.")


def _print_engineering_requirements(audit, program):
    """Print requirement analysis for BSCSE/BSEEE."""
    for cat_name, analysis in audit['category_analysis'].items():
        earned = format_credits(analysis['earned_credits'])
        required = format_credits(analysis['required_credits'])
        status = "✓ COMPLETE" if analysis['complete'] else "⚠ INCOMPLETE"
        suffix = f" ({earned} / {required})" if not analysis['complete'] else ""
        print(f"{cat_name + ':':30s} {status}{suffix}")

        if analysis.get('missing_courses'):
            print("  Missing:")
            for i, m in enumerate(analysis['missing_courses']):
                connector = "└─" if i == len(analysis['missing_courses']) - 1 else "├─"
                cr = format_credits(m.get('credits', 0))
                print(f"    {connector} {m['code']}: {m.get('name', m['code'])} ({cr} cr)")

    # Trail result
    if audit['trail_result']:
        tr = audit['trail_result']
        trail_status = "✓ SATISFIED" if tr['satisfied'] else "⚠ NOT SATISFIED"
        print(f"\n  Trail Requirement: {trail_status}")
        if tr['best_trail']:
            print(f"    Best trail: {tr['best_trail']} ({tr['best_count']} courses)")

    print()


def _print_llb_requirements(audit):
    """Print requirement analysis for LL.B with year sub-breakdown."""
    cat_analysis = audit['category_analysis']

    for cat_name in ['GED Group 1', 'GED Group 2']:
        if cat_name in cat_analysis:
            a = cat_analysis[cat_name]
            status = "✓ COMPLETE" if a['complete'] else "⚠ INCOMPLETE"
            earned = format_credits(a['earned_credits'])
            required = format_credits(a['required_credits'])
            suffix = f" ({earned} / {required})" if not a['complete'] else ""
            print(f"  {'├─' if cat_name == 'GED Group 1' else '└─'} {cat_name} ({required} cr):   {status}{suffix}")

    # Core Program with year breakdown
    core_years = ['Core Year 1', 'Core Year 2', 'Core Year 3', 'Core Year 4']
    total_ce = sum(cat_analysis.get(yr, {}).get('earned_credits', 0) for yr in core_years)
    total_cr = sum(cat_analysis.get(yr, {}).get('required_credits', 0) for yr in core_years)
    core_ok = total_ce >= total_cr
    core_status = "✓ COMPLETE" if core_ok else f"⚠ INCOMPLETE ({format_credits(total_ce)} / {format_credits(total_cr)})"
    print(f"\nCore Program ({format_credits(total_cr)} cr):   {core_status}")

    for i, yr in enumerate(core_years):
        if yr in cat_analysis:
            a = cat_analysis[yr]
            earned = format_credits(a['earned_credits'])
            required = format_credits(a['required_credits'])
            status = "✓ COMPLETE" if a['complete'] else f"⚠ INCOMPLETE ({earned} / {required})"
            connector = "└─" if i == len(core_years) - 1 else "├─"
            label = yr.replace('Core ', '')
            print(f"  {connector} {label} ({required} cr):     {status}")

            if a.get('missing_courses'):
                print("      Missing:")
                for j, m in enumerate(a['missing_courses']):
                    mc = "└─" if j == len(a['missing_courses']) - 1 else "├─"
                    print(f"        {mc} {m['code']}: {m.get('name', m['code'])} ({format_credits(m.get('credits', 0))} cr)")

    if 'Electives' in cat_analysis:
        a = cat_analysis['Electives']
        n_completed = len(a['completed_courses'])
        status = f"✓ COMPLETE ({n_completed} courses)" if a['complete'] else f"⚠ INCOMPLETE ({n_completed} / 8 courses)"
        print(f"\nElectives (24 cr):      {status}")

    print()


# ─────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────

def run_level3(csv_text: str, program: str, waivers: list[str] = None, knowledge_file_content: str = None) -> dict:
    import io
    import sys
    
    if waivers is None:
        waivers = []
        
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    try:
        student_id, detect_prog, records = parse_transcript(csv_text)
        prog = program if program else detect_prog
        
        knowledge = parse_knowledge_content(knowledge_file_content, prog)
        
        resolved, retake_info = resolve_retakes(records)
        
        allowed = ALLOWED_WAIVERS.get(prog, [])
        valid_waivers = [w.strip().upper() for w in waivers if w.strip().upper() in allowed]
        
        audit = run_audit(resolved, retake_info, knowledge, prog, records, valid_waivers)
        audit['missing_capstone_codes'] = set(c['code'] for c in audit['missing_capstone'])
        
        print()
        print_audit_output(student_id, prog, "API Upload", "program_knowledge.md", audit, knowledge)
        
        result_text = sys.stdout.getvalue()
        
        result_json = {
            "student_id": student_id,
            "program": prog,
            "audit_level": 3,
            "total_credits": audit['total_earned'],
            "cgpa": round(audit['cgpa'], 2),
            "standing": audit['standing'],
            "eligible": audit['eligible'],
            "missing_courses": [m['code'] for m in audit.get('all_missing', [])] + [c['code'] for c in audit.get('missing_capstone', [])],
            "excluded_courses": [],
            "waivers_applied": valid_waivers
        }
    finally:
        sys.stdout = old_stdout
        
    return {
        "result_text": result_text,
        "result_json": result_json
    }


if __name__ == '__main__':
    pass
