#!/usr/bin/env python3
"""
Level 3: Audit & Deficiency Reporter
Compares student history against program requirements and identifies deficiencies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.audit_core import AuditCore

class Level3Engine(AuditCore):
    def __init__(self):
        super().__init__()
    
    def get_completed_courses(self, courses):
        """Get list of successfully completed courses"""
        completed = set()
        for course in courses:
            course_code = course['Course_Code']
            credits = float(course['Credits'])
            grade = course['Grade']
            
            # Course is complete if it has credits and passing grade
            if credits > 0 and grade in self.passing_grades:
                completed.add(course_code)
        
        return completed
    
    def calculate_cgpa(self, courses):
        """Calculate CGPA for academic standing"""
        total_quality_points = 0
        total_credits = 0
        
        for course in courses:
            credits = float(course['Credits'])
            grade = course['Grade']
            
            if credits > 0 and grade in self.grade_points:
                quality_points = self.grade_points[grade] * credits
                total_quality_points += quality_points
                total_credits += credits
        
        return total_quality_points / total_credits if total_credits > 0 else 0.0
    
    def audit_program_requirements(self, courses, program_requirements, waivers=None):
        """Audit student against program requirements"""
        if waivers is None:
            waivers = []
        
        completed_courses = self.get_completed_courses(courses)
        cgpa = self.calculate_cgpa(courses)
        
        # Initialize audit results
        audit_results = {
            'program_name': program_requirements.get('program_name', 'Unknown'),
            'total_credits_required': program_requirements.get('total_credits', 0),
            'completed_credits': 0,
            'cgpa': round(cgpa, 3),
            'academic_standing': 'Good Standing' if cgpa >= 2.0 else 'PROBATION',
            'deficiencies': [],
            'completed_requirements': {},
            'missing_requirements': {},
            'can_graduate': False
        }
        
        # Calculate completed credits (only count passing grades)
        for course in courses:
            credits = float(course['Credits'])
            grade = course['Grade']
            if credits > 0 and grade in self.passing_grades:
                audit_results['completed_credits'] += credits
        
        # Check mandatory GED requirements
        mandatory_ged = program_requirements.get('mandatory_ged', [])
        for course in mandatory_ged:
            if course in waivers:
                audit_results['completed_requirements']['GED'] = audit_results['completed_requirements'].get('GED', []) + [f"{course} (Waived)"]
            elif course in completed_courses:
                audit_results['completed_requirements']['GED'] = audit_results['completed_requirements'].get('GED', []) + [course]
            else:
                audit_results['missing_requirements']['GED'] = audit_results['missing_requirements'].get('GED', []) + [course]
                audit_results['deficiencies'].append(f"Missing mandatory GED course: {course}")
        
        # Check core requirements based on program type
        if 'core_math' in program_requirements:
            core_math = program_requirements['core_math']
            for course in core_math:
                if course in waivers:
                    audit_results['completed_requirements']['Core Math'] = audit_results['completed_requirements'].get('Core Math', []) + [f"{course} (Waived)"]
                elif course in completed_courses:
                    audit_results['completed_requirements']['Core Math'] = audit_results['completed_requirements'].get('Core Math', []) + [course]
                else:
                    audit_results['missing_requirements']['Core Math'] = audit_results['missing_requirements'].get('Core Math', []) + [course]
                    audit_results['deficiencies'].append(f"Missing Core Math course: {course}")
        
        if 'core_business' in program_requirements:
            core_business = program_requirements['core_business']
            for course in core_business:
                if course in waivers:
                    audit_results['completed_requirements']['Core Business'] = audit_results['completed_requirements'].get('Core Business', []) + [f"{course} (Waived)"]
                elif course in completed_courses:
                    audit_results['completed_requirements']['Core Business'] = audit_results['completed_requirements'].get('Core Business', []) + [course]
                else:
                    audit_results['missing_requirements']['Core Business'] = audit_results['missing_requirements'].get('Core Business', []) + [course]
                    audit_results['deficiencies'].append(f"Missing Core Business course: {course}")
        
        # Check major core requirements
        if 'major_core' in program_requirements:
            major_core = program_requirements['major_core']
            for course in major_core:
                if course in waivers:
                    audit_results['completed_requirements']['Major Core'] = audit_results['completed_requirements'].get('Major Core', []) + [f"{course} (Waived)"]
                elif course in completed_courses:
                    audit_results['completed_requirements']['Major Core'] = audit_results['completed_requirements'].get('Major Core', []) + [course]
                else:
                    audit_results['missing_requirements']['Major Core'] = audit_results['missing_requirements'].get('Major Core', []) + [course]
                    audit_results['deficiencies'].append(f"Missing Major Core course: {course}")
        
        # Check credit requirement
        if audit_results['completed_credits'] < audit_results['total_credits_required']:
            audit_results['deficiencies'].append(
                f"Insufficient credits: {audit_results['completed_credits']}/{audit_results['total_credits_required']} required"
            )
        
        # Check CGPA requirement
        if cgpa < 2.0:
            audit_results['deficiencies'].append(f"CGPA below requirement: {cgpa:.3f} < 2.0")
        
        # Determine graduation eligibility
        audit_results['can_graduate'] = (
            audit_results['completed_credits'] >= audit_results['total_credits_required'] and
            cgpa >= 2.0 and
            len(audit_results['deficiencies']) == 0
        )
        
        return audit_results
    
    def get_program_selection(self, programs):
        """Allow admin to select program for audit"""
        print("\n" + "="*50)
        print("PROGRAM SELECTION")
        print("="*50)
        print("Available programs:")
        for i, program_name in enumerate(programs.keys(), 1):
            print(f"{i}. {program_name}")
        
        while True:
            try:
                choice = int(input(f"\nSelect program (1-{len(programs)}): "))
                if 1 <= choice <= len(programs):
                    selected_program = list(programs.keys())[choice - 1]
                    return selected_program, programs[selected_program]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    def get_waivers_from_user(self):
        """Interactive waiver input from admin"""
        waivers = []
        print("\n" + "="*50)
        print("WAIVER HANDLER")
        print("="*50)
        print("Enter course codes for granted waivers (press Enter to finish):")
        
        while True:
            waiver_input = input("Waiver for course code (or press Enter to finish): ").strip().upper()
            if not waiver_input:
                break
            waivers.append(waiver_input)
            print(f"Added waiver for {waiver_input}")
        
        return waivers
    
    def generate_report(self, transcript_file, program_file):
        """Generate Level 3 comprehensive audit report"""
        # Read data
        courses = self.read_transcript(transcript_file)
        if not courses:
            return
        
        programs = self.read_program_knowledge(program_file)
        if not programs:
            return
        
        # Get program selection and waivers
        program_name, program_requirements = self.get_program_selection(programs)
        program_requirements['program_name'] = program_name
        waivers = self.get_waivers_from_user()
        
        # Perform audit
        audit_results = self.audit_program_requirements(courses, program_requirements, waivers)
        
        # Generate report
        print("\n" + "=" * 70)
        print("LEVEL 3: COMPREHENSIVE AUDIT & DEFICIENCY REPORT")
        print("=" * 70)
        print(f"Program: {audit_results['program_name']}")
        print(f"Degree: {program_requirements.get('degree', 'N/A')}")
        print(f"Total Credits Required: {audit_results['total_credits_required']}")
        print(f"Completed Credits: {audit_results['completed_credits']}")
        print(f"CGPA: {audit_results['cgpa']}")
        print(f"Academic Standing: {audit_results['academic_standing']}")
        
        print(f"\nGRADUATION STATUS: {'ELIGIBLE' if audit_results['can_graduate'] else 'NOT ELIGIBLE'}")
        
        if waivers:
            print(f"\nWaivers Granted: {', '.join(waivers)}")
        
        if audit_results['completed_requirements']:
            print(f"\nCOMPLETED REQUIREMENTS:")
            for category, courses in audit_results['completed_requirements'].items():
                print(f"  {category}: {', '.join(courses)}")
        
        if audit_results['missing_requirements']:
            print(f"\nMISSING REQUIREMENTS:")
            for category, courses in audit_results['missing_requirements'].items():
                print(f"  {category}: {', '.join(courses)}")
        
        if audit_results['deficiencies']:
            print(f"\nDEFICIENCIES:")
            for deficiency in audit_results['deficiencies']:
                print(f"  ❌ {deficiency}")
        else:
            print(f"\n✅ No deficiencies found!")
        
        print("\n" + "=" * 70)

def main():
    if len(sys.argv) != 3:
        print("Usage: python level3_engine.py <transcript.csv> <program_knowledge.md>")
        sys.exit(1)
    
    transcript_file = sys.argv[1]
    program_file = sys.argv[2]
    
    engine = Level3Engine()
    engine.generate_report(transcript_file, program_file)

if __name__ == "__main__":
    main()