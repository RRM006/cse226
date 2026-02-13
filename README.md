# NSU Audit Core System

A command-line tool to automate graduation eligibility verification for North South University (NSU) students. This system validates student transcripts against BSCSE and BSEEE program requirements.

## Project Overview

- **Version**: 1.0
- **Language**: Python 3
- **Project Type**: CSE226 Project 1 - Spring 2026

## Project Structure

```
project_root/
├── src/
│   ├── level1_credit_tally.py       # Level 1: Credit Tally Engine
│   ├── level2_cgpa_calculator.py    # Level 2: CGPA Calculator & Waiver Handler
│   └── level3_audit_engine.py      # Level 3: Audit Engine & Deficiency Reporter
├── data/
│   ├── program_knowledge_BSCSE.md   # BSCSE program requirements
│   ├── program_knowledge_BSEEE.md  # BSEEE program requirements
│   └── transcript_template.csv      # Transcript CSV template
├── tests/
│   ├── level1/
│   │   ├── test_L1_1.csv           # Standard successful student
│   │   ├── test_L1_2.csv           # Mixed grades with failures
│   │   ├── test_L1_3.csv           # Incomplete and withdrawn
│   │   ├── test_L1_4.csv           # Zero-credit labs
│   │   ├── test_edge_all_A.csv     # Edge: All A grades
│   │   ├── test_edge_all_F.csv     # Edge: All F grades
│   │   └── test_edge_mixed_invalid.csv
│   ├── level2/
│   │   ├── test_L2_1.csv           # Standard CGPA calculation
│   │   ├── test_L2_2.csv           # Retake scenario
│   │   ├── test_L2_3.csv           # Course waivers
│   │   ├── test_L2_4.csv           # Complex retakes + waivers + F
│   │   ├── test_edge_borderline_cgpa.csv
│   │   └── test_edge_multiple_retakes.csv
│   └── level3/
│       ├── test_L3_1.csv           # Graduation ready student
│       ├── test_L3_2.csv           # Missing core courses
│       ├── test_L3_3.csv           # Probation status
│       ├── test_L3_4.csv           # Elective trail violation
│       ├── test_edge_bseee_complete.csv
│       ├── test_edge_missing_capstone.csv
│       ├── test_edge_extra_credits.csv
│       ├── test_edge_missing_open_elective.csv
│       ├── test_edge_dual_program_cse_ece.csv
│       ├── test_edge_prerequisite_violation.csv
│       ├── test_edge_eee_power_trail.csv
│       ├── test_edge_single_elective_trail.csv
│       ├── test_edge_ai_arch_trails.csv
│       └── test_edge_open_elective.csv
├── README.md
└── testing_plan.md
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

## Program Support Matrix

| Feature | BSCSE | BSEEE |
|---------|-------|-------|
| University Core (34 credits) | ✓ | ✓ |
| SEPS Core (38 credits) | ✓ | ✓ |
| Major Core | CSE courses | EEE courses |
| Capstone Projects | CSE299/499A/499B | EEE299/499A/499B |
| Specialized Electives | 6 trails | 5 trails |
| Open Elective | ✓ | ✓ |
| Waivers (ENG102, MAT116) | ✓ | ✓ |

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
python src/level1_credit_tally.py tests/level1/test_L1_1.csv
python src/level2_cgpa_calculator.py tests/level2/test_L2_1.csv
python src/level3_audit_engine.py tests/level3/test_L3_1.csv data/program_knowledge_BSCSE.md
```

See `testing_plan.md` for detailed test strategy and coverage information.

## Notes

- All transcript CSVs must include: `course_code`, `course_name`, `credits`, `grade`, `semester`
- Grade names are case-insensitive (accepts 'A', 'a', 'A-', etc.)
- Program knowledge files define requirements in markdown format
- System supports both BSCSE and BSEEE programs with unified audit engine
