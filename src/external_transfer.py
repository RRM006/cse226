#!/usr/bin/env python3
"""
NSU Audit Core - External Transfer Student Handler
Handles students transferring from other universities with credit transfers.
Implements NSU policy for external credit transfers.

NSU Transfer Policy:
- Maximum 50% of total program credits can be transferred
- Minimum grade requirement: C or above (2.0)
- Must complete at least 50% of credits at NSU
- Thesis/project credits usually not transferable
- Course must have NSU equivalent
"""

import sys
import csv
import os
from collections import defaultdict

VALID_GRADES = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'}
INVALID_GRADE_LABELS = {
    'F': 'FAILED',
    'W': 'WITHDRAWN',
    'I': 'INCOMPLETE',
    'X': 'MARKED',
    'D+': 'BELOW TRANSFER STANDARD',
    'D': 'BELOW TRANSFER STANDARD',
}

GRADE_POINTS = {
    'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0,
}

MIN_TRANSFER_GRADE = 'C'
MIN_TRANSFER_POINTS = 2.0

PROGRAM_CREDITS = {
    'BSCSE': 130,
    'BSEEE': 130,
    'LLB': 130,
}

MAX_TRANSFER_PERCENT = 0.50
MIN_NSUPERCENT = 0.50

EQUIVALENT_COURSES = {
    'BSCSE': {
        'ENG101': 'ENG102',
        'ENG102': 'ENG102',
        'ENG103': 'ENG103',
        'ENG111': 'ENG111',
        'MAT101': 'MAT120',
        'MAT102': 'MAT130',
        'MAT201': 'MAT250',
        'PHY101': 'PHY107',
        'PHY102': 'PHY108',
        'CHE101': 'CHE101',
        'CSE101': 'CSE115',
        'CSE102': 'CSE215',
        'CSE201': 'CSE225',
        'ECO101': 'ECO101',
        'ECO102': 'ECO104',
        'POL101': 'POL101',
        'SOC101': 'SOC101',
    },
    'BSEEE': {
        'ENG101': 'ENG102',
        'ENG102': 'ENG102',
        'ENG103': 'ENG103',
        'ENG111': 'ENG111',
        'MAT101': 'MAT120',
        'MAT102': 'MAT130',
        'MAT201': 'MAT250',
        'PHY101': 'PHY107',
        'PHY102': 'PHY108',
        'CHE101': 'CHE101',
        'EEE101': 'EEE141',
        'EEE102': 'EEE111',
        'ECO101': 'ECO101',
        'ECO102': 'ECO104',
    },
    'LLB': {
        'ENG101': 'ENG102',
        'ENG102': 'ENG102',
        'ENG103': 'ENG103',
        'LAW101': 'LLB101',
        'LAW102': 'LLB102',
        'LAW201': 'LLB103',
        'LAW202': 'LLB104',
        'ECO101': 'ECO101',
        'POL101': 'POL101',
    },
}

GED_EQUIVALENTS = {
    'ENG101': 'ENG102',
    'ENG102': 'ENG102',
    'ENG103': 'ENG103',
    'ENG111': 'ENG111',
    'MAT101': 'MAT120',
    'PHY101': 'PHY107',
    'CHE101': 'CHE101',
    'ECO101': 'ECO101',
    'POL101': 'POL101',
    'SOC101': 'SOC101',
    'HIS101': 'HIS103',
    'PHI101': 'PHI104',
}

def parse_external_transcript(filepath):
    """Parse external university transcript."""
    student_id = 'Unknown'
    university = 'Unknown'
    records = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                if 'Student:' in line:
                    student_id = line.split('Student:')[1].strip()
                elif 'University:' in line:
                    university = line.split('University:')[1].strip()
                continue
            break

    with open(filepath, 'r', encoding='utf-8') as f:
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
            semester = row.get('semester', 'N/A').strip()
            records.append({
                'code': code,
                'name': name,
                'credits': credits,
                'grade': grade,
                'semester': semester,
                'is_external': True,
                'university': university,
            })

    return student_id, university, records


def check_transfer_eligibility(grade):
    """Check if grade meets transfer eligibility."""
    if grade in VALID_GRADES:
        points = GRADE_POINTS.get(grade, 0)
        return points >= MIN_TRANSFER_POINTS
    return False


def find_equivalent_course(external_code, program):
    """Find NSU equivalent course code."""
    equivalencies = EQUIVALENT_COURSES.get(program, {})
    if external_code in equivalencies:
        return equivalencies[external_code]
    if external_code in GED_EQUIVALENTS:
        return GED_EQUIVALENTS[external_code]
    return None


