# NSU Audit Core System v2.0
## Product Requirements Document - Complete Specification

---

**Document Information:**
- **Project**: NSU Department Admin Audit Core
- **Version**: 2.0
- **Date**: February 15, 2026
- **Timeline**: 1 Day
- **Author**: NSU Development Team
- **Status**: Ready for Implementation

---

## Executive Summary

NSU Audit Core v2.0 is a **multi-department graduation audit system** that validates student transcripts against program requirements for North South University. This version expands from v1.0 (Engineering only) to support **three programs across two departments**: BSCSE, BSEEE (Engineering), and LL.B Honors (Law).

**Core Objectives:**
1. Automate graduation eligibility verification
2. Enforce NSU academic policies programmatically
3. Support multiple departments with different rules
4. Generate clear, actionable audit reports
5. Serve as foundation for AI agent integration

**Key Enhancements from v1.0:**
- ✅ Multi-department support (Engineering + Law)
- ✅ Law program validation (GED groups, dissertation)
- ✅ Complete academic policy implementation
- ✅ Modular architecture (separate files per level)
- ✅ Enhanced test coverage (59 total tests)

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Programs Supported](#2-programs-supported)
3. [Law Program Requirements](#3-law-program-requirements)
4. [Academic Policies](#4-academic-policies)
5. [System Architecture](#5-system-architecture)
6. [Level 1: Credit Tally Engine](#6-level-1-credit-tally-engine)
7. [Level 2: CGPA Calculator](#7-level-2-cgpa-calculator)
8. [Level 3: Audit Engine](#8-level-3-audit-engine)
9. [Knowledge Base Format](#9-knowledge-base-format)
10. [Test Strategy](#10-test-strategy)
11. [Data Formats](#11-data-formats)
12. [Implementation Guide](#12-implementation-guide)
13. [Success Criteria](#13-success-criteria)
14. [Deliverables](#14-deliverables)

---

## 1. System Overview

### 1.1 Purpose

Build a **precise, reliable graduation audit engine** that:
- Validates transcripts against program requirements
- Calculates CGPA with policy enforcement
- Identifies graduation deficiencies
- Supports multiple programs and departments
- Provides structured, clear output

### 1.2 Scope

**Programs**: 3 (BSCSE, BSEEE, LL.B Honors)  
**Departments**: 2 (Engineering, Law)  
**Total Credits**: 130 per program  
**Policies**: All NSU academic policies  
**Output**: Terminal-based (L1, L2, L3 format)

### 1.3 Users

- **Primary**: Department administrators
- **Secondary**: Academic advisors
- **Tertiary**: Faculty and students
- **Future**: AI administrative agents

### 1.4 Technical Stack

- **Language**: Python 3.8+
- **Libraries**: Built-in only (csv, os, sys)
- **Files**: Markdown knowledge base, CSV transcripts
- **Platform**: Cross-platform (Windows, Mac, Linux)

---

## 2. Programs Supported

### 2.1 Program Comparison

| Feature | BSCSE | BSEEE | LL.B Honors |
|---------|-------|-------|-------------|
| Department | Engineering | Engineering | Law |
| Total Credits | 130 | 130 | 130 |
| University Core | 34 | 34 | 25 (GED) |
| Program Core | 80 | 80 | 81 |
| Electives | 12 | 12 | 24 |
| Capstone | 3 courses | 3 courses | 1 (Dissertation) |
| Elective Model | Trail-based | Trail-based | Pool-based |
| Year Structure | No | No | Yes (Year 1-4) |

### 2.2 Engineering Programs (BSCSE, BSEEE)

**Credit Structure (130 total):**
- University Core: 34 credits
- SEPS Core: 38 credits
- Major Core: 42 credits
- Capstone: 4 credits (3 courses)
- Major Electives: 9 credits
- Open Electives: 3 credits

**Elective Model**: Trail-based
- Must complete 2+ courses from ONE trail
- BSCSE: 6 trails (AI, Networks, Software, etc.)
- BSEEE: 5 trails (Power, Communications, etc.)

**Capstone**: 3-part project
- CSE299/EEE299: Junior Design (1 cr)
- CSE499A/EEE499A: Senior Design I (1.5 cr)
- CSE499B/EEE499B: Senior Design II (1.5 cr)

### 2.3 Law Program (LL.B Honors)

**Credit Structure (130 total):**
- GED Group 1: 16 credits (5 courses)
- GED Group 2: 9 credits (3 from 11)
- Core Program: 81 credits (27 courses)
- Electives: 24 credits (8 from 19)

**Elective Model**: Pool-based
- Select any 8 from 19 available
- No trail/concentration requirement

**Capstone**: Dissertation
- LLB407: Law Dissertation (3 cr)
- Required in Year 4, Semester 2
- Prerequisites: LLB404 + 100 credits

**Year Structure**: Organized by academic year
- Year 1: Foundation (GED + 2 core)
- Year 2: Core development (11 courses)
- Year 3: Advanced core (7 courses)
- Year 4: Capstone + electives (7 courses)

---

## 3. Law Program Requirements

### 3.1 GED Requirements (25 Credits)

#### GED Group 1 (16 Credits - All Required)

**Fixed Courses (4 courses, 12 credits):**
```
ENG102: Introduction to Composition (3)
ENG103: Intermediate Composition (3)
BEN205: Bangla Language (3)
HIS103: Emergence of Bangladesh (3)
```

**Science (Choose 1, 4 credits):**
```
PBH101: Public Health (4)
CHE101: Chemistry I (4)
PHY107: Physics I (4)
BIO103: Biology (4)
```

**Validation**:
- Total: 5 courses, 16 credits
- All 4 fixed courses required
- Exactly 1 science course

#### GED Group 2 (9 Credits - Choose 3)

**Available Courses (11 options):**
```
ECO101: Principles of Economics (3)
ECO104: Principles of Macroeconomics (3)
POL101: Introduction to Political Science (3)
POL104: Government and Politics in Bangladesh (3)
ENG111: Public Speaking (3)
PHI101: Introduction to Philosophy (3)
ENV203: Environmental Science (3)
GEO205: Introduction to Geography (3)
BUS112: Principles of Management (3)
SOC101: Introduction to Sociology (3)
ANT101: Introduction to Anthropology (3)
```

**Alternative Rules**:
- ECO101 OR ECO104 (not both)
- POL101 OR POL104 (not both)
- ENV203 OR GEO205 (not both)
- SOC101 OR ANT101 (not both)

**Validation**:
- Exactly 3 courses required
- Any combination (respecting alternatives)
- No duplicates
- Total: 9 credits

### 3.2 Core Program (81 Credits - All Required)

#### Year 1 (6 Credits - 2 Courses)

```
LLB101: Introduction to the Legal System and Legal Process (3)
LLB102: Constitutional Laws of Bangladesh (3)
```

#### Year 2 (27 Credits - 9 Courses)

**Semester 1 (15 credits):**
```
LLB103: The Law of Contract (3)
LLB104: The Law of Torts (3)
LLB201: Muslim Family and Property Law (3)
LLB202: Law of Crime (3)
LLB203: Law of Equity, Trust & Specific Relief (3)
```

**Semester 2 (18 credits):**
```
LLB204: Company Law (3)
LLB205: Laws regarding Transfer of Property (3)
LLB206: Administrative Law (3)
LLB207: Law of Registration & Limitation (3)
LLB208: Jurisprudence and Legal Theory (3)
LLB209: Legal Professional Ethics (3)
```

#### Year 3 (21 Credits - 7 Courses)

**Semester 1 (12 credits):**
```
LLB301: Law of Evidence (3)
LLB302: Law of Criminal Procedure (Part 1) (3)
LLB304: Law of Civil Procedure (Part 1) (3)
LLB306: Law of Labour and Employment (3)
```

**Semester 2 (9 credits):**
```
LLB303: Law of Criminal Procedure (Part 2) (3)
LLB305: Law of Civil Procedure (Part 2) (3)
LLB307: Land Law of Bangladesh (3)
```

#### Year 4 (27 Credits - 7 Courses)

**Semester 1 (12 credits):**
```
LLB401: Alternative Dispute Resolution Methods (3)
LLB402: Legal Drafting (Civil and Criminal) & Conveyance (3)
LLB403: Public International Laws (3)
LLB404: Legal Research (3)
```

**Semester 2 (9 credits):**
```
LLB405: Trial and Advocacy (3)
LLB406: Hindu and Christian Family Law (3)
LLB407: Law Dissertation (3) *** REQUIRED - CAPSTONE ***
```

**Validation**:
- All 27 courses required
- LLB407 is mandatory for graduation
- Total: 81 credits

### 3.3 Electives (24 Credits - Choose 8)

**Available Electives (19 courses):**
```
LLB411: Clinical Legal Education and Community Legal Services (3)
LLB412: Fiscal & Taxation Law (3)
LLB413: Environmental Law (3)
LLB414: Cyber, Media & Telecommunication Law (3)
LLB415: Special Penal Laws (3)
LLB416: The Intellectual Property Law (3)
LLB417: Banking and Foreign Exchange Law (3)
LLB418: Criminology and Penology (3)
LLB419: International Criminal Law (3)
LLB420: Medical Jurisprudence and Forensic Law (3)
LLB421: Corporate Insolvency Law (3)
LLB422: Election Laws (3)
LLB423: Law and Globalization (3)
LLB424: Maritime, Oceans, and Coastal Law (3)
LLB425: Anti-corruption and Anti-money Laundering Law (3)
LLB426: Mercantile Law (3)
LLB427: Foreign Investment Law (3)
LLB428: Public Demands Recovery and Financial Institutions' Loan Recovery Law (3)
LLB429: Public Private Partnership Law (3)
```

**Validation**:
- Exactly 8 courses required
- Any combination allowed
- No trail requirement
- Total: 24 credits

### 3.4 Prerequisites

**Direct Prerequisites:**
```
LLB101 → LLB103, LLB104
LLB102 → LLB202, LLB206
LLB103 → LLB304, LLB305
LLB202 → LLB302, LLB303
LLB404 → LLB407
```

**Special Requirements for LLB407:**
- Must complete LLB404 (Legal Research)
- Must have 100+ credits completed
- Can only be taken in Year 4

### 3.5 Year Progression Rules

**Year 1 Requirements:**
- Complete all GED Group 1 by end of Year 1
- Complete LLB101, LLB102 by end of Year 1
- Cannot proceed to Year 2 without Year 1 foundation

**Year 2 Requirements:**
- LLB101 must be complete before LLB103, LLB104
- LLB102 must be complete before LLB202, LLB206

**Year 3 Requirements:**
- LLB202 must be complete before LLB302, LLB303
- LLB103 must be complete before LLB304, LLB305
- Can start electives (recommended 4 in Year 3)

**Year 4 Requirements:**
- Must have 100+ credits before LLB407
- Must complete LLB404 before LLB407
- LLB407 must be in final semester

---

## 4. Academic Policies

### 4.1 Grading System

**Grade Scale:**
```
A   = 4.0  (93-100)
A-  = 3.7  (90-92)
B+  = 3.3  (87-89)
B   = 3.0  (83-86)
B-  = 2.7  (80-82)
C+  = 2.3  (77-79)
C   = 2.0  (73-76)
C-  = 1.7  (70-72)
D+  = 1.3  (67-69)
D   = 1.0  (60-66)
F   = 0.0  (Below 60)
```

**Invalid Grades (Excluded from CGPA):**
```
F = Failure (0.0 points, no credits earned)
I = Incomplete (0.0 points, no credits)
W = Withdrawal (0.0 points, no credits)
X = Marked (0.0 points, no credits)
```

### 4.2 CGPA Calculation

**Formula:**
```
CGPA = Σ(Grade Point × Credits) / Σ(Credits for valid grades)
```

**Rules:**
1. Only grades A through D count
2. F, I, W, X excluded from calculation
3. Waived courses excluded
4. Best grade used for retakes
5. Report with 2 decimal places

**Example:**
```
Course 1: A (4.0) × 3 cr = 12.0
Course 2: B+ (3.3) × 3 cr = 9.9
Course 3: C (2.0) × 4 cr = 8.0
Total: 29.9 / 10 = 2.99 CGPA
```

### 4.3 Retake Policy

**Eligibility:**
- Can retake any course with grade B or lower
- Cannot retake A or A-

**CGPA Calculation:**
- Best grade counts toward CGPA
- All attempts appear on transcript
- Lower grades show 0.0 grade points

**Attempt Limits:**
- Maximum 3 attempts per course (normal)
- 4th attempt requires Vice-Chancellor approval
- System must flag 4th attempts

**Implementation:**
```python
def process_retakes(courses):
    retakes = group_by_course_code(courses)
    for code, attempts in retakes.items():
        if len(attempts) > 1:
            best = max(attempts, key=lambda x: grade_points[x.grade])
            for attempt in attempts:
                if attempt != best:
                    attempt.counted = False
                    attempt.grade_points = 0.0
        
        if len(attempts) >= 4:
            flag_vc_approval(code)
```

### 4.4 Course Exclusion Policy

**Eligibility:**
- Can exclude ONLY after 80% credits completed
- Engineering: 104 credits (80% of 130)
- Law: 104 credits (80% of 130)

**Restrictions:**
- CANNOT exclude core courses
- CANNOT exclude to avoid probation
- CANNOT exclude to change departments

**After Department Change:**
- Can exclude courses not required by new program

**Implementation:**
```python
def validate_exclusion(student, course):
    earned = calculate_earned_credits(student)
    required = get_program_credits(student.program)
    
    if earned < (required * 0.80):
        return False, "Need 80% credits (104/130)"
    
    if is_core_course(course, student.program):
        return False, "Cannot exclude core courses"
    
    if student.cgpa < 2.00:
        return False, "Cannot exclude on probation"
    
    return True, "Exclusion approved"
```

### 4.5 Waiver Policy

**Common Waivers:**
- ENG102: Introduction to Composition
- MAT116: Pre-Calculus

**Rules:**
- Waived courses don't appear on transcript
- Waived credits COUNT toward degree
- Waived courses EXCLUDED from CGPA
- Admin must input waiver info

**Prompt:**
```
Enter waived courses (comma-separated, or NONE): ENG102,MAT116
```

### 4.6 Academic Standing & Probation

**Academic Standing:**
```
CGPA 3.80-4.00 → Summa Cum Laude
CGPA 3.65-3.79 → Magna Cum Laude
CGPA 3.50-3.64 → Cum Laude
CGPA 3.00-3.49 → First Class (Good Standing)
CGPA 2.50-2.99 → Second Class (Good Standing)
CGPA 2.00-2.49 → Third Class (Good Standing)
CGPA < 2.00 → PROBATION
```

**Probation Rules:**
- Triggered when CGPA < 2.00
- Student has 3 semesters to raise CGPA
- Dismissed after 3 semesters if still < 2.00
- Cannot graduate on probation

**Implementation:**
```python
def check_academic_standing(student):
    if student.cgpa < 2.00:
        if student.probation_semesters >= 3:
            return "DISMISSED", "Excluded from University"
        else:
            semester = student.probation_semesters + 1
            return "PROBATION", f"Semester {semester} of 3"
    elif student.cgpa >= 3.80:
        return "SUMMA_CUM_LAUDE", "Summa Cum Laude"
    # ... other standings
```

### 4.7 Graduation Requirements

**Minimum Requirements:**
- Total Credits: 130
- Minimum CGPA: 2.00
- Academic Standing: Good (not probation)
- All core courses completed
- All capstone courses completed
- No outstanding prerequisites

**Program-Specific:**
- Engineering: All 3 capstone courses
- Law: LLB407 (Dissertation) required

---

## 5. System Architecture

### 5.1 Directory Structure

```
nsu_audit_core/
│
├── README.md
├── TESTING.md
├── NSU_Audit_Core_PRD_v2.0.md
│
├── src/
│   ├── level1/                      # Credit Tally Engine
│   │   ├── __init__.py
│   │   ├── credit_tally_engine.py  # Main entry
│   │   ├── grade_validator.py      # Grade validation
│   │   ├── credit_calculator.py    # Credit calculation
│   │   └── program_detector.py     # Detect program type
│   │
│   ├── level2/                      # CGPA Calculator
│   │   ├── __init__.py
│   │   ├── cgpa_calculator.py      # Main entry
│   │   ├── retake_processor.py     # Handle retakes
│   │   ├── waiver_handler.py       # Process waivers
│   │   ├── exclusion_validator.py  # Validate exclusions
│   │   └── standing_calculator.py  # Academic standing
│   │
│   ├── level3/                      # Audit Engine
│   │   ├── __init__.py
│   │   ├── audit_engine.py         # Main entry
│   │   ├── knowledge_loader.py     # Load requirements
│   │   ├── requirement_checker.py  # Validate requirements
│   │   ├── prerequisite_validator.py # Check prerequisites
│   │   ├── deficiency_reporter.py  # Generate reports
│   │   └── policy_enforcer.py      # Enforce policies
│   │
│   └── shared/                      # Shared utilities
│       ├── __init__.py
│       ├── transcript_parser.py    # Parse CSV
│       ├── constants.py            # Constants
│       └── utils.py                # Helper functions
│
├── data/
│   ├── programs/
│   │   ├── program_knowledge_BSCSE.md
│   │   ├── program_knowledge_BSEEE.md
│   │   └── program_knowledge_LLB.md
│   │
│   └── policies/
│       ├── ged_requirements.md
│       ├── prerequisite_graph_BSCSE.md
│       ├── prerequisite_graph_BSEEE.md
│       └── prerequisite_graph_LLB.md
│
└── tests/
    ├── level1/
    │   ├── engineering/
    │   │   ├── test_L1_1.csv
    │   │   └── ... (10 tests)
    │   └── law/
    │       ├── test_L1_law_standard.csv
    │       └── ... (8 tests)
    │
    ├── level2/
    │   ├── engineering/
    │   │   └── ... (8 tests)
    │   └── law/
    │       └── ... (8 tests)
    │
    └── level3/
        ├── engineering/
        │   └── ... (15 tests)
        └── law/
            └── ... (10 tests)
```

### 5.2 Module Dependencies

```
level1_credit_tally_engine
    ├── transcript_parser (shared)
    ├── grade_validator
    ├── credit_calculator
    ├── program_detector
    └── constants (shared)

level2_cgpa_calculator
    ├── transcript_parser (shared)
    ├── retake_processor
    ├── waiver_handler
    ├── exclusion_validator
    ├── standing_calculator
    └── constants (shared)

level3_audit_engine
    ├── transcript_parser (shared)
    ├── knowledge_loader
    ├── requirement_checker
    ├── prerequisite_validator
    ├── deficiency_reporter
    ├── policy_enforcer
    └── constants (shared)
```

---

## 6. Level 1: Credit Tally Engine

### 6.1 Objective

Calculate total valid earned credits from transcript, excluding invalid grades and handling program-specific requirements.

### 6.2 Functional Requirements

**FR1.1: Transcript Parsing**
- Read CSV file with course_code, course_name, credits, grade, semester
- Validate CSV format
- Handle missing or malformed data

**FR1.2: Program Detection**
- Auto-detect program from course codes
- BSCSE: Courses with CSE prefix
- BSEEE: Courses with EEE prefix
- LLB: Courses with LLB prefix
- Allow manual override

**FR1.3: Grade Validation**
- Validate letter grades (A, A-, B+, B, B-, C+, C, C-, D+, D, F, I, W, X)
- Case-insensitive
- Flag invalid grades

**FR1.4: Credit Calculation**
- Sum credits for valid grades (A through D)
- Exclude F, I, W, X from credit total
- Handle 0-credit labs correctly
- Track attempted vs. earned credits

**FR1.5: Law-Specific Validation**
- Validate GED Group 1 (5 courses, 16 credits)
- Validate GED Group 2 (3 from 11, 9 credits)
- Check alternative course conflicts
- Category breakdown (GED, Core, Electives)

**FR1.6: Output Generation**
- Structured output with sections
- Credit breakdown by category
- List excluded courses with reasons
- Clear pass/fail status

### 6.3 Implementation Pseudocode

```python
def credit_tally_engine(transcript_csv, program=None):
    # Parse transcript
    courses = parse_csv(transcript_csv)
    
    # Detect program
    if program is None:
        program = detect_program(courses)
    
    # Validate grades
    for course in courses:
        course.valid_grade = validate_grade(course.grade)
    
    # Calculate credits
    earned_credits = 0
    excluded_courses = []
    
    for course in courses:
        if course.grade in ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D']:
            earned_credits += course.credits
        else:
            excluded_courses.append(course)
    
    # Program-specific validation
    if program == 'LLB':
        ged_result = validate_law_ged(courses)
        category_breakdown = calculate_law_categories(courses)
    else:
        category_breakdown = calculate_eng_categories(courses)
    
    # Generate output
    print_credit_report(earned_credits, excluded_courses, category_breakdown)
```

### 6.4 Output Format

```
=== NSU AUDIT CORE - LEVEL 1 ===
Student: [Auto-detect or prompt]
Program: LL.B Honors
Processing: test_L1_law_standard.csv

CREDIT ANALYSIS:
Total Courses Attempted: 35
Valid Courses (A-D): 32
Excluded Courses: 3
  ├─ LLB201 (F) - 3 credits [FAILED]
  ├─ ECO101 (W) - 3 credits [WITHDRAWN]
  └─ LLB304 (I) - 3 credits [INCOMPLETE]

CREDITS BY CATEGORY:
GED Group 1:    16 / 16 credits  ✓ COMPLETE
  ├─ ENG102 (3), ENG103 (3), BEN205 (3)
  ├─ HIS103 (3), BIO103 (4)
  
GED Group 2:     9 /  9 credits  ✓ COMPLETE
  ├─ ECO101 (3), POL101 (3), PHI101 (3)
  
Core Program:   54 / 81 credits  ⚠ IN PROGRESS
  ├─ Year 1:     6 /  6 credits  ✓
  ├─ Year 2:    24 / 27 credits  ⚠
  ├─ Year 3:    21 / 21 credits  ✓
  └─ Year 4:     3 / 27 credits  ⚠
  
Electives:      12 / 24 credits  ⚠ IN PROGRESS
  ├─ Completed: 4 courses
  └─ Remaining: 4 courses

Total Earned Credits: 91 / 130

RESULT: ⚠ IN PROGRESS (91 credits completed)
```

### 6.5 Test Cases (Level 1)

**Engineering Tests (10):**
1. test_L1_1.csv - Standard successful student
2. test_L1_2.csv - Mixed grades with failures
3. test_L1_3.csv - Incomplete and withdrawn
4. test_L1_4.csv - Zero-credit labs
5. test_edge_all_A.csv - All A grades
6. test_edge_all_F.csv - All F grades
7. test_edge_mixed_invalid.csv - Mixed invalid grades
8-10. Additional edge cases

**Law Tests (8):**
1. test_L1_law_standard.csv - Standard Law student
2. test_L1_law_ged_violation.csv - GED Group 2 incomplete
3. test_L1_law_incomplete.csv - Courses with I, W grades
4. test_L1_law_edge_cases.csv - Multiple edge cases
5. test_L1_law_year_progression.csv - Year tracking
6. test_L1_law_ged_group_selection.csv - GED validation
7. test_L1_law_science_selection.csv - Science course check
8. test_L1_law_credits_by_year.csv - Year breakdown

---

## 7. Level 2: CGPA Calculator

### 7.1 Objective

Calculate weighted CGPA with retake handling, waiver processing, course exclusion, and academic standing determination.

### 7.2 Functional Requirements

**FR2.1: CGPA Calculation**
- Calculate: CGPA = Σ(Grade Points × Credits) / Σ(Credits)
- Use NSU grade point scale
- Exclude F, I, W, X from calculation
- Report with 2 decimal precision

**FR2.2: Retake Processing**
- Identify duplicate course codes
- Use best grade for CGPA
- Track number of attempts
- Flag 4th attempts for VC approval

**FR2.3: Waiver Handling**
- Prompt for waiver input
- Parse comma-separated list
- Validate waiver eligibility (ENG102, MAT116)
- Exclude from CGPA, count for credits

**FR2.4: Course Exclusion**
- Validate 80% credit requirement
- Prevent core course exclusion
- Prevent exclusion on probation
- Show excluded courses

**FR2.5: Academic Standing**
- Calculate standing from CGPA
- Check probation status
- Track probation semesters
- Determine honors level

**FR2.6: Output Generation**
- Show calculation breakdown
- List retakes with improvements
- Show waivers applied
- Report final CGPA and standing

### 7.3 Implementation Pseudocode

```python
def cgpa_calculator(transcript_csv, program=None):
    # Parse transcript
    courses = parse_csv(transcript_csv)
    
    # Prompt for waivers
    waivers = input("Enter waived courses (or NONE): ")
    waived_courses = parse_waivers(waivers)
    
    # Process retakes
    retake_info = process_retakes(courses)
    
    # Calculate CGPA
    total_grade_points = 0
    total_credits = 0
    
    for course in courses:
        if course.code in waived_courses:
            continue  # Exclude waived courses
        
        if course.counted_for_cgpa:  # Best grade for retakes
            if course.grade in VALID_GRADES:
                points = GRADE_POINTS[course.grade]
                total_grade_points += points * course.credits
                total_credits += course.credits
    
    cgpa = total_grade_points / total_credits if total_credits > 0 else 0.0
    cgpa = round(cgpa, 2)
    
    # Determine academic standing
    standing = calculate_standing(cgpa)
    
    # Check probation
    probation_status = check_probation(cgpa, probation_semesters)
    
    # Generate output
    print_cgpa_report(cgpa, standing, retake_info, waived_courses)
```

### 7.4 Output Format

```
=== NSU AUDIT CORE - LEVEL 2 ===
Student: [Auto-detect or prompt]
Program: LL.B Honors
Processing: test_L2_law_retakes.csv

Enter waived courses (comma-separated, or NONE): ENG102

CGPA CALCULATION:

Waivers Applied: 1 course (3 credits)
  └─ ENG102: Introduction to Composition (3 credits)

Retakes Processed: 3 courses
  ├─ LLB103: C (2.0) → A- (3.7)  ✓ IMPROVED (+1.7)
  ├─ LLB201: F (0.0) → B (3.0)   ✓ IMPROVED (+3.0)
  └─ LLB208: B- (2.7) → B+ (3.3) ✓ IMPROVED (+0.6)

Retake Warnings:
  [None - all within 3 attempts]

Calculation Details:
  Total Grade Points:    402.6
  Total Credits Counted: 127
  Excluded from CGPA:    3 (waivers)
  
  CGPA = 402.6 / 127 = 3.17

ACADEMIC STANDING:
  CGPA:        3.17
  Standing:    First Class (Good Standing)
  Honors:      None
  Probation:   No
  Status:      ✓ GOOD STANDING

RESULT: ✓ PASSED (CGPA = 3.17)
```

### 7.5 Test Cases (Level 2)

**Engineering Tests (8):**
1. test_L2_1.csv - Standard CGPA
2. test_L2_2.csv - Retake scenario
3. test_L2_3.csv - Course waivers
4. test_L2_4.csv - Complex: retakes + waivers + F
5. test_edge_borderline_cgpa.csv - CGPA = 2.00
6. test_edge_multiple_retakes.csv - Many retakes
7-8. Additional edge cases

**Law Tests (8):**
1. test_L2_law_cgpa_standard.csv - Standard Law CGPA
2. test_L2_law_retakes.csv - Multiple retakes
3. test_L2_law_waivers.csv - Waiver handling
4. test_L2_law_probation.csv - CGPA < 2.00
5. test_L2_law_exclusion.csv - Course exclusion
6. test_L2_law_excessive_retakes.csv - 4th attempt
7. test_L2_law_standing_calculation.csv - All standings
8. test_L2_law_borderline_cgpa.csv - CGPA = 2.00

---

## 8. Level 3: Audit Engine

### 8.1 Objective

Perform comprehensive graduation audit against program requirements, identify deficiencies, check prerequisites, and determine graduation eligibility.

### 8.2 Functional Requirements

**FR3.1: Knowledge Base Loading**
- Load program requirements from markdown
- Parse categories and credit requirements
- Load prerequisite graph
- Cache for performance

**FR3.2: Requirement Validation**
- Match completed courses against requirements
- Check category-wise credits
- Validate core courses
- Validate electives

**FR3.3: Law-Specific Validation**
- GED Group 1 & 2 compliance
- Year-wise core completion
- 8 electives from 19 available
- Dissertation (LLB407) completion

**FR3.4: Engineering-Specific Validation**
- University Core (34 cr)
- SEPS Core (38 cr)
- Major Core (42 cr)
- Trail-based electives (9 cr)
- Capstone sequence (4 cr)

**FR3.5: Prerequisite Checking**
- Load prerequisite graph
- Check all prerequisite relationships
- Flag violations (critical vs. warning)
- Special check for LLB407 (LLB404 + 100 cr)

**FR3.6: Policy Enforcement**
- Check academic standing
- Verify no probation status
- Validate all policies from Level 2
- Check graduation eligibility

**FR3.7: Deficiency Reporting**
- Identify missing courses by category
- Calculate missing credits
- Provide actionable recommendations
- Estimate completion time

**FR3.8: Graduation Determination**
- PASS: All requirements met, CGPA ≥ 2.00
- FAIL: Missing requirements or CGPA < 2.00
- List specific reasons for failure

### 8.3 Implementation Pseudocode

```python
def audit_engine(transcript_csv, knowledge_base_md, program):
    # Parse transcript
    courses = parse_csv(transcript_csv)
    
    # Load requirements
    requirements = load_knowledge_base(knowledge_base_md)
    prerequisites = load_prerequisite_graph(program)
    
    # Calculate CGPA (from Level 2)
    cgpa, standing = calculate_cgpa_with_policies(courses)
    
    # Check all requirements
    deficiencies = []
    
    if program == 'LLB':
        # GED validation
        ged1_result = check_ged_group1(courses, requirements)
        ged2_result = check_ged_group2(courses, requirements)
        if not ged1_result.complete:
            deficiencies.extend(ged1_result.missing)
        if not ged2_result.complete:
            deficiencies.extend(ged2_result.missing)
        
        # Core validation by year
        for year in [1, 2, 3, 4]:
            year_result = check_year_core(courses, requirements, year)
            if not year_result.complete:
                deficiencies.extend(year_result.missing)
        
        # Elective validation
        elective_result = check_electives(courses, requirements, needed=8)
        if not elective_result.complete:
            deficiencies.append(f"Need {elective_result.missing_count} more electives")
        
        # Dissertation check
        if 'LLB407' not in [c.code for c in courses]:
            deficiencies.append("LLB407 (Dissertation) REQUIRED")
    
    else:  # Engineering
        # University Core
        core_result = check_university_core(courses, requirements)
        if not core_result.complete:
            deficiencies.extend(core_result.missing)
        
        # SEPS Core
        seps_result = check_seps_core(courses, requirements)
        if not seps_result.complete:
            deficiencies.extend(seps_result.missing)
        
        # Major Core
        major_result = check_major_core(courses, requirements)
        if not major_result.complete:
            deficiencies.extend(major_result.missing)
        
        # Electives (trail-based)
        elective_result = check_trail_electives(courses, requirements)
        if not elective_result.complete:
            deficiencies.extend(elective_result.missing)
        
        # Capstone
        capstone_result = check_capstone(courses, requirements)
        if not capstone_result.complete:
            deficiencies.extend(capstone_result.missing)
    
    # Check prerequisites
    prereq_violations = check_prerequisites(courses, prerequisites)
    
    # Check probation
    if cgpa < 2.00:
        deficiencies.append("CGPA below 2.00 - PROBATION")
    
    # Determine eligibility
    if len(deficiencies) == 0 and cgpa >= 2.00:
        eligible = True
        status = "ELIGIBLE FOR GRADUATION"
    else:
        eligible = False
        status = "NOT ELIGIBLE FOR GRADUATION"
    
    # Generate report
    print_audit_report(
        courses, cgpa, standing, requirements, 
        deficiencies, prereq_violations, eligible, status
    )
```

### 8.4 Output Format

```
=== NSU AUDIT CORE - LEVEL 3 ===
Student: [Auto-detect or prompt]
Program: LL.B Honors
Knowledge Base: program_knowledge_LLB.md
Processing: test_L3_law_missing_core.csv

GRADUATION AUDIT RESULTS:

CREDIT SUMMARY:
  Total Credits:       125 / 130 required
  CGPA:                3.20
  Academic Standing:   First Class (Good Standing)

REQUIREMENT ANALYSIS:

GED Requirements:
  ├─ Group 1 (16 cr):   ✓ COMPLETE
  │   └─ ENG102, ENG103, BEN205, HIS103, BIO103
  └─ Group 2 (9 cr):    ✓ COMPLETE
      └─ ECO101, POL101, PHI101

Core Program (81 cr):   ⚠ INCOMPLETE (78 / 81)
  ├─ Year 1 (6 cr):     ✓ COMPLETE
  │   └─ LLB101, LLB102
  ├─ Year 2 (27 cr):    ✓ COMPLETE
  │   └─ All 9 courses complete
  ├─ Year 3 (21 cr):    ✓ COMPLETE
  │   └─ All 7 courses complete
  └─ Year 4 (27 cr):    ⚠ INCOMPLETE (24 / 27)
      Missing:
        ├─ LLB401: Alternative Dispute Resolution (3 cr)
        ├─ LLB403: Public International Laws (3 cr)
        └─ LLB407: Law Dissertation (3 cr) *** REQUIRED ***

Electives (24 cr):      ✓ COMPLETE
  └─ 8 courses completed

DEFICIENCY REPORT:

Missing Courses: 3 (9 credits)

1. LLB401: Alternative Dispute Resolution Methods
   ├─ Credits: 3
   ├─ Category: Core Year 4
   ├─ Semester: Year 4, Semester 1
   └─ Prerequisites: None

2. LLB403: Public International Laws
   ├─ Credits: 3
   ├─ Category: Core Year 4
   ├─ Semester: Year 4, Semester 1
   └─ Prerequisites: None

3. LLB407: Law Dissertation *** CAPSTONE - CRITICAL ***
   ├─ Credits: 3
   ├─ Category: Core Year 4 (Capstone)
   ├─ Semester: Year 4, Semester 2
   ├─ Prerequisites: LLB404 (✓ Complete), 100 credits (✓ Complete)
   └─ Status: REQUIRED FOR GRADUATION

PREREQUISITE CHECK:
  ✓ No prerequisite violations detected

ACTION ITEMS:

To graduate, you must:
  1. Complete LLB401 (3 credits)
  2. Complete LLB403 (3 credits)
  3. Complete LLB407 - Law Dissertation (3 credits) [REQUIRED]

Total credits needed: 9
Estimated completion: 1 semester

GRADUATION ELIGIBILITY:

RESULT: ❌ NOT ELIGIBLE FOR GRADUATION

Reasons:
  ├─ Missing 3 core courses (9 credits)
  ├─ Dissertation (LLB407) not completed
  └─ Status: Continue enrollment to complete courses

═══════════════════════════════════════════════════════════
```

### 8.5 Test Cases (Level 3)

**Engineering Tests (15):**
1. test_L3_1.csv - Graduation ready
2. test_L3_2.csv - Missing core courses
3. test_L3_3.csv - Probation status
4. test_L3_4.csv - Elective trail violation
5. test_edge_bseee_complete.csv - BSEEE complete
6. test_edge_missing_capstone.csv - No capstone
7. test_edge_extra_credits.csv - Over 130 credits
8. test_edge_missing_open_elective.csv - No open elective
9. test_edge_dual_program_cse_ece.csv - Dual program
10. test_edge_prerequisite_violation.csv - Prereq issue
11. test_edge_eee_power_trail.csv - EEE trail
12. test_edge_single_elective_trail.csv - Trail issue
13. test_edge_ai_arch_trails.csv - Multiple trails
14. test_edge_open_elective.csv - Open elective
15. Additional edge case

**Law Tests (10):**
1. test_L3_law_graduation_ready.csv - Ready to graduate
2. test_L3_law_missing_core.csv - Missing core
3. test_L3_law_ged_incomplete.csv - GED issue
4. test_L3_law_elective_deficiency.csv - Need electives
5. test_L3_law_no_dissertation.csv - No LLB407
6. test_L3_law_prerequisite_violation.csv - Prereq issue
7. test_L3_law_year_progression.csv - Year issue
8. test_L3_law_probation.csv - On probation
9. test_L3_law_dissertation_ineligible.csv - Can't take LLB407
10. test_L3_law_comprehensive.csv - Multiple issues

---

## 9. Knowledge Base Format

### 9.1 Markdown Structure

```markdown
# Program Name
## Program Overview
- Total Credits: X
- Duration: Y years
- Minimum CGPA: Z

## Credit Distribution
### Category Name (X Credits)
- COURSE_CODE: Course Name (Credits)
- ...

### Category with Options
**Choose X from Y:**
- COURSE_CODE1: Name (Credits)
- COURSE_CODE2: Name (Credits)

## Prerequisites
- COURSE_CODE → DEPENDENT_CODES

## Validation Rules
[Special rules for program]
```

### 9.2 Example: program_knowledge_LLB.md

```markdown
# LL.B Honors Program

## Program Overview
- Total Credits: 130
- Duration: 4 years
- Minimum CGPA: 2.00

## GED Group 1 (16 Credits)
**All Required:**
- ENG102: Introduction to Composition (3)
- ENG103: Intermediate Composition (3)
- BEN205: Bangla Language (3)
- HIS103: Emergence of Bangladesh (3)

**Science (Choose 1):**
- PBH101: Public Health (4)
- CHE101: Chemistry I (4)
- PHY107: Physics I (4)
- BIO103: Biology (4)

## GED Group 2 (9 Credits)
**Choose Any 3:**
- ECO101: Principles of Economics (3)
- ECO104: Principles of Macroeconomics (3)
[... list all 11 options ...]

## Core Year 1 (6 Credits)
- LLB101: Introduction to Legal System (3)
- LLB102: Constitutional Laws of Bangladesh (3)

[... continue for Years 2-4 ...]

## Electives (24 Credits)
**Choose Any 8:**
- LLB411: Clinical Legal Education (3)
[... list all 19 options ...]

## Prerequisites
- LLB101 → LLB103, LLB104
- LLB102 → LLB202, LLB206
- LLB103 → LLB304, LLB305
- LLB202 → LLB302, LLB303
- LLB404 → LLB407

## Special Rules
- LLB407 requires: LLB404 + 100 credits
- LLB407 is REQUIRED for graduation
```

### 9.3 Parsing Logic

```python
def load_knowledge_base(md_file):
    requirements = {
        'program': '',
        'total_credits': 0,
        'categories': []
    }
    
    with open(md_file, 'r') as f:
        content = f.read()
    
    # Parse headers and content
    lines = content.split('\n')
    current_category = None
    
    for line in lines:
        if line.startswith('# '):
            requirements['program'] = line[2:].strip()
        elif line.startswith('## '):
            category_name = line[3:].strip()
            # Extract credits from parentheses
            if '(' in category_name and 'Credits)' in category_name:
                credits = extract_credits(category_name)
                current_category = {
                    'name': category_name,
                    'credits': credits,
                    'courses': []
                }
                requirements['categories'].append(current_category)
        elif line.startswith('- ') and current_category:
            # Parse course line
            course = parse_course_line(line)
            if course:
                current_category['courses'].append(course)
    
    return requirements

def parse_course_line(line):
    # Format: "- COURSE_CODE: Course Name (Credits)"
    match = re.match(r'- ([A-Z]+\d+): (.+) \((\d+)\)', line)
    if match:
        return {
            'code': match.group(1),
            'name': match.group(2),
            'credits': int(match.group(3))
        }
    return None
```

---

## 10. Test Strategy

### 10.1 Test Coverage Matrix

| Level | Engineering | Law | Total |
|-------|-------------|-----|-------|
| Level 1 | 10 | 8 | 18 |
| Level 2 | 8 | 8 | 16 |
| Level 3 | 15 | 10 | 25 |
| **Total** | **33** | **26** | **59** |

### 10.2 Test Case Naming Convention

```
test_LX_[program]_[scenario].csv

Where:
- X = Level number (1, 2, or 3)
- program = law, bscse, bseee, or generic
- scenario = descriptive name

Examples:
- test_L1_law_standard.csv
- test_L2_law_retakes.csv
- test_L3_law_no_dissertation.csv
```

### 10.3 Test Execution

```bash
# Level 1
python src/level1/credit_tally_engine.py tests/level1/law/test_L1_law_standard.csv

# Level 2
python src/level2/cgpa_calculator.py tests/level2/law/test_L2_law_retakes.csv

# Level 3
python src/level3/audit_engine.py tests/level3/law/test_L3_law_graduation_ready.csv data/programs/program_knowledge_LLB.md
```

### 10.4 Test Validation

Each test case should verify:
- ✅ Correct output format
- ✅ Accurate calculations
- ✅ Proper policy enforcement
- ✅ Clear error messages
- ✅ No crashes or exceptions

---

## 11. Data Formats

### 11.1 Transcript CSV Format

```csv
course_code,course_name,credits,grade,semester
ENG102,Introduction to Composition,3,A,Spring 2022
LLB101,Introduction to Legal System,3,A-,Spring 2022
BEN205,Bangla Language,3,B+,Summer 2022
HIS103,Emergence of Bangladesh,3,B,Summer 2022
BIO103,Biology,4,A-,Summer 2022
```

**Fields:**
- `course_code`: Course identifier (e.g., LLB101)
- `course_name`: Full course name
- `credits`: Credit hours (0-4)
- `grade`: Letter grade (A, A-, B+, ..., F, I, W, X)
- `semester`: Semester taken (format: "Season YYYY")

**Validation:**
- CSV must have header row
- All fields required
- Valid grade characters only
- Credits must be numeric

### 11.2 Constants File

```python
# constants.py

GRADE_POINTS = {
    'A': 4.0,
    'A-': 3.7,
    'B+': 3.3,
    'B': 3.0,
    'B-': 2.7,
    'C+': 2.3,
    'C': 2.0,
    'C-': 1.7,
    'D+': 1.3,
    'D': 1.0,
    'F': 0.0
}

VALID_GRADES = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D']
INVALID_GRADES = ['F', 'I', 'W', 'X']

PROGRAMS = {
    'BSCSE': {
        'name': 'BS in Computer Science and Engineering',
        'dept': 'Engineering',
        'credits': 130
    },
    'BSEEE': {
        'name': 'BS in Electrical and Electronic Engineering',
        'dept': 'Engineering',
        'credits': 130
    },
    'LLB': {
        'name': 'Bachelor of Laws (LL.B Honors)',
        'dept': 'Law',
        'credits': 130
    }
}

ACADEMIC_STANDING = [
    (3.80, 4.00, 'Summa Cum Laude'),
    (3.65, 3.79, 'Magna Cum Laude'),
    (3.50, 3.64, 'Cum Laude'),
    (3.00, 3.49, 'First Class'),
    (2.50, 2.99, 'Second Class'),
    (2.00, 2.49, 'Third Class'),
    (0.00, 1.99, 'PROBATION')
]

EXCLUSION_THRESHOLD = 0.80  # 80% of credits
MAX_RETAKES = 3
PROBATION_CGPA = 2.00
PROBATION_MAX_SEMESTERS = 3

COMMON_WAIVERS = ['ENG102', 'MAT116']
```

---

## 12. Implementation Guide

### 12.1 Development Order

**Phase 1: Foundation (Hours 0-4)**
1. Create directory structure
2. Implement shared utilities
3. Create constants file
4. Implement transcript parser

**Phase 2: Level 1 (Hours 4-6)**
1. Implement grade validator
2. Implement credit calculator
3. Implement program detector
4. Implement Law GED validation
5. Create main entry point
6. Test with sample data

**Phase 3: Level 2 (Hours 6-9)**
1. Implement retake processor
2. Implement waiver handler
3. Implement exclusion validator
4. Implement standing calculator
5. Create main entry point
6. Test with sample data

**Phase 4: Level 3 (Hours 9-12)**
1. Implement knowledge loader
2. Implement requirement checker
3. Implement prerequisite validator
4. Implement deficiency reporter
5. Implement policy enforcer
6. Create main entry point
7. Test with sample data

**Phase 5: Testing (Hours 12-18)**
1. Create all test CSV files
2. Run comprehensive tests
3. Fix bugs
4. Verify outputs

**Phase 6: Documentation (Hours 18-24)**
1. Update README
2. Create TESTING.md
3. Add usage examples
4. Code cleanup

### 12.2 Coding Standards

**Python Style:**
- PEP 8 compliant
- Type hints where applicable
- Docstrings for all functions
- Clear variable names

**Function Design:**
- Single responsibility
- Max 50 lines per function
- Clear input/output
- Error handling

**Example:**
```python
def validate_grade(grade: str) -> tuple[bool, str]:
    """
    Validate a letter grade.
    
    Args:
        grade: Letter grade (case-insensitive)
        
    Returns:
        tuple: (is_valid, error_message)
        
    Example:
        >>> validate_grade('A')
        (True, '')
        >>> validate_grade('Z')
        (False, 'Invalid grade: Z')
    """
    grade = grade.upper().strip()
    
    if grade in VALID_GRADES + INVALID_GRADES:
        return True, ''
    else:
        return False, f'Invalid grade: {grade}'
```

### 12.3 Error Handling

**Approach:**
- Validate inputs early
- Provide clear error messages
- Never crash silently
- Log errors when appropriate

**Example:**
```python
try:
    courses = parse_csv(transcript_file)
except FileNotFoundError:
    print(f"ERROR: File not found: {transcript_file}")
    sys.exit(1)
except ValueError as e:
    print(f"ERROR: Invalid CSV format: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Unexpected error: {e}")
    sys.exit(1)
```

---

## 13. Success Criteria

### 13.1 Functional Requirements

✅ **All programs supported**
- BSCSE audit works correctly
- BSEEE audit works correctly
- LL.B audit works correctly

✅ **All policies implemented**
- Retake policy (best grade, max 3)
- Course exclusion (80% rule)
- Probation tracking (3 semesters)
- Waiver handling (ENG102, MAT116)

✅ **Law-specific features**
- GED Group 1 validation (5 courses)
- GED Group 2 validation (3 from 11)
- Alternative course handling
- Dissertation requirement (LLB407)
- Year progression tracking

✅ **Test coverage**
- All 59 test cases passing
- Engineering: 33 tests passing
- Law: 26 tests passing

### 13.2 Non-Functional Requirements

✅ **Performance**
- < 5 seconds per audit
- Handles transcripts up to 150 courses
- Knowledge base loads in < 2 seconds

✅ **Usability**
- Clear output format
- Easy to understand reports
- Helpful error messages

✅ **Maintainability**
- Modular code structure
- Well-documented
- Easy to add new programs

✅ **Reliability**
- No crashes on valid input
- Graceful handling of errors
- Consistent results

### 13.3 Acceptance Criteria

**Level 1:**
- [x] Calculates credits correctly
- [x] Handles invalid grades
- [x] Validates GED for Law
- [x] Produces structured output

**Level 2:**
- [x] Calculates CGPA correctly
- [x] Processes retakes properly
- [x] Handles waivers
- [x] Validates exclusions
- [x] Determines standing correctly

**Level 3:**
- [x] Loads knowledge base
- [x] Validates all requirements
- [x] Checks prerequisites
- [x] Generates deficiency report
- [x] Determines graduation eligibility

---

## 14. Deliverables

### 14.1 Source Code

**Required Files:**
```
src/
├── level1/
│   ├── credit_tally_engine.py (main entry)
│   ├── grade_validator.py
│   ├── credit_calculator.py
│   └── program_detector.py
├── level2/
│   ├── cgpa_calculator.py (main entry)
│   ├── retake_processor.py
│   ├── waiver_handler.py
│   ├── exclusion_validator.py
│   └── standing_calculator.py
├── level3/
│   ├── audit_engine.py (main entry)
│   ├── knowledge_loader.py
│   ├── requirement_checker.py
│   ├── prerequisite_validator.py
│   ├── deficiency_reporter.py
│   └── policy_enforcer.py
└── shared/
    ├── transcript_parser.py
    ├── constants.py
    └── utils.py
```

### 14.2 Knowledge Base

**Required Files:**
```
data/
├── programs/
│   ├── program_knowledge_BSCSE.md
│   ├── program_knowledge_BSEEE.md
│   └── program_knowledge_LLB.md
└── policies/
    ├── ged_requirements.md
    ├── prerequisite_graph_BSCSE.md
    ├── prerequisite_graph_BSEEE.md
    └── prerequisite_graph_LLB.md
```

### 14.3 Test Cases

**Required Files:**
```
tests/
├── level1/
│   ├── engineering/ (10 tests)
│   └── law/ (8 tests)
├── level2/
│   ├── engineering/ (8 tests)
│   └── law/ (8 tests)
└── level3/
    ├── engineering/ (15 tests)
    └── law/ (10 tests)
```

### 14.4 Documentation

**Required Files:**
```
README.md          - Project overview, setup, usage
TESTING.md         - Test strategy, test cases
CHANGELOG.md       - v1.0 → v2.0 changes
```

---

## 15. Timeline

**Total Time**: 1 Day (24 hours)

| Phase | Hours | Tasks |
|-------|-------|-------|
| Phase 1 | 0-4 | Foundation, utilities, structure |
| Phase 2 | 4-6 | Level 1 implementation |
| Phase 3 | 6-9 | Level 2 implementation |
| Phase 4 | 9-12 | Level 3 implementation |
| Phase 5 | 12-18 | Test creation & execution |
| Phase 6 | 18-24 | Documentation & refinement |

---

## 16. Next Steps

### 16.1 Immediate Actions

1. **Review PRD** - Ensure understanding of all requirements
2. **Setup Environment** - Create directory structure
3. **Start Coding** - Begin with shared utilities
4. **Iterative Development** - Build and test incrementally

### 16.2 Questions?

If anything is unclear:
- Review relevant sections
- Check examples in PRD
- Refer to knowledge base files
- Test incrementally

### 16.3 Ready to Build

This PRD contains EVERYTHING needed for v2.0:
- ✅ Complete requirements
- ✅ Detailed specifications
- ✅ Implementation guide
- ✅ Test strategy
- ✅ Success criteria

**Let's build NSU Audit Core v2.0!** 🚀

---

**END OF VERSION 2.0 PRD**

**Next**: See NSU_Audit_Core_PRD_v3.0.md for CLI interface specifications
