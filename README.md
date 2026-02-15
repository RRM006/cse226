# NSU Audit Core System

A command-line tool to automate graduation eligibility verification for North South University (NSU) students. This system validates student transcripts against BSCSE, BSEEE, and LL.B Honors program requirements.

## Project Overview

- **Version**: 2.0
- **Language**: Python 3
- **Project Type**: CSE226 Project 1 - Spring 2026

## Project Structure

```
project_root/
├── src/
│   ├── level1_credit_tally.py       # Level 1: Credit Tally Engine
│   ├── level2_cgpa_calculator.py    # Level 2: CGPA Calculator & Waiver Handler
│   └── level3_audit_engine.py       # Level 3: Audit Engine & Deficiency Reporter
├── data/
│   ├── program_knowledge_BSCSE.md   # BSCSE program requirements
│   ├── program_knowledge_BSEEE.md   # BSEEE program requirements
│   ├── program_knowledge_LLB.md     # LL.B Honors program requirements
│   └── transcript_template.csv      # Transcript CSV template
├── tests/
│   ├── level1/
│   │   ├── bscse/
│   │   │   ├── test_bscse_standard.csv
│   │   │   ├── test_bscse_mixed_grades.csv
│   │   │   ├── test_bscse_with_failures.csv
│   │   │   ├── test_bscse_all_A.csv
│   │   │   └── test_bscse_invalid_grades.csv
│   │   ├── bseee/
│   │   │   ├── test_bseee_standard.csv
│   │   │   └── test_bseee_with_failures.csv
│   │   └── law/
│   │       ├── test_law_standard.csv
│   │       └── test_law_ged_incomplete.csv
│   ├── level2/
│   │   ├── bscse/
│   │   │   ├── test_bscse_standard.csv
│   │   │   └── test_bscse_retakes.csv
│   │   ├── bseee/
│   │   │   └── test_bseee_standard.csv
│   │   └── law/
│   │       └── test_law_standard.csv
│   └── level3/
│       ├── bscse/
│       │   ├── test_bscse_complete.csv
│       │   ├── test_bscse_missing_electives.csv
│       │   └── test_bscse_probation.csv
│       ├── bseee/
│       │   └── test_bseee_complete.csv
│       └── law/
│           ├── test_law_complete.csv
│           ├── test_law_missing_dissertation.csv
│           └── test_law_probation.csv
├── README.md
├── TESTME.md
├── testing_plan.md
└── version2.0.md
```

## Requirements

- Python 3.6+
- No external dependencies (uses built-in `csv` module)

## Installation

No installation required. Clone or download the project and run directly.

## Usage

### Level 1: Credit Tally Engine

Calculates total valid earned credits from transcript.

```bash
python src/level1_credit_tally.py tests/level1/test_L1_1.csv
```

For Law program:
```bash
python src/level1_credit_tally.py tests/level1/law/test_L1_law_standard.csv
```

### Level 2: CGPA Calculator

Calculates weighted CGPA with retake and waiver handling.

```bash
python src/level2_cgpa_calculator.py tests/level2/test_L2_1.csv
```

The tool will prompt for waiver information:
```
Enter waived courses (comma-separated course codes, or press Enter for NONE): ENG102,MAT116
```

### Level 3: Audit Engine

Performs comprehensive graduation audit against program requirements.

```bash
python src/level3_audit_engine.py tests/level3/test_L3_1.csv data/program_knowledge_BSCSE.md
```

For BSEEE program:
```bash
python src/level3_audit_engine.py tests/level3/test_edge_bseee_complete.csv data/program_knowledge_BSEEE.md
```

For Law program:
```bash
python src/level3_audit_engine.py tests/level3/law/test_L3_law_complete.csv data/program_knowledge_LLB.md
```

## Program Support Matrix

| Feature | BSCSE | BSEEE | LL.B Honors |
|---------|-------|-------|--------------|
| University Core (34 credits) | ✓ | ✓ | - |
| GED (25 credits) | - | - | ✓ (Group 1 + Group 2) |
| SEPS Core (38 credits) | ✓ | ✓ | - |
| Major Core | CSE courses | EEE courses | 27 Law courses |
| Capstone Projects | CSE299/499A/499B | EEE299/499A/499B | LLB407 Dissertation |
| Specialized Electives | 6 trails | 5 trails | 19 options (pool) |
| Open Elective | ✓ | ✓ | - |
| Waivers (ENG102, MAT116) | ✓ | ✓ | ENG102 |

### BSCSE Elective Trails
- Algorithms and Computation
- Software Engineering
- Networks
- Computer Architecture and VLSI
- Artificial Intelligence
- Bioinformatics

### BSEEE Elective Trails
- Solid State Electronics
- Power System Engineering
- Communications Engineering
- Robotics and Intelligence System
- Telecommunication System

### LL.B Honors Program
- **GED Group 1**: 16 credits (5 required courses + 1 science)
- **GED Group 2**: 9 credits (choose 3 from 11)
- **Core Program**: 81 credits (27 courses by year)
- **Electives**: 24 credits (choose 8 from 19)
- **Capstone**: LLB407 Law Dissertation (required)

## NSU Grading Scale

| Grade | Points |
|-------|--------|
| A | 4.0 |
| A- | 3.7 |
| B+ | 3.3 |
| B | 3.0 |
| B- | 2.7 |
| C+ | 2.3 |
| C | 2.0 |
| C- | 1.7 |
| D+ | 1.3 |
| D | 1.0 |
| F | 0.0 |

### Grades Excluded from CGPA
- **F**: Failure (0.0 points, no credits)
- **I**: Incomplete (0.0 points, no credits)
- **W**: Withdrawal (0.0 points, no credits)
- **X**: Marked (0.0 points, no credits)

## Academic Standing

| CGPA Range | Standing |
|------------|----------|
| 3.80 - 4.00 | Summa Cum Laude |
| 3.65 - 3.79 | Magna Cum Laude |
| 3.50 - 3.64 | Cum Laude |
| 3.00 - 3.49 | First Class (Good Standing) |
| 2.50 - 2.99 | Second Class (Good Standing) |
| 2.00 - 2.49 | Third Class (Good Standing) |
| Below 2.00 | PROBATION |

## Edge Cases Handled

- 0-credit lab courses (counted as completion, not toward credit total)
- Course retakes (best grade used for CGPA)
- Course waivers (excluded from CGPA calculation)
- Multiple invalid grades (F, I, W, X)
- Prerequisite violations
- Elective trail concentration requirements
- Probation status detection
- Missing capstone projects

## Testing

Run individual test files:
```bash
# BSCSE Tests
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_standard.csv
python src/level2_cgpa_calculator.py tests/level2/bscse/test_bscse_standard.csv
python src/level3_audit_engine.py tests/level3/bscse/test_bscse_complete.csv data/program_knowledge_BSCSE.md

# BSEEE Tests
python src/level1_credit_tally.py tests/level1/bseee/test_bseee_standard.csv
python src/level3_audit_engine.py tests/level3/bseee/test_bseee_complete.csv data/program_knowledge_BSEEE.md

# Law Tests
python src/level1_credit_tally.py tests/level1/law/test_law_standard.csv
python src/level3_audit_engine.py tests/level3/law/test_law_complete.csv data/program_knowledge_LLB.md
```

See `testing_plan.md` for detailed test strategy and coverage information.

## Notes

- All transcript CSVs must include: `course_code`, `course_name`, `credits`, `grade`, `semester`
- Grade names are case-insensitive (accepts 'A', 'a', 'A-', etc.)
- Program knowledge files define requirements in markdown format
- System supports both BSCSE and BSEEE programs with unified audit engine