def process_transfer_request(records, target_program):
    """Process external transfer request."""
    transferred = []
    rejected = []
    total_external_credits = 0.0

    for record in records:
        total_external_credits += record['credits']
        
        if not check_transfer_eligibility(record['grade']):
            rejected.append({
                'code': record['code'],
                'name': record['name'],
                'credits': record['credits'],
                'grade': record['grade'],
                'reason': f"Grade {record['grade']} below transfer standard (min C)",
            })
            continue

        equivalent = find_equivalent_course(record['code'], target_program)
        
        if equivalent:
            transferred.append({
                'external_code': record['code'],
                'nsu_code': equivalent,
                'name': record['name'],
                'credits': record['credits'],
                'grade': record['grade'],
                'university': record['university'],
            })
        else:
            rejected.append({
                'code': record['code'],
                'name': record['name'],
                'credits': record['credits'],
                'grade': record['grade'],
                'reason': f"No NSU equivalent found for {record['code']}",
            })

    max_transfer_credits = PROGRAM_CREDITS.get(target_program, 130) * MAX_TRANSFER_PERCENT
    
    transferred_credits = sum(t['credits'] for t in transferred)
    
    if transferred_credits > max_transfer_credits:
        excess = transferred_credits - max_transfer_credits
        rejected.append({
            'code': 'MAX_TRANSFER',
            'name': 'Maximum Transfer Limit',
            'credits': excess,
            'grade': 'N/A',
            'reason': f"Exceeds 50% transfer limit ({transferred_credits} > {max_transfer_credits})",
        })
        transferred_credits = max_transfer_credits

    return {
        'transferred': transferred,
        'rejected': rejected,
        'total_external_credits': total_external_credits,
        'transferred_credits': transferred_credits,
        'max_transfer_credits': max_transfer_credits,
        'target_program': target_program,
    }


def print_transfer_report(student_id, university, program, result):
    """Print the transfer evaluation report."""
    program_label = {
        'BSCSE': 'BSc in Computer Science and Engineering',
        'BSEEE': 'BSc in Electrical and Electronic Engineering',
        'LLB': 'LL.B Honors',
    }.get(program, program)

    print("=" * 70)
    print("NSU AUDIT CORE - EXTERNAL TRANSFER EVALUATION")
    print("=" * 70)
    print()
    print(f"Student:        {student_id}")
    print(f"External Univ:  {university}")
    print(f"Target Program: {program_label}")
    print()

    print("=" * 70)
    print("TRANSFER POLICY COMPLIANCE")
    print("=" * 70)
    print(f"Minimum Grade:    {MIN_TRANSFER_GRADE} ({MIN_TRANSFER_POINTS} points)")
    print(f"Max Transfer:     {result['max_transfer_credits']:.0f} credits (50% of program)")
    print(f"Total External:   {result['total_external_credits']:.1f} credits")
    print()

    print("=" * 70)
    print("TRANSFERRED COURSES")
    print("=" * 70)
    if result['transferred']:
        for i, t in enumerate(result['transferred']):
            connector = "└─" if i == len(result['transferred']) - 1 else "├─"
            print(f"  {connector} {t['external_code']} → {t['nsu_code']}: {t['name']}")
            print(f"      Grade: {t['grade']} | Credits: {t['credits']} | From: {t['university']}")
    else:
        print("  No courses transferred.")
    print()

    print("=" * 70)
    print("REJECTED/NON-TRANSFERABLE COURSES")
    print("=" * 70)
    if result['rejected']:
        for i, r in enumerate(result['rejected']):
            connector = "└─" if i == len(result['rejected']) - 1 else "├─"
            print(f"  {connector} {r['code']}: {r['name']}")
            print(f"      Grade: {r['grade']} | Credits: {r['credits']}")
            print(f"      Reason: {r['reason']}")
    else:
        print("  No rejected courses.")
    print()

    print("=" * 70)
    print("TRANSFER SUMMARY")
    print("=" * 70)
    print(f"Courses Evaluated:    {len(result['transferred']) + len(result['rejected'])}")
    print(f"Courses Transferred:  {len(result['transferred'])}")
    print(f"Courses Rejected:     {len(result['rejected'])}")
    print(f"Credits Transferred:  {result['transferred_credits']:.1f}")
    print(f"Credits Rejected:     {result['total_external_credits'] - result['transferred_credits']:.1f}")
    print()

    nsu_credits_needed = PROGRAM_CREDITS.get(program, 130) - result['transferred_credits']
    print("=" * 70)
    print("REQUIREMENTS TO COMPLETE AT NSU")
    print("=" * 70)
    print(f"NSU Credits Required: {nsu_credits_needed:.0f}")
    print(f"Minimum NSU Credits:  {PROGRAM_CREDITS.get(program, 130) * MIN_NSUPERCENT:.0f} (50% of program)")
    
    if nsu_credits_needed >= PROGRAM_CREDITS.get(program, 130) * MIN_NSUPERCENT:
        print("Status: ✓ MEETS NSU RESIDENCY REQUIREMENT")
    else:
        print("Status: ⚠ DOES NOT MEET NSU RESIDENCY REQUIREMENT")
    print()


def main():
    if len(sys.argv) < 3:
        print("Usage: python external_transfer.py <external_transcript.csv> <target_program>")
        print("  target_program: BSCSE | BSEEE | LLB")
        sys.exit(1)

    filepath = sys.argv[1]
    target_program = sys.argv[2].upper()

    if target_program not in PROGRAM_CREDITS:
        print(f"Error: Invalid program. Must be BSCSE, BSEEE, or LLB")
        sys.exit(1)

    if not os.path.isfile(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    student_id, university, records = parse_external_transcript(filepath)
    result = process_transfer_request(records, target_program)
    print_transfer_report(student_id, university, target_program, result)


if __name__ == '__main__':
    main()
