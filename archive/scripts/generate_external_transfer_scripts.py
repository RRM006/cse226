#!/usr/bin/env python3
"""
Generate test scripts for external transfer tests.
"""

import os
import glob

PROJECT_ROOT = '/home/rafi/Workspace/Projects/cse226_project/project1_antigravity'
TESTS_DIR = os.path.join(PROJECT_ROOT, 'tests')
TESTBAT_DIR = os.path.join(PROJECT_ROOT, 'testbat')

# Get all external transfer test files
test_files = glob.glob(os.path.join(TESTS_DIR, 'external_transfers', '**', '*.csv'), recursive=True)
test_files.sort()

PROGRAM_MAP = {
    'BSCSE': 'BSCSE',
    'BSEEE': 'BSEEE',
    'LLB': 'LLB',
}

def get_program(filepath):
    parts = filepath.replace('\\', '/').split('/')
    if '/BSCSE/' in filepath:
        return 'BSCSE'
    elif '/BSEEE/' in filepath:
        return 'BSEEE'
    elif '/LLB/' in filepath:
        return 'LLB'
    return 'BSCSE'

for test_file in test_files:
    program = get_program(test_file)
    test_name = os.path.basename(test_file).replace('.csv', '')
    
    # Get relative path
    rel_path = os.path.relpath(test_file, TESTS_DIR)
    base_name = os.path.basename(test_file).replace('.csv', '')
    dir_name = os.path.relpath(test_file, os.path.join(TESTS_DIR, 'external_transfers'))
    dir_path = os.path.dirname(dir_name)
    
    # Calculate depth
    depth = len(dir_path.split(os.sep)) if dir_path and dir_path != '.' else 0
    up_levels = '../' * (depth + 3)
    
    # Create target directory
    target_dir = os.path.join(TESTBAT_DIR, 'external_transfers', dir_path)
    os.makedirs(target_dir, exist_ok=True)
    
    rel_src = f"{up_levels}src"
    rel_tests = f"{up_levels}tests"
    rel_test_file = os.path.join(rel_tests, 'external_transfers', os.path.basename(os.path.dirname(test_file)), base_name + '.csv')
    
    # Generate .bat file
    bat_content = f'''@echo off
REM Test: {test_name}
REM External Transfer Evaluation
python "{rel_src}/external_transfer.py" "{rel_test_file}" {program}
pause
'''
    bat_file = os.path.join(target_dir, base_name + '.bat')
    with open(bat_file, 'w') as f:
        f.write(bat_content)
    
    # Generate .sh file
    sh_content = f'''#!/bin/bash
# Test: {test_name}
# External Transfer Evaluation
python3 "{rel_src}/external_transfer.py" "{rel_test_file}" {program}
'''
    sh_file = os.path.join(target_dir, base_name + '.sh')
    with open(sh_file, 'w') as f:
        f.write(sh_content)
    os.chmod(sh_file, 0o755)

print(f"Generated {len(test_files) * 2} external transfer scripts")
