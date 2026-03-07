import csv
import sys
import os

class AuditCore:
    def __init__(self):
        self.grade_points = {
            'A': 4.0, 'A-': 3.67, 'B+': 3.33, 'B': 3.0, 'B-': 2.67,
            'C+': 2.33, 'C': 2.0, 'C-': 1.67, 'D+': 1.33, 'D': 1.0, 'F': 0.0
        }
        self.passing_grades = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D'}
        
    def read_transcript(self, transcript_file):
        """Read student transcript from CSV file"""
        courses = []
        try:
            with open(transcript_file, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    courses.append(row)
        except FileNotFoundError:
            print(f"Error: Transcript file '{transcript_file}' not found")
            return []
        return courses
    
    def read_program_knowledge(self, program_file):
        """Read program requirements from markdown file"""
        try:
            with open(program_file, 'r') as file:
                content = file.read()
            return self.parse_program_knowledge(content)
        except FileNotFoundError:
            print(f"Error: Program knowledge file '{program_file}' not found")
            return {}
    
    def parse_program_knowledge(self, content):
        """Parse program knowledge from markdown content"""
        programs = {}
        lines = content.split('\n')
        current_program = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('## [Program:'):
                program_name = line.split(':')[1].split(']')[0].strip()
                programs[program_name] = {}
                current_program = program_name
            elif current_program and line.startswith('-'):
                if '**Degree**:' in line:
                    programs[current_program]['degree'] = line.split(':')[1].strip()
                elif '**Total Credits Required**:' in line:
                    programs[current_program]['total_credits'] = int(line.split(':')[1].strip())
                elif '**Mandatory GED**:' in line:
                    courses = line.split(':')[1].strip().split(', ')
                    programs[current_program]['mandatory_ged'] = [c.strip() for c in courses]
                elif '**Core Math**:' in line:
                    courses = line.split(':')[1].strip().split(', ')
                    programs[current_program]['core_math'] = [c.strip() for c in courses]
                elif '**Core Business**:' in line:
                    courses = line.split(':')[1].strip().split(', ')
                    programs[current_program]['core_business'] = [c.strip() for c in courses]
                elif '**Major Core**:' in line:
                    courses = line.split(':')[1].strip().split(', ')
                    programs[current_program]['major_core'] = [c.strip() for c in courses]
        
        return programs