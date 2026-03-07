#!/usr/bin/env python3
"""
Level 1: Credit Tally Engine
Counts only valid earned credits for graduation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.audit_core import AuditCore

class Level1Engine(AuditCore):
    def __init__(self):
        super().__init__()
    
    def calculate_valid_credits(self, courses):
        """Calculate total valid credits for graduation"""
        total_credits = 0
        valid_courses = []
        invalid_courses = []
        
        for course in courses:
            course_code = course['Course_Code']
            credits = float(course['Credits'])
            grade = course['Grade']
            
            # Skip 0-credit courses
            if credits == 0:
                invalid_courses.append({
                    'course_code': course_code,
                    'credits': credits,
                    'grade': grade,
                    'reason': '0-credit course'
                })
                continue
            
            # Skip failed grades and withdrawals
            if grade not in self.passing_grades or grade == 'W':
                invalid_courses.append({
                    'course_code': course_code,
                    'credits': credits,
                    'grade': grade,
                    'reason': 'Non-passing grade or withdrawal'
                })
                continue
            
            # Count valid credits
            total_credits += credits
            valid_courses.append({
                'course_code': course_code,
                'credits': credits,
                'grade': grade
            })
        
        return {
            'total_valid_credits': total_credits,
            'valid_courses': valid_courses,
            'invalid_courses': invalid_courses
        }
    
    def generate_report(self, transcript_file):
        """Generate Level 1 audit report"""
        courses = self.read_transcript(transcript_file)
        if not courses:
            return
        
        result = self.calculate_valid_credits(courses)
        
        print("=" * 60)
        print("LEVEL 1: CREDIT TALLY ENGINE REPORT")
        print("=" * 60)
        print(f"Total Valid Credits: {result['total_valid_credits']}")
        print(f"Valid Courses Count: {len(result['valid_courses'])}")
        print(f"Invalid Courses Count: {len(result['invalid_courses'])}")
        
        print("\nVALID COURSES:")
        for course in result['valid_courses']:
            print(f"  {course['course_code']} - {course['credits']} credits - Grade: {course['grade']}")
        
        print("\nINVALID COURSES:")
        for course in result['invalid_courses']:
            print(f"  {course['course_code']} - {course['credits']} credits - Grade: {course['grade']} ({course['reason']})")
        
        print("=" * 60)

def main():
    if len(sys.argv) != 2:
        print("Usage: python level1_engine.py <transcript.csv>")
        sys.exit(1)
    
    transcript_file = sys.argv[1]
    engine = Level1Engine()
    engine.generate_report(transcript_file)

if __name__ == "__main__":
    main()