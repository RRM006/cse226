#!/usr/bin/env python3
"""
Generate batch (.bat) and shell (.sh) scripts for each test case.
"""

import os
import glob

# Get the project root directory (parent of scripts folder)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.join(PROJECT_ROOT, 'tests')
TESTBAT_DIR = os.path.join(PROJECT_ROOT, 'testbat')

# Get all CSV test files
test_files = glob.glob(os.path.join(TESTS_DIR, '**', '*.csv'), recursive=True)

# Sort for consistent ordering
test_files.sort()

# Map programs to their knowledge files
PROGRAM_KNOWLEDGE = {
    'BSCSE': 'program_knowledge_BSCSE.md',
    'BSEEE': 'program_knowledge_BSEEE.md',
    'LLB': 'program_knowledge_LLB.md',
    'transfers': 'program_knowledge_LLB.md',
}

# Map test folder to level and program
def get_level_program(filepath):
    parts = filepath.split(os.sep)
    if 'BSCSE' in parts:
        program = 'BSCSE'
    elif 'BSEEE' in parts:
        program = 'BSEEE'
    elif 'LLB' in parts:
        program = 'LLB'
    else:
        program = 'transfers'
    
    if 'L1' in parts:
        level = 1
    elif 'L2' in parts:
        level = 2
    elif 'L3' in parts:
        level = 3
    else:
        level = 3
    
    return level, program

# Generate .bat file content
def generate_bat(test_name, level, program, rel_src, rel_test_file, rel_prog_knowledge):
    if level == 1:
        return f'''@echo off
REM Test: {test_name}
REM Level: 1 - Credit Tally
python "{rel_src}/level1_credit_tally.py" "{rel_test_file}"
pause
'''
    elif level == 2:
        return f'''@echo off
REM Test: {test_name}
REM Level: 2 - CGPA Calculator
echo NONE | python "{rel_src}/level2_cgpa_calculator.py" "{rel_test_file}"
pause
'''
    else:
        knowledge_file = os.path.join(rel_prog_knowledge, PROGRAM_KNOWLEDGE.get(program, 'program_knowledge_BSCSE.md'))
        return f'''@echo off
REM Test: {test_name}
REM Level: 3 - Audit Engine
echo NONE | python "{rel_src}/level3_audit_engine.py" "{rel_test_file}" "{knowledge_file}"
pause
'''

# Generate .sh file content
def generate_sh(test_name, level, program, rel_src, rel_test_file, rel_prog_knowledge):
    if level == 1:
        return f'''#!/bin/bash
# Test: {test_name}
# Level: 1 - Credit Tally
python3 "{rel_src}/level1_credit_tally.py" "{rel_test_file}"
'''
    elif level == 2:
        return f'''#!/bin/bash
# Test: {test_name}
# Level: 2 - CGPA Calculator
echo "NONE" | python3 "{rel_src}/level2_cgpa_calculator.py" "{rel_test_file}"
'''
    else:
        knowledge_file = os.path.join(rel_prog_knowledge, PROGRAM_KNOWLEDGE.get(program, 'program_knowledge_BSCSE.md'))
        return f'''#!/bin/bash
# Test: {test_name}
# Level: 3 - Audit Engine
echo "NONE" | python3 "{rel_src}/level3_audit_engine.py" "{rel_test_file}" "{knowledge_file}"
'''

# Generate all files
for test_file in test_files:
    level, program = get_level_program(test_file)
    
    # Get relative path from tests directory
    rel_path = os.path.relpath(test_file, TESTS_DIR)
    test_name = os.path.basename(test_file).replace('.csv', '')
    dir_name = os.path.dirname(rel_path)
    
    # Calculate depth to determine relative path
    depth = len(dir_name.split(os.sep)) if dir_name else 0
    up_levels = '../' * (depth + 1)
    
    # Build relative paths
    rel_src = f"{up_levels}src"
    rel_tests = f"{up_levels}tests"
    rel_prog_knowledge = f"{up_levels}program_knowledge"
    rel_test_file = os.path.join(rel_tests, rel_path)
    
    # Create target directory
    target_dir = os.path.join(TESTBAT_DIR, dir_name)
    os.makedirs(target_dir, exist_ok=True)
    
    # Generate .bat file
    bat_content = generate_bat(test_name, level, program, rel_src, rel_test_file, rel_prog_knowledge)
    bat_file = os.path.join(target_dir, test_name + '.bat')
    with open(bat_file, 'w') as f:
        f.write(bat_content)
    
    # Generate .sh file
    sh_content = generate_sh(test_name, level, program, rel_src, rel_test_file, rel_prog_knowledge)
    sh_file = os.path.join(target_dir, test_name + '.sh')
    with open(sh_file, 'w') as f:
        f.write(sh_content)
    os.chmod(sh_file, 0o755)

print(f"Generated {len(test_files) * 2} scripts in {TESTBAT_DIR}")
