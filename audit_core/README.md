# NSU Audit Core - Department Administration Tool

## Overview
The Audit Core is a comprehensive CLI tool designed for NSU's Department Administration to verify student graduation eligibility. This tool processes student transcripts and compares them against program requirements to provide detailed audit reports.

## Features
- **Level 1**: Credit Tally Engine - Counts valid earned credits for graduation
- **Level 2**: CGPA Calculator with Waiver Handler - Calculates weighted CGPA and handles waivers
- **Level 3**: Audit & Deficiency Reporter - Comprehensive audit against program requirements

## Project Structure
```
audit_core/
├── src/
│   ├── audit_core.py          # Base functionality
│   ├── level1_engine.py       # Level 1 implementation
│   ├── level2_engine.py       # Level 2 implementation
│   └── level3_engine.py       # Level 3 implementation
├── data/
│   ├── test_L1.csv           # Level 1 test data
│   ├── test_L2.csv           # Level 2 test data
│   └── retake_scenario.csv   # Retake scenario test data
├── pdf/
│   ├── transcript.csv        # Sample transcript
│   ├── Audit Core.md         # Project requirements
│   └── program.md            # Program knowledge base
└── README.md                 # This file
```

## Installation & Setup

### Prerequisites
- Python 3.6 or higher
- No additional packages required (uses only standard library)

### Setup
1. Clone or download the project
2. Navigate to the `audit_core` directory
3. Ensure the data files are in place

## Usage

### Level 1: Credit Tally Engine
Counts only valid earned credits for graduation eligibility.

```bash
python src/level1_engine.py data/transcript.csv
```

**What it does:**
- Counts credits from courses with passing grades (A, B, C, D)
- Excludes 0-credit courses, failed grades (F), and withdrawals (W)
- Provides detailed report of valid vs invalid courses

### Level 2: CGPA Calculator with Waiver Handler
Calculates weighted CGPA and handles program-specific waivers.

```bash
python src/level2_engine.py data/transcript.csv
```

**What it does:**
- Calculates weighted CGPA using NSU grade scale
- Interactive waiver input from admin
- Excludes waived courses and non-graded entries from CGPA calculation
- Determines academic standing (Dean's List, Good Standing, Probation)

### Level 3: Comprehensive Audit & Deficiency Reporter
Full audit against program requirements with detailed deficiency reporting.

```bash
python src/level3_engine.py data/transcript.csv pdf/program.md
```

**What it does:**
- Interactive program selection
- Comprehensive audit against program requirements
- Identifies missing mandatory courses
- Checks credit requirements and CGPA thresholds
- Provides detailed graduation eligibility report

## Test Data

### Provided Test Files
- `data/test_L1.csv`: Edge cases for credit validation
- `data/test_L2.csv`: CGPA and waiver scenarios
- `data/retake_scenario.csv`: Course retake and multiple attempts

### Test Scenarios Covered
1. **Credit Validation**: 0-credit courses, failed grades, withdrawals
2. **Waiver Handling**: Interactive waiver input for ENG102, BUS112, etc.
3. **Retake Scenarios**: Multiple course attempts with different outcomes
4. **Edge Cases**: Incomplete grades, repeated courses, mixed performance

## Grade Scale & Rules

### NSU Grade Points
- A: 4.0
- A-: 3.67
- B+: 3.33
- B: 3.0
- B-: 2.67
- C+: 2.33
- C: 2.0
- C-: 1.67
- D+: 1.33
- D: 1.0
- F: 0.0

### Passing Grades
A, A-, B+, B, B-, C+, C, C-, D+, D

### Academic Standing
- **Dean's List**: CGPA ≥ 3.5
- **Good Standing**: CGPA ≥ 2.0
- **Probation**: CGPA < 2.0

## Program Requirements

### Computer Science & Engineering (BS)
- **Total Credits**: 130
- **Mandatory GED**: ENG102, ENG103, HIS103, PHI101
- **Core Math**: MAT116, MAT120, MAT250, MAT350, MAT361
- **Major Core**: CSE115, CSE173, CSE215, CSE225, CSE231, CSE311, CSE323, CSE327, CSE331, CSE332, CSE425

### Business Administration (BBA)
- **Total Credits**: 124
- **Mandatory GED**: ENG102, ENG103, HIS103, PHI101, ENV203
- **Core Business**: ACT201, ACT202, FIN254, MGT210, MGT314, MGT368, MKT202
- **Major Core**: BUS101, BUS112, BUS134, MIS205, QM212

## Sample Output

### Level 1 Output
```
============================================================
LEVEL 1: CREDIT TALLY ENGINE REPORT
============================================================
Total Valid Credits: 42.0
Valid Courses Count: 12
Invalid Courses Count: 5

VALID COURSES:
  ENG102 - 3 credits - Grade: A
  MAT116 - 3 credits - Grade: B
  ...

INVALID COURSES:
  CSE115L - 0 credits - Grade: A (0-credit course)
  HIS103 - 3 credits - Grade: F (Non-passing grade or withdrawal)
  ...
```

### Level 2 Output
```
============================================================
LEVEL 2: CGPA CALCULATOR & WAIVER HANDLER REPORT
============================================================
Weighted CGPA: 3.245
Total Quality Points: 136.29
Total Credits for CGPA: 42.0
Academic Standing: Good Standing
```

### Level 3 Output
```
======================================================================
LEVEL 3: COMPREHENSIVE AUDIT & DEFICIENCY REPORT
======================================================================
Program: Computer Science & Engineering
Total Credits Required: 130
Completed Credits: 42
CGPA: 3.245
Academic Standing: Good Standing

GRADUATION STATUS: NOT ELIGIBLE

MISSING REQUIREMENTS:
  Core Math: MAT250, MAT350, MAT361
  Major Core: CSE231, CSE311, CSE323, CSE327, CSE331, CSE332, CSE425

DEFICIENCIES:
  ❌ Insufficient credits: 42/130 required
  ❌ Missing Core Math course: MAT250
  ❌ Missing Major Core course: CSE311
  ...
```

## Testing the Project

### Running All Tests
```bash
# Test Level 1
python src/level1_engine.py data/test_L1.csv

# Test Level 2 (interactive)
python src/level2_engine.py data/test_L2.csv

# Test Level 3 (interactive)
python src/level3_engine.py data/retake_scenario.csv pdf/program.md
```

### Verification Steps
1. **Level 1**: Verify correct credit counting and exclusion of invalid courses
2. **Level 2**: Test CGPA calculation accuracy and waiver handling
3. **Level 3**: Validate comprehensive audit and deficiency identification

### Edge Cases to Test
- Students with withdrawals (W)
- Failed courses that were retaken
- 0-credit lab courses
- Waivered courses
- Incomplete grades (IP, I)

## Future AI Integration
This tool is designed to be the "Skill" or "Service" that future AI Admin Agents would call to verify student graduation eligibility. The CLI interface can be easily adapted to API endpoints for agentic AI integration.

## Author
Built for CSE226.1 Spring 2026 - Vibe Coding Project
Dr. Nabeel Mohammed

## License
Educational Use Only