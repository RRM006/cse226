# NSU Audit Core System
## Product Requirements Document v2.0
### CSE226 Project 1 - Spring 2026

---

**Document Information:**
- **Project Name:** NSU Department Admin Audit Core
- **Version:** 2.0
- **Previous Version:** 1.0 (Engineering Programs: BSCSE, BSEEE)
- **Date:** February 2026
- **Target Completion:** [To be determined]

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Changes from v1.0](#2-changes-from-v10)
3. [Project Overview](#3-project-overview)
4. [Multi-Department Support](#4-multi-department-support)
5. [Law Program Requirements](#5-law-program-requirements)
6. [Enhanced System Requirements](#6-enhanced-system-requirements)
7. [Academic Policy Implementation](#7-academic-policy-implementation)
8. [Implementation Architecture](#8-implementation-architecture)
9. [Test Strategy](#9-test-strategy)
10. [Data Structures & File Formats](#10-data-structures--file-formats)
11. [Deliverables](#11-deliverables)
12. [Version 3.0 Roadmap](#12-version-30-roadmap)
13. [Success Criteria](#13-success-criteria)

---

## 1. Executive Summary

**Version 2.0 Objectives:**

NSU Audit Core System v2.0 expands the graduation eligibility verification system to support **multi-department, cross-program auditing**. This version adds support for the **School of Law (LL.B Honors program)** alongside existing Engineering programs (BSCSE, BSEEE), demonstrating the system's flexibility to handle diverse academic structures.

**Key Enhancements:**
- ✅ Multi-department support (Engineering + Law)
- ✅ Program-specific validation rules
- ✅ Enhanced academic policy enforcement
- ✅ Modular solution architecture (separate files per level)
- ✅ Comprehensive test coverage
- ✅ Clear, structured output for all users

**Vision:**
Build a **unified audit engine** capable of validating any NSU program while respecting each program's unique requirements, prerequisite structures, and academic policies.

---

## 2. Changes from v1.0

### 2.1 Major Additions

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Programs Supported | 2 (BSCSE, BSEEE) | 3 (BSCSE, BSEEE, LL.B Honors) |
| Departments | 1 (Engineering) | 2 (Engineering + Law) |
| Solution Files | Mixed | Separate per level |
| GED Validation | Fixed requirements | Group-based selection rules |
| Elective Rules | Trail-based (6 trails) | Trail + Pool-based (8 from 19) |
| Year Progression | Not tracked | Year-wise progression validation |
| Dissertation | Not required | Required for Law (LLB407) |
| Academic Policies | Basic | Enhanced (retake, exclusion, probation) |

### 2.2 Architectural Changes

**v1.0 Structure:**
```
src/
├── level1_credit_tally.py
├── level2_cgpa_calculator.py
└── level3_audit_engine.py
```

**v2.0 Structure:**
```
src/
├── level1/
│   ├── credit_tally_engine.py
│   ├── grade_validator.py
│   └── credit_calculator.py
├── level2/
│   ├── cgpa_calculator.py
│   ├── waiver_handler.py
│   └── retake_processor.py
├── level3/
│   ├── audit_engine.py
│   ├── requirement_checker.py
│   ├── deficiency_reporter.py
│   └── policy_enforcer.py
└── shared/
    ├── transcript_parser.py
    ├── utils.py
    └── constants.py
```

### 2.3 Knowledge Base Expansion

**Added:**
- `program_knowledge_LLB.md` - Law program requirements
- `ged_requirements.md` - General Education Development rules
- `academic_policies.md` - NSU academic policy reference
- `prerequisite_graph.md` - Course dependency rules

---

## 3. Project Overview

### 3.1 Purpose

To build a **multi-program, multi-department graduation audit system** that:
- Validates academic requirements for diverse programs
- Enforces program-specific rules and prerequisites
- Implements NSU academic policies consistently
- Provides clear, actionable audit reports
- Serves as foundation for AI agent integration

### 3.2 Scope

**Programs Covered:**
1. **BSCSE** (BS in Computer Science and Engineering) - School of Engineering
2. **BSEEE** (BS in Electrical and Electronic Engineering) - School of Engineering
3. **LL.B Honors** (Bachelor of Laws) - School of Law

**Policies Implemented:**
- Credit calculation and validation
- CGPA computation with retakes and waivers
- Academic standing determination
- Probation and dismissal rules
- Course exclusion policies
- Year-wise progression requirements
- Prerequisite validation

### 3.3 Target Users

- **Primary:** Department administrators (Engineering + Law)
- **Secondary:** Academic advisors and faculty
- **Tertiary:** Students (read-only audit reports)
- **Future:** AI Administrative Agents (v3.0)

---

## 4. Multi-Department Support

### 4.1 Department Differences

#### Engineering Programs (BSCSE, BSEEE)

**Structure:**
- Fixed GED: 34 credits
- Fixed SEPS Core: 38 credits
- Major Core: 42 credits
- Specialized Electives: 9 credits (trail-based)
- Open Electives: 3 credits
- Capstone: 4 credits (3 courses)
- **Total: 130 credits**

**Elective Model:** Trail-based concentration
- Students must complete 2+ courses from one trail
- 6 trails available (AI, Networks, Software, etc.)

**Capstone:** 3-part project sequence
- CSE299/EEE299 (Junior Design)
- CSE499A/EEE499A (Senior Design I)
- CSE499B/EEE499B (Senior Design II)

---

#### Law Program (LL.B Honors)

**Structure:**
- GED Group 1: 16 credits (fixed courses)
- GED Group 2: 9 credits (3 from 7 courses)
- Core Program: 81 credits (27 fixed courses by year)
- Electives: 24 credits (8 from 19 courses)
- **Total: 130 credits**

**Elective Model:** Pool-based selection
- Students select any 8 courses from 19 available
- No trail requirement - completely flexible

**Capstone:** Dissertation
- LLB407: Law Dissertation (3 credits)
- Completed in Year 4, Semester 2

**Year Structure:** Courses organized by academic year
- Year 1: 2 GED + 2 Core courses
- Year 2: 9 Core courses
- Year 3: 7 Core courses + 4 Electives
- Year 4: 9 Core courses + 4 Electives

### 4.2 Common Requirements

**Across All Programs:**
- Minimum 2.00 CGPA for graduation
- Pass all courses with D or better
- Complete all core requirements
- Maximum 6 years to complete degree
- Academic probation if CGPA < 2.00
- Course retake policy (best grade counts)

---

## 5. Law Program Requirements

### 5.1 Credit Breakdown (130 Total)

| Category | Credits | Description |
|----------|---------|-------------|
| GED Group 1 | 16 | Fixed courses (ENG102, ENG103, BEN205, HIS103, Science) |
| GED Group 2 | 9 | Choose 3 from 7 courses (ECO, POL, ENG111, PHI, ENV, BUS, SOC/ANT) |
| Core Program | 81 | 27 required courses (LLB101-407) |
| Electives | 24 | Choose 8 from 19 courses (LLB411-429) |

### 5.2 GED Requirements

#### Group 1 (16 Credits - All Required)

```
ENG102: Introduction to Composition (3)
ENG103: Intermediate Composition (3)
BEN205: Bangla Language (3)
HIS103: Emergence of Bangladesh (3)

Science (Choose 1):
  - PBH101: Public Health (4)
  - CHE101: Chemistry I (4)
  - PHY107: Physics I (4)
  - BIO103: Biology (4)
```

#### Group 2 (9 Credits - Choose Any 3)

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

**Validation Rules:**
- Exactly 5 GED courses from Group 1
- Exactly 1 science course from options
- Exactly 3 courses from Group 2 (no duplicates)
- Total GED: 25 credits

### 5.3 Core Program Courses (81 Credits)

**Year 1 (6 Credits):**
```
LLB101: Introduction to Legal System (3)
LLB102: Constitutional Laws of Bangladesh (3)
```

**Year 2 (27 Credits):**
```
LLB103: Law of Contract (3)
LLB104: Law of Torts (3)
LLB201: Muslim Family and Property Law (3)
LLB202: Law of Crime (3)
LLB203: Law of Equity, Trust & Specific Relief (3)
LLB204: Company Law (3)
LLB205: Laws regarding Transfer of Property (3)
LLB206: Administrative Law (3)
LLB207: Law of Registration & Limitation (3)
LLB208: Jurisprudence and Legal Theory (3)
LLB209: Legal Professional Ethics (3)
```

**Year 3 (21 Credits):**
```
LLB301: Law of Evidence (3)
LLB302: Law of Criminal Procedure (Part 1) (3)
LLB303: Law of Criminal Procedure (Part 2) (3)
LLB304: Law of Civil Procedure (Part 1) (3)
LLB305: Law of Civil Procedure (Part 2) (3)
LLB306: Law of Labour and Employment (3)
LLB307: Land Law of Bangladesh (3)
```

**Year 4 (27 Credits):**
```
LLB401: Alternative Dispute Resolution Methods (3)
LLB402: Legal Drafting & Conveyance (3)
LLB403: Public International Laws (3)
LLB404: Legal Research (3)
LLB405: Trial and Advocacy (3)
LLB406: Hindu and Christian Family Law (3)
LLB407: Law Dissertation (3) [REQUIRED - Capstone]
```

### 5.4 Elective Courses (24 Credits - Choose 8)

```
LLB411: Clinical Legal Education (3)
LLB412: Fiscal & Taxation Law (3)
LLB413: Environmental Law (3)
LLB414: Cyber, Media & Telecommunication Law (3)
LLB415: Special Penal Laws (3)
LLB416: Intellectual Property Law (3)
LLB417: Banking and Foreign Exchange Law (3)
LLB418: Criminology and Penology (3)
LLB419: International Criminal Law (3)
LLB420: Medical Jurisprudence and Forensic Law (3)
LLB421: Corporate Insolvency Law (3)
LLB422: Election Laws (3)
LLB423: Law and Globalization (3)
LLB424: Maritime, Oceans, and Coastal Law (3)
LLB425: Anti-corruption & Anti-money Laundering Law (3)
LLB426: Mercantile Law (3)
LLB427: Foreign Investment Law (3)
LLB428: Public Demands Recovery & Loan Recovery Law (3)
LLB429: Public Private Partnership Law (3)
```

**Validation Rules:**
- Exactly 8 elective courses required
- Any combination allowed (no trail requirement)
- Must total 24 credits (all are 3-credit courses)

### 5.5 Year-Wise Progression Rules

**Law-Specific Policies:**

1. **Year 1 Foundation:**
   - Must complete all GED Group 1 courses by end of Year 1
   - Must complete LLB101 and LLB102 by end of Year 1
   - Cannot proceed to Year 2 core without completing Year 1 foundation

2. **Year 2 Prerequisites:**
   - Must complete LLB101 before LLB103, LLB104
   - Must complete LLB102 before LLB202, LLB206

3. **Year 3 Prerequisites:**
   - Must complete LLB202 before LLB302, LLB303
   - Must complete LLB103 before LLB304, LLB305

4. **Year 4 Capstone:**
   - LLB407 (Dissertation) can only be taken in Year 4
   - Must complete at least 100 credits before LLB407
   - Must complete LLB404 (Legal Research) before LLB407

5. **Elective Timing:**
   - Can start taking electives from Year 3 onwards
   - Recommended: 4 electives in Year 3, 4 in Year 4

### 5.6 Semester-Wise Recommended Sequence

**Year 1, Semester 1:**
```
ENG102 (3)
2 GED Group 2 courses (6)
1 Science course (4)
LLB101 (3)
Total: 16 credits
```

**Year 1, Semester 2:**
```
ENG103 (3)
1 GED Group 2 course (3)
HIS103 (3)
BEN205 (3)
Science Lab (1) [if applicable]
LLB102 (3)
Total: 16 credits
```

**Year 2, Semester 1:**
```
LLB103 (3)
LLB104 (3)
LLB201 (3)
LLB202 (3)
LLB203 (3)
Total: 15 credits
```

**Year 2, Semester 2:**
```
LLB204 (3)
LLB205 (3)
LLB206 (3)
LLB207 (3)
LLB208 (3)
LLB209 (3)
Total: 18 credits
```

**Year 3, Semester 1:**
```
LLB301 (3)
LLB302 (3)
LLB304 (3)
LLB306 (3)
ELECTIVE 1 (3)
Total: 15 credits
```

**Year 3, Semester 2:**
```
LLB303 (3)
LLB305 (3)
LLB307 (3)
ELECTIVE 2 (3)
ELECTIVE 3 (3)
ELECTIVE 4 (3)
Total: 18 credits
```

**Year 4, Semester 1:**
```
LLB401 (3)
LLB402 (3)
LLB403 (3)
LLB404 (3)
ELECTIVE 5 (3)
ELECTIVE 6 (3)
Total: 18 credits
```

**Year 4, Semester 2:**
```
LLB405 (3)
LLB406 (3)
LLB407 (3) [Dissertation - REQUIRED]
ELECTIVE 7 (3)
ELECTIVE 8 (3)
Total: 15 credits
```

---

## 6. Enhanced System Requirements

### 6.1 Functional Requirements

#### Level 1: Credit Tally Engine (Enhanced)

**FR1.1: Multi-Program Credit Calculation**
- Support Engineering (130 credits) and Law (130 credits)
- Validate program-specific credit structures
- Handle different course code formats (CSE, EEE, LLB)

**FR1.2: GED Validation for Law**
- Verify Group 1 completion (5 courses, 16 credits)
- Verify Group 2 selection (3 from 7, 9 credits)
- Ensure no duplicate selections in Group 2

**FR1.3: Enhanced Grade Handling**
- All v1.0 grade rules (F, I, W, X exclusions)
- Track courses by academic year (Year 1-4)
- Identify year-based progression issues

---

#### Level 2: CGPA Calculator & Policy Enforcer (Enhanced)

**FR2.1: Retake Policy Implementation**
- Identify all course retakes (same course code)
- Use best grade for CGPA calculation
- Track retake count (max 3 times per course)
- Flag courses requiring Vice-Chancellor approval (4th retake)

**FR2.2: Course Exclusion Policy**
- Allow exclusion only after 80% credits completed
- Prevent exclusion of core courses
- Prevent exclusion to avoid probation
- Track exclusion requests and approvals

**FR2.3: Waiver Handling (Program-Specific)**
- Engineering: ENG102, MAT116
- Law: ENG102 (if applicable)
- Exclude waived courses from CGPA
- Count waived credits toward degree

**FR2.4: Academic Standing Enforcement**
- Calculate CGPA with all policies applied
- Determine academic standing (Summa, Magna, Cum Laude, etc.)
- Flag probation status (CGPA < 2.00)
- Track probation semesters (max 3)

---

#### Level 3: Audit Engine & Deficiency Reporter (Enhanced)

**FR3.1: Multi-Program Requirement Validation**
- Load program-specific knowledge base
- Validate category-wise requirements (GED, Core, Electives)
- Check program-specific rules (trails vs. pool selection)

**FR3.2: Law-Specific Validation**
- GED Group 1 & 2 compliance
- Year-wise core course completion
- 8 electives from 19 available
- Dissertation (LLB407) completion

**FR3.3: Prerequisite Validation**
- Load prerequisite graph for program
- Check prerequisite violations
- Flag courses taken without prerequisites

**FR3.4: Year Progression Tracking**
- Validate year-wise progression (Law program)
- Ensure foundation courses completed before advanced
- Check Year 4 dissertation eligibility (100 credits)

**FR3.5: Enhanced Deficiency Reporting**
- Generate program-specific deficiency report
- List missing courses by category
- Suggest course selections (electives)
- Provide clear action items

**FR3.6: Graduation Eligibility Determination**
- PASS: All requirements met, CGPA ≥ 2.00
- FAIL: Missing requirements or CGPA < 2.00
- PROBATION: CGPA < 2.00 (not eligible)

### 6.2 Non-Functional Requirements

**NFR1: Accuracy**
- 100% policy compliance across all programs
- Zero false positives/negatives in deficiency detection

**NFR2: Performance**
- Process transcript in < 5 seconds
- Load knowledge base in < 2 seconds

**NFR3: Usability**
- Clear CLI commands for each program
- Structured output readable by anyone
- Consistent formatting across all reports

**NFR4: Maintainability**
- Modular architecture (separate files per level)
- Shared utilities for common operations
- Well-documented code

**NFR5: Extensibility**
- Easy to add new programs
- Pluggable policy validators
- Configurable knowledge base format

**NFR6: Output Clarity**
- Use clear section headers
- Color-code results (v3.0)
- Provide actionable recommendations
- Include summary statistics

---

## 7. Academic Policy Implementation

### 7.1 Retake Policy (Full Implementation)

**Rules from Academic Policies Document:**

1. **Eligibility:**
   - Student may retake if grade is B or lower
   - No retake for grades A, A-

2. **CGPA Calculation:**
   - Best grade from all attempts used
   - Lower grades show 0.0 grade points

3. **Retake Limits:**
   - Normal limit: 3 attempts per course
   - 4th attempt: Requires Vice-Chancellor approval

4. **Transcript Display:**
   - All attempts appear on transcript
   - Only best attempt counted

**Implementation:**
```python
# Pseudo-code for retake handling
def process_retakes(transcript):
    retakes = group_by_course_code(transcript)
    for course_code, attempts in retakes.items():
        if len(attempts) > 1:
            best_grade = max(attempts, key=grade_point)
            for attempt in attempts:
                if attempt != best_grade:
                    attempt.counted_for_cgpa = False
                    attempt.grade_points = 0.0
        
        if len(attempts) >= 4:
            flag_for_vc_approval(course_code)
    
    return calculate_cgpa(transcript)
```

### 7.2 Course Exclusion Policy

**Rules:**

1. **Eligibility:**
   - Can exclude only after completing 80% of required credits
   - Engineering: 80% of 130 = 104 credits
   - Law: 80% of 130 = 104 credits

2. **Restrictions:**
   - Cannot exclude core courses
   - Cannot exclude to improve CGPA for probation avoidance
   - Cannot exclude to meet department change requirements

3. **After Department Change:**
   - Can exclude courses not required by new program

4. **Re-inclusion:**
   - Discouraged but allowed with justification

**Implementation:**
```python
def validate_exclusion_request(student, course):
    earned_credits = calculate_earned_credits(student.transcript)
    required_credits = get_program_requirement(student.program)
    
    if earned_credits < (required_credits * 0.80):
        return False, "Must complete 80% of credits first"
    
    if is_core_course(course, student.program):
        return False, "Cannot exclude core courses"
    
    if student.cgpa < 2.00:
        return False, "Cannot exclude while on probation"
    
    return True, "Exclusion approved"
```

### 7.3 Academic Probation & Dismissal

**Rules:**

1. **Probation:**
   - Triggered when CGPA < 2.00 (undergrad) or < 2.50 (grad)
   - Student has 3 semesters to raise CGPA

2. **Dismissal ("Excluded"):**
   - After 3 semesters on probation without reaching required CGPA
   - Dismissed in 4th semester

3. **Probation Status:**
   - Cannot change department
   - Cannot exclude courses
   - Limited course load

4. **No Fresh Start:**
   - Once excluded, cannot be readmitted
   - Cannot take admission test again

**Implementation:**
```python
def check_academic_standing(student):
    if student.cgpa < 2.00:
        if student.probation_semesters >= 3:
            return "DISMISSED", "Excluded from University"
        else:
            return "PROBATION", f"Semester {student.probation_semesters + 1} of 3"
    else:
        return "GOOD_STANDING", determine_honors(student.cgpa)
```

### 7.4 Course Registration Rules

**Rules:**

1. **100-Level Course Requirement:**
   - Must pass all 100-level courses by 3rd semester
   - Exception: English courses (can take longer)
   - Cannot register for higher-level courses until complete

2. **Failed 100-Level Course:**
   - After 2 failures, cannot register for any other course (except English)
   - Must pass failed course before continuing

3. **English Requirement:**
   - Must pass ENG105 by 4th semester
   - If not passed, cannot register for other courses

4. **Late Registration:**
   - Must pay late registration fee
   - Requires department chair approval

**Implementation:**
```python
def validate_registration(student, course):
    # Check 100-level completion
    if course.level > 100:
        incomplete_100 = get_incomplete_100_courses(student)
        if incomplete_100 and student.semesters_enrolled >= 3:
            return False, "Must complete 100-level courses first"
    
    # Check failed course restrictions
    failed_100 = get_failed_100_courses(student, attempts=2)
    if failed_100 and course.code not in failed_100:
        return False, f"Must pass {failed_100} first"
    
    # Check English requirement
    if not has_passed_eng105(student) and student.semesters >= 4:
        if course.code != "ENG105":
            return False, "Must pass ENG105 first"
    
    return True, "Registration approved"
```

### 7.5 Withdrawal & Semester Drop

**Rules:**

1. **Course Drop:**
   - Before week 3: No record entry
   - Week 3-12: Grade 'W' on transcript
   - After week 12: Cannot drop

2. **Semester Withdrawal:**
   - Must notify Registrar's Office
   - Must withdraw by week 6
   - After week 6: Only for non-academic hardships

3. **Abandonment:**
   - Students who abandon without withdrawal receive 'F' grades
   - Affects CGPA and academic standing

**Implementation:**
```python
def process_withdrawal(student, request_type, week_number):
    if request_type == "COURSE_DROP":
        if week_number <= 3:
            return "APPROVED", "No record entry"
        elif week_number <= 12:
            return "APPROVED", "Grade 'W' recorded"
        else:
            return "DENIED", "Cannot drop after week 12"
    
    elif request_type == "SEMESTER_DROP":
        if week_number <= 6:
            return "APPROVED", "Semester withdrawal recorded"
        else:
            # Requires department chair approval + hardship
            return "REQUIRES_APPROVAL", "Non-academic hardship required"
```

---

## 8. Implementation Architecture

### 8.1 File Structure

```
nsu_audit_core/
│
├── README.md
├── testing_plan.md
├── NSU_Audit_Core_PRD_v2.0.md
│
├── src/
│   ├── __init__.py
│   │
│   ├── level1/                      # Credit Tally Engine
│   │   ├── __init__.py
│   │   ├── credit_tally_engine.py  # Main entry point
│   │   ├── grade_validator.py      # Grade validation logic
│   │   ├── credit_calculator.py    # Credit calculation
│   │   └── year_tracker.py         # Year-wise tracking (Law)
│   │
│   ├── level2/                      # CGPA Calculator & Policy Enforcer
│   │   ├── __init__.py
│   │   ├── cgpa_calculator.py      # Main entry point
│   │   ├── waiver_handler.py       # Waiver processing
│   │   ├── retake_processor.py     # Retake policy
│   │   ├── exclusion_validator.py  # Course exclusion
│   │   └── standing_calculator.py  # Academic standing
│   │
│   ├── level3/                      # Audit Engine & Deficiency Reporter
│   │   ├── __init__.py
│   │   ├── audit_engine.py         # Main entry point
│   │   ├── requirement_checker.py  # Requirement validation
│   │   ├── deficiency_reporter.py  # Report generation
│   │   ├── policy_enforcer.py      # Policy validation
│   │   ├── prerequisite_validator.py # Prerequisite checks
│   │   └── elective_validator.py   # Elective rules
│   │
│   ├── shared/                      # Shared utilities
│   │   ├── __init__.py
│   │   ├── transcript_parser.py    # CSV parsing
│   │   ├── knowledge_loader.py     # Load program requirements
│   │   ├── utils.py                # Helper functions
│   │   ├── constants.py            # Constants (grades, policies)
│   │   └── output_formatter.py     # Formatted output
│   │
│   └── cli.py                       # Command-line interface (v3.0)
│
├── data/
│   ├── programs/
│   │   ├── program_knowledge_BSCSE.md
│   │   ├── program_knowledge_BSEEE.md
│   │   └── program_knowledge_LLB.md        # NEW
│   │
│   ├── policies/
│   │   ├── ged_requirements.md             # NEW
│   │   ├── academic_policies.md            # NEW
│   │   ├── prerequisite_graph_BSCSE.md
│   │   ├── prerequisite_graph_BSEEE.md
│   │   └── prerequisite_graph_LLB.md       # NEW
│   │
│   └── templates/
│       ├── transcript_template.csv
│       ├── audit_report_template.md
│       └── deficiency_report_template.md
│
├── tests/
│   ├── level1/
│   │   ├── engineering/
│   │   │   ├── test_L1_1.csv
│   │   │   ├── test_L1_2.csv
│   │   │   └── ... (existing tests)
│   │   │
│   │   └── law/                            # NEW
│   │       ├── test_L1_law_standard.csv
│   │       ├── test_L1_law_ged_violation.csv
│   │       ├── test_L1_law_incomplete.csv
│   │       └── test_L1_law_edge_cases.csv
│   │
│   ├── level2/
│   │   ├── engineering/
│   │   │   └── ... (existing tests)
│   │   │
│   │   └── law/                            # NEW
│   │       ├── test_L2_law_cgpa_standard.csv
│   │       ├── test_L2_law_retakes.csv
│   │       ├── test_L2_law_waivers.csv
│   │       ├── test_L2_law_probation.csv
│   │       └── test_L2_law_exclusion.csv
│   │
│   ├── level3/
│   │   ├── engineering/
│   │   │   └── ... (existing tests)
│   │   │
│   │   └── law/                            # NEW
│   │       ├── test_L3_law_graduation_ready.csv
│   │       ├── test_L3_law_missing_core.csv
│   │       ├── test_L3_law_ged_incomplete.csv
│   │       ├── test_L3_law_elective_deficiency.csv
│   │       ├── test_L3_law_no_dissertation.csv
│   │       ├── test_L3_law_prerequisite_violation.csv
│   │       ├── test_L3_law_year_progression.csv
│   │       └── test_L3_law_probation.csv
│   │
│   └── integration/
│       ├── test_multi_program_audit.py
│       └── test_policy_enforcement.py
│
├── docs/
│   ├── API.md                              # API documentation
│   ├── KNOWLEDGE_BASE_FORMAT.md            # Knowledge base format spec
│   ├── TEST_STRATEGY.md                    # Testing strategy
│   └── POLICY_REFERENCE.md                 # Academic policy reference
│
└── outputs/
    ├── audit_reports/                      # Generated audit reports
    ├── deficiency_reports/                 # Deficiency reports
    └── logs/                               # System logs
```

### 8.2 Modular Design Principles

#### Level 1 Modules

**credit_tally_engine.py** - Main entry point
- Orchestrates credit calculation workflow
- Calls grade validator and credit calculator
- Generates Level 1 report

**grade_validator.py** - Grade validation logic
- Validates letter grades (A-F, I, W, X)
- Maps grades to grade points
- Identifies invalid grades

**credit_calculator.py** - Credit calculation
- Calculates earned credits
- Handles 0-credit labs
- Excludes invalid grades (F, I, W, X)

**year_tracker.py** - Year-wise tracking (NEW)
- Tracks courses by academic year
- Validates year progression (Law)
- Identifies year-based issues

---

#### Level 2 Modules

**cgpa_calculator.py** - Main entry point
- Orchestrates CGPA calculation
- Calls waiver handler and retake processor
- Generates Level 2 report

**waiver_handler.py** - Waiver processing
- Prompts for waiver information
- Validates waiver eligibility
- Excludes waivers from CGPA

**retake_processor.py** - Retake policy (NEW)
- Identifies course retakes
- Selects best grade
- Flags excessive retakes (4+)

**exclusion_validator.py** - Course exclusion (NEW)
- Validates exclusion requests
- Enforces 80% credit requirement
- Prevents core course exclusion

**standing_calculator.py** - Academic standing
- Calculates final CGPA
- Determines honors (Summa, Magna, Cum Laude)
- Flags probation status

---

#### Level 3 Modules

**audit_engine.py** - Main entry point
- Orchestrates full audit workflow
- Calls requirement checker and deficiency reporter
- Generates comprehensive audit report

**requirement_checker.py** - Requirement validation
- Loads program knowledge base
- Validates category-wise requirements
- Checks program-specific rules

**deficiency_reporter.py** - Report generation
- Identifies missing courses
- Categorizes deficiencies
- Generates actionable recommendations

**policy_enforcer.py** - Policy validation (NEW)
- Enforces academic policies
- Validates retakes, exclusions
- Checks probation status

**prerequisite_validator.py** - Prerequisite checks (NEW)
- Loads prerequisite graph
- Identifies prerequisite violations
- Suggests correct course sequence

**elective_validator.py** - Elective rules (NEW)
- Validates elective selection
- Checks trail requirements (Engineering)
- Checks pool requirements (Law)

---

#### Shared Modules

**transcript_parser.py** - CSV parsing
- Parses transcript CSV files
- Validates CSV format
- Returns structured data

**knowledge_loader.py** - Load program requirements (NEW)
- Parses markdown knowledge base
- Loads program requirements
- Returns structured requirements

**utils.py** - Helper functions
- Common utility functions
- String manipulation
- Data structure operations

**constants.py** - Constants
- Grade point mappings
- Academic standing thresholds
- Policy constants

**output_formatter.py** - Formatted output (NEW)
- Formats CLI output
- Creates structured reports
- Ensures consistent formatting

### 8.3 Knowledge Base Format

#### program_knowledge_LLB.md Structure

```markdown
# LL.B Honors Program Requirements
## North South University School of Law

### Program Overview
- Total Credits: 130
- Duration: 4 years (8 semesters)
- Minimum CGPA: 2.00

### Credit Distribution

#### GED Group 1 (16 Credits)
- ENG102: Introduction to Composition (3)
- ENG103: Intermediate Composition (3)
- BEN205: Bangla Language (3)
- HIS103: Emergence of Bangladesh (3)
- Science (Choose 1 from 4 options): (4)
  - PBH101: Public Health
  - CHE101: Chemistry I
  - PHY107: Physics I
  - BIO103: Biology

#### GED Group 2 (9 Credits - Choose 3)
- ECO101 or ECO104: Economics (3)
- POL101 or POL104: Political Science (3)
- ENG111: Public Speaking (3)
- PHI101: Introduction to Philosophy (3)
- ENV203 or GEO205: Environment/Geography (3)
- BUS112: Principles of Management (3)
- SOC101 or ANT101: Sociology/Anthropology (3)

#### Core Program Courses (81 Credits)
**Year 1 (6 Credits):**
- LLB101: Introduction to Legal System (3)
- LLB102: Constitutional Laws of Bangladesh (3)

**Year 2 (27 Credits):**
[... list all Year 2 courses ...]

[... continue for Years 3 and 4 ...]

#### Electives (24 Credits - Choose 8)
- LLB411: Clinical Legal Education (3)
- LLB412: Fiscal & Taxation Law (3)
[... list all 19 elective options ...]

### Prerequisite Rules
- LLB101 → LLB103, LLB104
- LLB102 → LLB202, LLB206
- LLB202 → LLB302, LLB303
- LLB103 → LLB304, LLB305
- LLB404 → LLB407

### Year Progression Rules
1. Must complete all GED Group 1 by end of Year 1
2. Must complete Year 1 core before Year 2 core
3. Can take electives starting Year 3
4. LLB407 (Dissertation) only in Year 4 after 100 credits

### Capstone Requirement
- LLB407: Law Dissertation (3 credits)
- Required in Year 4, Semester 2
- Prerequisite: LLB404 + 100 credits completed
```

---

## 9. Test Strategy

### 9.1 Test Coverage Matrix

| Level | Engineering Tests | Law Tests | Total |
|-------|------------------|-----------|-------|
| Level 1 | 10 | 8 | 18 |
| Level 2 | 8 | 8 | 16 |
| Level 3 | 15 | 10 | 25 |
| **Total** | **33** | **26** | **59** |

### 9.2 Law Program Test Cases

#### Level 1: Credit Tally (Law)

**test_L1_law_standard.csv**
- Purpose: Standard Law student with good progress
- Features: 90 credits earned, all GED complete, Year 1-3 core complete
- Expected: 90 credits earned, breakdown by category

**test_L1_law_ged_violation.csv**
- Purpose: Law student with GED Group 2 violation
- Features: Only 2 courses from Group 2 (needs 3)
- Expected: Flag GED deficiency

**test_L1_law_incomplete.csv**
- Purpose: Law student with incomplete grades
- Features: 3 courses with 'I' grade, 1 with 'W'
- Expected: Exclude I and W from credit count

**test_L1_law_edge_cases.csv**
- Purpose: Edge cases (retakes, 0-credit courses if any, F grades)
- Features: Mixed scenarios
- Expected: Correct credit calculation with all exclusions

**test_L1_law_year_progression.csv** (NEW)
- Purpose: Year progression tracking
- Features: Student in Year 3 with some Year 2 courses incomplete
- Expected: Flag year progression issues

**test_L1_law_ged_group_selection.csv** (NEW)
- Purpose: GED Group 2 selection validation
- Features: Student selected courses from Group 2
- Expected: Validate correct selection (3 from 7)

**test_L1_law_science_selection.csv** (NEW)
- Purpose: GED Group 1 science course validation
- Features: Student selected science course
- Expected: Validate 1 science course from 4 options

**test_L1_law_credits_by_year.csv** (NEW)
- Purpose: Credit distribution by year
- Features: Courses distributed across 4 years
- Expected: Show credit breakdown by year

---

#### Level 2: CGPA & Policies (Law)

**test_L2_law_cgpa_standard.csv**
- Purpose: Standard CGPA calculation for Law
- Features: 100 credits, mix of grades, no retakes/waivers
- Expected: CGPA = 3.15, Good Standing

**test_L2_law_retakes.csv**
- Purpose: Multiple course retakes
- Features: 4 courses retaken (best grades used)
- Expected: CGPA with best grades, retake count

**test_L2_law_waivers.csv**
- Purpose: Waiver handling for Law
- Features: ENG102 waived (if applicable)
- Expected: CGPA excludes waived course

**test_L2_law_probation.csv**
- Purpose: Probation status detection
- Features: CGPA = 1.85 (below 2.00)
- Expected: Flag PROBATION status

**test_L2_law_exclusion.csv** (NEW)
- Purpose: Course exclusion policy validation
- Features: Student requesting exclusion after 105 credits
- Expected: Validate exclusion eligibility

**test_L2_law_excessive_retakes.csv** (NEW)
- Purpose: Excessive retake detection
- Features: One course retaken 4 times
- Expected: Flag for VC approval

**test_L2_law_standing_calculation.csv** (NEW)
- Purpose: All academic standing levels
- Features: Various CGPAs (Summa to Probation)
- Expected: Correct standing determination

**test_L2_law_borderline_cgpa.csv** (NEW)
- Purpose: Borderline CGPA (exactly 2.00)
- Features: CGPA = 2.00
- Expected: Good Standing (not probation)

---

#### Level 3: Full Audit (Law)

**test_L3_law_graduation_ready.csv**
- Purpose: Student ready to graduate
- Features: 130 credits, all requirements met, CGPA = 3.40
- Expected: PASS - Eligible for graduation

**test_L3_law_missing_core.csv**
- Purpose: Missing core courses
- Features: 125 credits, missing 2 Year 4 core courses
- Expected: FAIL - Missing LLB401, LLB402

**test_L3_law_ged_incomplete.csv**
- Purpose: GED requirements not met
- Features: Only 2 courses from GED Group 2
- Expected: FAIL - Need 1 more GED Group 2 course

**test_L3_law_elective_deficiency.csv**
- Purpose: Insufficient electives
- Features: Only 6 electives taken (need 8)
- Expected: FAIL - Need 2 more electives (6 credits)

**test_L3_law_no_dissertation.csv**
- Purpose: Missing dissertation
- Features: All other requirements met, no LLB407
- Expected: FAIL - Must complete LLB407 (Dissertation)

**test_L3_law_prerequisite_violation.csv** (NEW)
- Purpose: Prerequisite violation detection
- Features: Took LLB302 without LLB202
- Expected: Flag prerequisite violation

**test_L3_law_year_progression.csv** (NEW)
- Purpose: Year progression validation
- Features: Year 4 student with Year 2 courses incomplete
- Expected: Flag year progression issues

**test_L3_law_probation.csv** (NEW)
- Purpose: Student on probation
- Features: CGPA = 1.95, all courses complete
- Expected: FAIL - Cannot graduate on probation

**test_L3_law_dissertation_ineligible.csv** (NEW)
- Purpose: Dissertation eligibility check
- Features: Student with < 100 credits trying to take LLB407
- Expected: Flag ineligibility for dissertation

**test_L3_law_comprehensive.csv** (NEW)
- Purpose: Comprehensive audit with multiple issues
- Features: Multiple deficiencies across categories
- Expected: Detailed deficiency report with all issues

### 9.3 Integration Tests

**test_multi_program_audit.py** (NEW)
- Purpose: Test audit engine across all programs
- Features: Run audits for BSCSE, BSEEE, LLB students
- Expected: Correct program-specific validations

**test_policy_enforcement.py** (NEW)
- Purpose: Test all academic policies
- Features: Retake, exclusion, probation, withdrawal policies
- Expected: Correct policy enforcement

### 9.4 Test Execution Strategy

1. **Unit Testing:**
   - Test individual functions (grade mapper, credit calculator)
   - Test policy validators (retake, exclusion)
   - Test knowledge base parser

2. **Integration Testing:**
   - Test complete workflows for each level
   - Test multi-program support
   - Test policy enforcement

3. **Edge Case Testing:**
   - Focus on boundary conditions
   - Test all edge cases from v1.0 + new Law edge cases
   - Test policy edge cases

4. **Manual Testing:**
   - Run all provided test cases
   - Verify output format and clarity
   - Cross-validate with manual calculations

5. **Regression Testing:**
   - Ensure v1.0 functionality still works
   - Test BSCSE and BSEEE programs
   - Verify no breaking changes

---

## 10. Data Structures & File Formats

### 10.1 Transcript CSV Format (Unchanged)

```csv
course_code,course_name,credits,grade,semester
ENG102,Introduction to Composition,3,A,Spring 2022
LLB101,Introduction to Legal System,3,A-,Spring 2022
BEN205,Bangla Language,3,B+,Summer 2022
HIS103,Emergence of Bangladesh,3,B,Summer 2022
...
```

**Fields:**
- `course_code`: Course identifier (e.g., LLB101)
- `course_name`: Full course name
- `credits`: Credit hours (0-4)
- `grade`: Letter grade (A, A-, B+, ..., F, I, W, X)
- `semester`: Semester taken (e.g., "Spring 2022")

### 10.2 Knowledge Base Format (Enhanced)

**Markdown Structure:**
```markdown
# Program Name
## Category (Credit Requirement)
### Subcategory (Optional)
- COURSE_CODE: Course Name (Credits)
- ...

## Prerequisites
- COURSE_CODE → DEPENDENT_CODES
```

**Example:**
```markdown
# LL.B Honors Program

## GED Group 1 (16 Credits)
- ENG102: Introduction to Composition (3)
- ENG103: Intermediate Composition (3)
- ...

## GED Group 2 (9 Credits - Choose 3)
- ECO101: Principles of Economics (3)
- ECO104: Principles of Macroeconomics (3)
- ...

## Prerequisites
- LLB101 → LLB103, LLB104
- LLB102 → LLB202, LLB206
```

### 10.3 Output Format Specifications

#### Level 1 Output (Enhanced)

```
=== NSU AUDIT CORE - LEVEL 1 ===
Student: [Student ID]
Program: LL.B Honors
Processing: test_L1_law_standard.csv

╔════════════════════════════════════════════════════════════════╗
║                     CREDIT ANALYSIS                            ║
╚════════════════════════════════════════════════════════════════╝

Total Courses Attempted: 35
Valid Courses (A-D): 32
Excluded Courses: 3
  ├─ LLB201 (F) - 3 credits [FAILED]
  ├─ ECO101 (W) - 3 credits [WITHDRAWN]
  └─ LLB304 (I) - 3 credits [INCOMPLETE]

╔════════════════════════════════════════════════════════════════╗
║                   CREDITS BY CATEGORY                          ║
╚════════════════════════════════════════════════════════════════╝

GED Group 1:           16 / 16 credits  ✓ COMPLETE
GED Group 2:            9 /  9 credits  ✓ COMPLETE
Core Program:          54 / 81 credits  ⚠ IN PROGRESS
  ├─ Year 1:            6 /  6 credits  ✓
  ├─ Year 2:           24 / 27 credits  ⚠ (Missing 3)
  ├─ Year 3:           21 / 21 credits  ✓
  └─ Year 4:            3 / 27 credits  ⚠ (Missing 24)
Electives:             12 / 24 credits  ⚠ IN PROGRESS

Total Earned Credits:  91 / 130 credits

RESULT: ⚠ IN PROGRESS (91 credits completed)
```

#### Level 2 Output (Enhanced)

```
=== NSU AUDIT CORE - LEVEL 2 ===
Student: [Student ID]
Program: LL.B Honors
Processing: test_L2_law_retakes.csv

Enter waived courses (comma-separated, or NONE): ENG102

╔════════════════════════════════════════════════════════════════╗
║                     CGPA CALCULATION                           ║
╚════════════════════════════════════════════════════════════════╝

Waivers Applied: 1 course (3 credits)
  └─ ENG102: Introduction to Composition (3 credits)

Retakes Processed: 3 courses
  ├─ LLB103: C (2.0) → A- (3.7)  ✓ IMPROVED
  ├─ LLB201: F (0.0) → B (3.0)   ✓ IMPROVED
  └─ LLB208: B- (2.7) → B+ (3.3) ✓ IMPROVED

Calculation:
  Total Grade Points:    402.6
  Total Credits Counted: 127
  
  CGPA = 402.6 / 127 = 3.17

╔════════════════════════════════════════════════════════════════╗
║                   ACADEMIC STANDING                            ║
╚════════════════════════════════════════════════════════════════╝

CGPA:             3.17
Standing:         First Class (Good Standing)
Honors:           None
Status:           ✓ GOOD STANDING

RESULT: ✓ PASSED (CGPA = 3.17)
```

#### Level 3 Output (Enhanced)

```
=== NSU AUDIT CORE - LEVEL 3 ===
Student: [Student ID]
Program: LL.B Honors
Processing: test_L3_law_missing_core.csv
Knowledge Base: data/programs/program_knowledge_LLB.md

╔════════════════════════════════════════════════════════════════╗
║                    GRADUATION AUDIT                            ║
╚════════════════════════════════════════════════════════════════╝

Credits:          125 / 130 required
CGPA:             3.20
Standing:         First Class (Good Standing)

╔════════════════════════════════════════════════════════════════╗
║                   REQUIREMENT ANALYSIS                         ║
╚════════════════════════════════════════════════════════════════╝

GED Requirements:
  ├─ Group 1 (16 cr):   ✓ COMPLETE
  └─ Group 2 (9 cr):    ✓ COMPLETE

Core Program (81 cr):   ⚠ INCOMPLETE (78 / 81)
  ├─ Year 1 (6 cr):     ✓ COMPLETE
  ├─ Year 2 (27 cr):    ✓ COMPLETE
  ├─ Year 3 (21 cr):    ✓ COMPLETE
  └─ Year 4 (27 cr):    ⚠ INCOMPLETE (24 / 27)
      Missing:
        ├─ LLB401: Alternative Dispute Resolution (3 cr)
        ├─ LLB403: Public International Laws (3 cr)
        └─ LLB407: Law Dissertation (3 cr) [REQUIRED]

Electives (24 cr):      ✓ COMPLETE (8 courses)

╔════════════════════════════════════════════════════════════════╗
║                   DEFICIENCY REPORT                            ║
╚════════════════════════════════════════════════════════════════╝

Missing Courses: 3 (9 credits)

Core Courses:
  1. LLB401: Alternative Dispute Resolution Methods (3 cr)
     └─ Year 4, Semester 1
  
  2. LLB403: Public International Laws (3 cr)
     └─ Year 4, Semester 1
  
  3. LLB407: Law Dissertation (3 cr) [CAPSTONE - REQUIRED]
     └─ Year 4, Semester 2
     └─ Prerequisite: LLB404 (✓ Complete)

╔════════════════════════════════════════════════════════════════╗
║                   ACTION ITEMS                                 ║
╚════════════════════════════════════════════════════════════════╝

To graduate, you must:
  1. Complete LLB401 (3 credits)
  2. Complete LLB403 (3 credits)
  3. Complete LLB407 - Dissertation (3 credits) [REQUIRED]

Total credits needed: 9
Estimated completion: 1 semester

╔════════════════════════════════════════════════════════════════╗
║                  GRADUATION ELIGIBILITY                        ║
╚════════════════════════════════════════════════════════════════╝

RESULT: ❌ NOT ELIGIBLE FOR GRADUATION

Reasons:
  ├─ Missing 3 core courses (9 credits)
  └─ Dissertation (LLB407) not completed

Status: Continue enrollment to complete remaining courses.
```

### 10.4 CLI Command Structure

```bash
# Level 1: Credit Tally
python src/level1/credit_tally_engine.py <transcript_csv> [--program PROGRAM]

# Level 2: CGPA Calculator
python src/level2/cgpa_calculator.py <transcript_csv> [--program PROGRAM]

# Level 3: Full Audit
python src/level3/audit_engine.py <transcript_csv> <knowledge_base_md> [--program PROGRAM]

# Examples:
python src/level1/credit_tally_engine.py tests/level1/law/test_L1_law_standard.csv --program LLB
python src/level2/cgpa_calculator.py tests/level2/law/test_L2_law_retakes.csv --program LLB
python src/level3/audit_engine.py tests/level3/law/test_L3_law_graduation_ready.csv data/programs/program_knowledge_LLB.md --program LLB
```

---

## 11. Deliverables

### 11.1 Core Deliverables (v2.0)

1. **Source Code:**
   - Level 1: Credit Tally Engine (multi-file solution)
   - Level 2: CGPA Calculator & Policy Enforcer (multi-file solution)
   - Level 3: Audit Engine & Deficiency Reporter (multi-file solution)
   - Shared utilities and constants

2. **Knowledge Base:**
   - `program_knowledge_LLB.md` - Law program requirements
   - `ged_requirements.md` - GED Group 1 & 2 rules
   - `academic_policies.md` - NSU academic policy reference
   - `prerequisite_graph_LLB.md` - Law prerequisite dependencies
   - Updated BSCSE and BSEEE knowledge bases

3. **Test Cases:**
   - 8 Law test cases for Level 1
   - 8 Law test cases for Level 2
   - 10 Law test cases for Level 3
   - Integration tests for multi-program support
   - Policy enforcement tests

4. **Documentation:**
   - Updated README.md with v2.0 features
   - Testing plan for Law program
   - API documentation for all modules
   - Knowledge base format specification
   - Policy implementation guide

5. **Output:**
   - Clear, structured terminal output
   - Audit reports for all test cases
   - Deficiency reports with action items

### 11.2 Optional Enhancements (Bonus)

1. **Enhanced Output:**
   - Export audit reports to Markdown
   - Generate PDF reports (using reportlab)
   - Create HTML dashboard

2. **Advanced Validation:**
   - Prerequisite graph visualization
   - Course sequence recommendations
   - What-if analysis ("What if I drop this course?")

3. **Performance Optimization:**
   - Cache knowledge base parsing
   - Parallel processing for multiple students
   - Database integration (SQLite)

4. **Testing:**
   - Automated test runner
   - Test coverage reporting
   - Performance benchmarking

---

## 12. Version 3.0 Roadmap

### 12.1 Custom CLI Terminal

**Vision:** Transform the command-line tool into an interactive, user-friendly CLI application with modern UI elements.

**Key Features:**

1. **Interactive Menu System:**
```
╔══════════════════════════════════════════════════════════════╗
║           NSU AUDIT CORE SYSTEM v3.0                         ║
║        North South University Graduation Auditor             ║
╚══════════════════════════════════════════════════════════════╝

Main Menu:
  [1] Run Credit Tally (Level 1)
  [2] Calculate CGPA (Level 2)
  [3] Full Graduation Audit (Level 3)
  [4] Multi-Student Batch Audit
  [5] View Academic Policies
  [6] Settings
  [0] Exit

Select option: _
```

2. **Colored Output:**
   - ✅ Green for success/completion
   - ⚠️ Yellow for warnings/in-progress
   - ❌ Red for errors/deficiencies
   - 🔵 Blue for information
   - Color-coded categories (GED, Core, Electives)

3. **Progress Bars:**
```
Analyzing transcript...
[████████████████████████████████████] 100%

Processing courses:
[████████████░░░░░░░░░░░░░░░░░░░░░░░░]  40%  (15/35 courses)

Loading knowledge base...
[████████████████████████████████████] 100%
```

4. **Rich Text Formatting:**
   - Tables with borders (using `rich` or `tabulate`)
   - Indented hierarchies
   - Box-drawing characters
   - Unicode icons (✓, ✗, ⚠, ►)

**Implementation Libraries:**
- `rich` - Modern terminal formatting
- `click` - CLI framework
- `colorama` - Cross-platform colors
- `tqdm` - Progress bars
- `prompt_toolkit` - Interactive prompts

### 12.2 Enhanced Features (v3.0)

1. **Batch Processing:**
   - Process multiple student transcripts at once
   - Generate comparative reports
   - Export to Excel/CSV

2. **Interactive Mode:**
   - Step-by-step wizard for each level
   - Guided waiver input
   - Course selection recommendations

3. **Visualization:**
   - ASCII chart for credit distribution
   - Progress visualization (credits earned over time)
   - CGPA trend graph (semester-wise)

4. **Export Options:**
   - PDF reports (using `reportlab` or `weasyprint`)
   - HTML dashboard (using `jinja2`)
   - JSON/XML data export

5. **Configuration:**
   - Save user preferences (default program, output format)
   - Custom output templates
   - Theme selection (light/dark mode)

6. **Database Integration:**
   - SQLite database for transcript storage
   - Query student records
   - Historical audit tracking

### 12.3 v3.0 Architecture

```
nsu_audit_core/
│
├── src/
│   ├── cli/                         # NEW: CLI Application
│   │   ├── __init__.py
│   │   ├── main.py                  # Main CLI entry point
│   │   ├── menu.py                  # Interactive menu system
│   │   ├── commands.py              # CLI commands (click)
│   │   ├── formatters.py            # Rich text formatters
│   │   ├── progress.py              # Progress bars (tqdm)
│   │   └── themes.py                # Color themes
│   │
│   ├── batch/                       # NEW: Batch Processing
│   │   ├── __init__.py
│   │   ├── batch_processor.py       # Multi-student processing
│   │   ├── report_generator.py      # Comparative reports
│   │   └── export.py                # Export to Excel/CSV
│   │
│   ├── database/                    # NEW: Database Layer
│   │   ├── __init__.py
│   │   ├── models.py                # SQLite models
│   │   ├── queries.py               # Database queries
│   │   └── migrations.py            # Schema migrations
│   │
│   └── visualization/               # NEW: Visualization
│       ├── __init__.py
│       ├── charts.py                # ASCII charts
│       ├── graphs.py                # CGPA trends
│       └── pdf_generator.py         # PDF reports
│
└── config/                          # NEW: Configuration
    ├── settings.yaml                # User preferences
    ├── themes.yaml                  # Color themes
    └── templates/                   # Output templates
        ├── report_template.html
        └── audit_template.pdf
```

### 12.4 v3.0 CLI Examples

**Example 1: Interactive Audit**
```
$ nsu-audit

╔══════════════════════════════════════════════════════════════╗
║           NSU AUDIT CORE SYSTEM v3.0                         ║
╚══════════════════════════════════════════════════════════════╝

Select audit level:
  [1] Credit Tally (Level 1)
  [2] CGPA Calculator (Level 2)
  [3] Full Audit (Level 3)
  
Choice: 3

Select program:
  [1] BSCSE (Computer Science & Engineering)
  [2] BSEEE (Electrical & Electronic Engineering)
  [3] LL.B Honors (Law)
  
Choice: 3

Enter transcript file path:
> tests/level3/law/test_L3_law_graduation_ready.csv

Analyzing transcript...
[████████████████████████████████████] 100%

Processing requirements...
[████████████████████████████████████] 100%

╔══════════════════════════════════════════════════════════════╗
║                  GRADUATION AUDIT RESULTS                    ║
╚══════════════════════════════════════════════════════════════╝

✅ Credits:  130 / 130
✅ CGPA:     3.40
✅ Status:   First Class

Result: ✅ ELIGIBLE FOR GRADUATION

Export report? [y/N]: y
Format [pdf/html/md]: pdf

✅ Report saved: outputs/audit_reports/student_12345_audit.pdf
```

**Example 2: Batch Processing**
```
$ nsu-audit batch --input students/ --program LLB --output reports/

Processing students:
[████████████████████████████████████]  50/50  100%

Summary:
  ✅ Eligible:       35 students (70%)
  ⚠️  Deficiencies:  12 students (24%)
  ❌ On Probation:    3 students (6%)

Comparative report generated:
  📊 reports/batch_summary.xlsx
  📄 reports/batch_report.pdf
```

### 12.5 v3.0 Timeline

**Phase 1: CLI Framework (2 weeks)**
- Implement interactive menu system
- Add colored output and progress bars
- Create rich text formatters

**Phase 2: Enhanced Features (2 weeks)**
- Batch processing
- Export to PDF/HTML
- Visualization (charts, graphs)

**Phase 3: Database Integration (1 week)**
- SQLite database setup
- Student record storage
- Query system

**Phase 4: Testing & Documentation (1 week)**
- Integration testing
- User documentation
- Demo videos

**Total: 6 weeks**

---

## 13. Success Criteria

### 13.1 v2.0 Success Criteria

**Functional Requirements:**
- ✅ Successfully audits BSCSE, BSEEE, and LL.B programs
- ✅ Implements all academic policies (retake, exclusion, probation)
- ✅ Validates Law-specific requirements (GED groups, dissertation)
- ✅ Passes all 59 test cases (33 Engineering + 26 Law)
- ✅ Generates clear, structured output for all levels

**Technical Requirements:**
- ✅ Modular architecture (separate files per level)
- ✅ Clean, well-documented code
- ✅ Consistent error handling
- ✅ Performance: < 5 seconds per audit

**Documentation:**
- ✅ Updated README with v2.0 features
- ✅ Complete API documentation
- ✅ Knowledge base format specification
- ✅ Testing strategy document

### 13.2 v3.0 Success Criteria (Future)

**User Experience:**
- ✅ Interactive CLI with intuitive menus
- ✅ Colored output for better readability
- ✅ Progress indicators for all operations
- ✅ Export to PDF/HTML

**Advanced Features:**
- ✅ Batch processing for multiple students
- ✅ Database integration (SQLite)
- ✅ Visualization (charts, graphs)
- ✅ Configuration management

**Performance:**
- ✅ < 3 seconds for single audit
- ✅ < 30 seconds for batch of 50 students
- ✅ Responsive UI (no freezing)

---

## 14. Questions & Clarifications

Before starting implementation, please confirm:

1. **Law Program Details:**
   - Is LLB407 (Dissertation) absolutely required for graduation?
   - Can students take electives before Year 3?
   - Are there any GED Group 2 restrictions (e.g., must include one from Economics)?

2. **Academic Policies:**
   - Should course exclusion be fully automated or require manual approval?
   - How should we handle students on probation for > 3 semesters?
   - Should the system enforce course registration rules (Level 1-3)?

3. **Output Format:**
   - Is the proposed structured output acceptable for all users?
   - Should we include semester-wise credit progression?
   - Any specific formatting requirements for Law reports?

4. **Testing:**
   - Are 26 Law test cases sufficient?
   - Should we include integration tests for policy enforcement?
   - Need performance benchmarking tests?

5. **v3.0 Features:**
   - Which v3.0 features are highest priority?
   - Should database integration be in v2.0 or v3.0?
   - Any specific export format requirements (PDF template)?

---

## Appendix A: Law Course Codes Reference

### GED Courses

**Group 1:**
- ENG102, ENG103, BEN205, HIS103
- PBH101, CHE101, PHY107, BIO103

**Group 2:**
- ECO101, ECO104, POL101, POL104
- ENG111, PHI101, ENV203, GEO205
- BUS112, SOC101, ANT101

### Core Courses (LLB)

**Year 1:**
- LLB101, LLB102

**Year 2:**
- LLB103, LLB104, LLB201-209

**Year 3:**
- LLB301-307

**Year 4:**
- LLB401-407

### Electives (LLB)
- LLB411-429 (19 courses total)

---

## Appendix B: Prerequisite Graph (Law)

```
LLB101 ─────┬──→ LLB103
            └──→ LLB104

LLB102 ─────┬──→ LLB202
            └──→ LLB206

LLB103 ─────┬──→ LLB304
            └──→ LLB305

LLB202 ─────┬──→ LLB302
            └──→ LLB303

LLB404 ──────→ LLB407
```

---

## Appendix C: Sample Law Student Transcript

```csv
course_code,course_name,credits,grade,semester
ENG102,Introduction to Composition,3,A,Spring 2022
ECO101,Principles of Economics,3,B+,Spring 2022
POL101,Introduction to Political Science,3,B,Spring 2022
BIO103,Biology,4,A-,Spring 2022
LLB101,Introduction to Legal System,3,A,Spring 2022
ENG103,Intermediate Composition,3,A-,Summer 2022
ENG111,Public Speaking,3,B+,Summer 2022
HIS103,Emergence of Bangladesh,3,B,Summer 2022
BEN205,Bangla Language,3,B+,Summer 2022
LLB102,Constitutional Laws of Bangladesh,3,A-,Summer 2022
LLB103,Law of Contract,3,B,Fall 2022
LLB104,Law of Torts,3,B+,Fall 2022
LLB201,Muslim Family and Property Law,3,A-,Fall 2022
LLB202,Law of Crime,3,B+,Fall 2022
LLB203,Law of Equity Trust & Specific Relief,3,A,Fall 2022
LLB204,Company Law,3,B,Spring 2023
LLB205,Laws regarding Transfer of Property,3,B+,Spring 2023
LLB206,Administrative Law,3,A,Spring 2023
LLB207,Law of Registration & Limitation,3,B+,Spring 2023
LLB208,Jurisprudence and Legal Theory,3,A-,Spring 2023
LLB209,Legal Professional Ethics,3,A,Spring 2023
LLB301,Law of Evidence,3,B+,Fall 2023
LLB302,Law of Criminal Procedure Part 1,3,A,Fall 2023
LLB304,Law of Civil Procedure Part 1,3,B,Fall 2023
LLB306,Law of Labour and Employment,3,B+,Fall 2023
LLB411,Clinical Legal Education,3,A-,Fall 2023
LLB303,Law of Criminal Procedure Part 2,3,A-,Spring 2024
LLB305,Law of Civil Procedure Part 2,3,B+,Spring 2024
LLB307,Land Law of Bangladesh,3,A,Spring 2024
LLB412,Fiscal & Taxation Law,3,B+,Spring 2024
LLB413,Environmental Law,3,A,Spring 2024
LLB416,Intellectual Property Law,3,A-,Spring 2024
LLB401,Alternative Dispute Resolution,3,B+,Fall 2024
LLB402,Legal Drafting & Conveyance,3,A,Fall 2024
LLB403,Public International Laws,3,A-,Fall 2024
LLB404,Legal Research,3,A,Fall 2024
LLB417,Banking and Foreign Exchange Law,3,B+,Fall 2024
LLB419,International Criminal Law,3,A-,Fall 2024
LLB405,Trial and Advocacy,3,A,Spring 2025
LLB406,Hindu and Christian Family Law,3,B+,Spring 2025
LLB407,Law Dissertation,3,A,Spring 2025
LLB421,Corporate Insolvency Law,3,A-,Spring 2025
LLB423,Law and Globalization,3,B+,Spring 2025
```

**Statistics:**
- Total Courses: 43
- Total Credits: 130
- CGPA: ~3.40
- Status: Ready for Graduation

---

**End of Document**

**Ready to implement! 🚀**
**Questions? Review Section 14 before starting.**
