#!/usr/bin/env python3
"""
Level 2: CGPA Calculator with Waiver Handler
Calculates weighted CGPA and handles program-specific waivers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.audit_core import AuditCore

class Level2Engine(AuditCore):
    def __init__(self):
        super().__init__()
    
    def calculate_cgpa(self, courses, waivers=None):
        """Calculate weighted CGPA excluding waivers and non-graded courses"""
        if waivers is None:
            waivers = []
        
        total_quality_points = 0
        total_credits = 0
        graded_courses = []
        excluded_courses = []
        
        for course in courses:
            course_code = course['Course_Code']
            credits = float(course['Credits'])
            grade = course['Grade']
            
            # Skip waived courses
            if course_code in waivers:
                excluded_courses.append({
                    'course_code': course_code,
                    'credits': credits,
                    'grade': grade,
                    'reason': 'Waived'
                })
                continue
            
            # Skip 0-credit courses
            if credits == 0:
                excluded_courses.append({
                    'course_code': course_code,
                    'credits': credits,
                    'grade': grade,
                    'reason': '0-credit course'
                })
                continue
            
            # Skip withdrawals and incomplete grades
            if grade == 'W' or grade not in self.grade_points:
                excluded_courses.append({
                    'course_code': course_code,
                    'credits': credits,
                    'grade': grade,
                    'reason': 'Withdrawal or non-graded'
                })
                continue
            
            # Calculate quality points
            quality_points = self.grade_points[grade] * credits
            total_quality_points += quality_points
            total_credits += credits
            
            graded_courses.append({
                'course_code': course_code,
                'credits': credits,
                'grade': grade,
                'grade_points': self.grade_points[grade],
                'quality_points': quality_points
            })
        
        cgpa = total_quality_points / total_credits if total_credits > 0 else 0.0
        
        return {
            'cgpa': round(cgpa, 3),
            'total_quality_points': round(total_quality_points, 3),
            'total_credits': total_credits,
            'graded_courses': graded_courses,
            'excluded_courses': excluded_courses
        }
    
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
    
    def generate_report(self, transcript_file):
        """Generate Level 2 audit report with CGPA and waivers"""
        courses = self.read_transcript(transcript_file)
        if not courses:
            return
        
        # Get waivers from admin
        waivers = self.get_waivers_from_user()
        
        # Calculate CGPA
        result = self.calculate_cgpa(courses, waivers)
        
        print("\n" + "=" * 60)
        print("LEVEL 2: CGPA CALCULATOR & WAIVER HANDLER REPORT")
        print("=" * 60)
        print(f"Weighted CGPA: {result['cgpa']}")
        print(f"Total Quality Points: {result['total_quality_points']}")
        print(f"Total Credits for CGPA: {result['total_credits']}")
        print(f"Graded Courses Count: {len(result['graded_courses'])}")
        print(f"Excluded Courses Count: {len(result['excluded_courses'])}")
        
        if waivers:
            print(f"\nWaivers Granted: {', '.join(waivers)}")
        
        print("\nGRADED COURSES (for CGPA):")
        for course in result['graded_courses']:
            print(f"  {course['course_code']} - {course['credits']} credits - "
                  f"Grade: {course['grade']} ({course['grade_points']} points) - "
                  f"QP: {course['quality_points']}")
        
        print("\nEXCLUDED COURSES:")
        for course in result['excluded_courses']:
            print(f"  {course['course_code']} - {course['credits']} credits - "
                  f"Grade: {course['grade']} ({course['reason']})")
        
        # Academic standing
        print(f"\nACADEMIC STANDING:")
        if result['cgpa'] >= 3.5:
            print("  Status: Dean's List")
        elif result['cgpa'] >= 2.0:
            print("  Status: Good Standing")
        else:
            print("  Status: PROBATION")
        
        print("=" * 60)

def main():
    if len(sys.argv) != 2:
        print("Usage: python level2_engine.py <transcript.csv>")
        sys.exit(1)
    
    transcript_file = sys.argv[1]
    engine = Level2Engine()
    engine.generate_report(transcript_file)

if __name__ == "__main__":
    main()