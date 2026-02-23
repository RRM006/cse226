#!/usr/bin/env python3
"""
Run all test cases and capture outputs to files.
"""

import os
import subprocess
import glob
import sys

PROJECT_ROOT = '/home/rafi/Workspace/Projects/cse226_project/project1_antigravity'
TESTS_DIR = os.path.join(PROJECT_ROOT, 'tests')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'test_outputs')
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
PROG_KNOWLEDGE_DIR = os.path.join(PROJECT_ROOT, 'program_knowledge')

PROGRAM_KNOWLEDGE = {
    'BSCSE': 'program_knowledge_BSCSE.md',
    'BSEEE': 'program_knowledge_BSEEE.md',
    'LLB': 'program_knowledge_LLB.md',
    'transfers': 'program_knowledge_LLB.md',
}

def get_level_program(filepath):
    parts = filepath.replace('\\', '/').split('/')
    
    # Check for external transfers first
    if 'external_transfers' in parts:
        program = None
        for p in ['BSCSE', 'BSEEE', 'LLB']:
            if f'/{p}/' in filepath or filepath.endswith(f'/{p}/'):
                program = p
                break
        if program is None:
            program = 'BSCSE'  # default
        return 'external', program
    
    if 'BSCSE' in parts:
        program = 'BSCSE'
    elif 'BSEEE' in parts:
        program = 'BSEEE'
    elif 'LLB' in parts:
        program = 'LLB'
    else:
        program = 'transfers'
    
    if '/L1/' in filepath:
        level = 1
    elif '/L2/' in filepath:
        level = 2
    elif '/L3/' in filepath or '/transfers/' in filepath:
        level = 3
    else:
        level = 1
    
    return level, program

def run_test(test_file, level, program):
    test_name = os.path.basename(test_file).replace('.csv', '')
    
    # Get relative path from tests directory
    rel_path = os.path.relpath(test_file, TESTS_DIR)
    output_subdir = os.path.join(OUTPUT_DIR, os.path.dirname(rel_path))
    os.makedirs(output_subdir, exist_ok=True)
    output_file = os.path.join(output_subdir, test_name + '.txt')
    
    try:
        # Handle external transfers separately
        if level == 'external':
            cmd = [sys.executable, os.path.join(SRC_DIR, 'external_transfer.py'), test_file, program]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            output = result.stdout + result.stderr
        elif level == 1:
            cmd = [sys.executable, os.path.join(SRC_DIR, 'level1_credit_tally.py'), test_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            output = result.stdout + result.stderr
        elif level == 2:
            cmd = [sys.executable, os.path.join(SRC_DIR, 'level2_cgpa_calculator.py'), test_file]
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate(input='NONE\n', timeout=30)
            output = stdout + stderr
        else:
            knowledge_file = os.path.join(PROG_KNOWLEDGE_DIR, PROGRAM_KNOWLEDGE.get(program, 'program_knowledge_BSCSE.md'))
            cmd = [sys.executable, os.path.join(SRC_DIR, 'level3_audit_engine.py'), test_file, knowledge_file]
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate(input='NONE\n', timeout=30)
            output = stdout + stderr
        
        with open(output_file, 'w') as f:
            f.write(output)
        
        # Check for errors
        has_error = 'Error' in output or 'error' in output or 'Traceback' in output or 'Exception' in output
        
        return test_name, output_file, has_error, output
        
    except Exception as e:
        error_msg = f"EXCEPTION: {str(e)}"
        with open(output_file, 'w') as f:
            f.write(error_msg)
        return test_name, output_file, True, error_msg

# Get all test files
test_files = glob.glob(os.path.join(TESTS_DIR, '**', '*.csv'), recursive=True)
test_files.sort()

# Run all tests
bugs_found = []
results = []

print(f"Running {len(test_files)} test cases...\n")

for test_file in test_files:
    level, program = get_level_program(test_file)
    test_name = os.path.basename(test_file).replace('.csv', '')
    
    level_str = "EXT" if level == "external" else f"L{level}"
    print(f"Testing: {test_name} ({program} {level_str})...", end=" ")
    
    name, output_file, has_error, output = run_test(test_file, level, program)
    
    results.append({
        'test': test_name,
        'program': program,
        'level': level,
        'file': output_file,
        'has_error': has_error
    })
    
    if has_error:
        print(f"BUG FOUND!")
        bugs_found.append({
            'test': test_name,
            'program': program,
            'level': level,
            'output': output[:1000]
        })
    else:
        print("OK")

print(f"\n{'='*50}")
print(f"Total tests: {len(test_files)}")
print(f"Bugs found: {len(bugs_found)}")

# Write bugs to foundbug.md
bugs_md = """# Found Bugs Report

This file contains all bugs and issues found during testing.

"""

if bugs_found:
    for i, bug in enumerate(bugs_found, 1):
        bugs_md += f"""## Bug #{i}: {bug['test']}

- **Program**: {bug['program']}
- **Level**: {bug['level']}
- **Test File**: {bug['test']}

### Output:
```
{bug['output'][:1500]}
```

---

"""
else:
    bugs_md += "No bugs found! All tests passed.\n"

with open(os.path.join(PROJECT_ROOT, 'foundbug.md'), 'w') as f:
    f.write(bugs_md)

print(f"\nBug report written to: foundbug.md")
print(f"Test outputs saved to: {OUTPUT_DIR}")
