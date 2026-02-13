# NSU Audit Core System
## Product Requirements Document
### CSE226 Project 1 - Spring 2026

---

**Document Information:**
- **Project Name:** NSU Department Admin Audit Core
- **Version:** 1.0
- **Date:** February 2026
- **Due Date:** February 24, 2026

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Overview](#2-project-overview)
3. [System Requirements](#3-system-requirements)
4. [NSU Business Rules & Policies](#4-nsu-business-rules--policies)
5. [Implementation Levels](#5-implementation-levels)
6. [Test Cases](#6-test-cases)
7. [Data Structures & File Formats](#7-data-structures--file-formats)
8. [Deliverables](#8-deliverables)
9. [Success Criteria & Evaluation](#9-success-criteria--evaluation)
10. [Additional Notes & Recommendations](#10-additional-notes--recommendations)

---

## 1. Executive Summary

The NSU Audit Core System is a command-line tool designed to automate graduation eligibility verification for North South University students. This system will serve as the foundational "skill" for future AI-powered administrative agents, ensuring accurate, consistent, and traceable audit processes.

The system validates student transcripts against NSU program requirements, calculates CGPA, handles waivers and retakes, and generates comprehensive deficiency reports. It must handle all edge cases and NSU-specific policies to produce audit-ready outputs.

---

## 2. Project Overview

### 2.1 Purpose

To build a precise, reliable graduation audit engine that:
- Automates credit validation and CGPA calculation
- Enforces NSU academic policies programmatically
- Identifies missing requirements and deficiencies
- Provides clear, actionable audit reports
- Serves as a foundation for future AI agent integration

### 2.2 Scope

This project covers **BSCSE** (BS in Computer Science and Engineering) and **BSEEE** (BS in Electrical and Electronic Engineering) programs at NSU, implementing all graduation requirements, grading policies, and academic regulations as of Spring 2026.

### 2.3 Target Users

- **Primary:** Department administrators conducting graduation audits
- **Secondary:** Faculty advisors reviewing student progress
- **Future:** AI Administrative Agents

---

## 3. System Requirements

### 3.1 Functional Requirements

#### 3.1.1 Credit Validation (Level 1)

- **FR1.1:** Calculate total earned credits from transcript
- **FR1.2:** Exclude courses with grades F, I, W, X from credit count
- **FR1.3:** Handle 0-credit lab courses correctly
- **FR1.4:** Distinguish between earned and attempted credits
- **FR1.5:** Report total valid credits with breakdown

#### 3.1.2 CGPA Calculation & Waivers (Level 2)

- **FR2.1:** Calculate weighted CGPA using NSU grading scale
- **FR2.2:** Handle course retakes (use best grade only)
- **FR2.3:** Process course waivers (exclude from CGPA calculation)
- **FR2.4:** Accept admin input for waiver status (ENG102, MAT116)
- **FR2.5:** Exclude I, W, X grades from CGPA calculation
- **FR2.6:** Report CGPA with 2 decimal precision

#### 3.1.3 Audit & Deficiency Detection (Level 3)

- **FR3.1:** Load program requirements from knowledge file
- **FR3.2:** Match completed courses against required courses
- **FR3.3:** Check category-wise credit requirements (University Core, SEPS Core, Major Core, etc.)
- **FR3.4:** Identify missing mandatory courses
- **FR3.5:** Verify prerequisite requirements
- **FR3.6:** Check elective requirements (specialized trails)
- **FR3.7:** Flag probation status if CGPA < 2.0
- **FR3.8:** Generate comprehensive deficiency report
- **FR3.9:** Determine graduation eligibility (PASS/FAIL)

### 3.2 Non-Functional Requirements

- **NFR1:** Accuracy - 100% compliance with NSU policies
- **NFR2:** Performance - Process student transcript in < 5 seconds
- **NFR3:** Usability - Clear CLI interface with intuitive commands
- **NFR4:** Maintainability - Modular code structure
- **NFR5:** Extensibility - Easy to add new programs/policies

---

## 4. NSU Business Rules & Policies

### 4.1 Grading System

| Numerical Score | Letter Grade | Grade Points | Status |
|----------------|--------------|--------------|---------|
| 93 and above | A | 4.0 | Excellent |
| 90 - 92 | A- | 3.7 | |
| 87 - 89 | B+ | 3.3 | |
| 83 - 86 | B | 3.0 | Good |
| 80 - 82 | B- | 2.7 | |
| 77 - 79 | C+ | 2.3 | |
| 73 - 76 | C | 2.0 | Average |
| 70 - 72 | C- | 1.7 | |
| 67 - 69 | D+ | 1.3 | |
| 60 - 66 | D | 1.0 | Poor |
| Below 60 | F | 0.0 | Failure* |
| - | I | 0.0 | Incomplete** |
| - | W | 0.0 | Withdrawal** |
| - | X | 0.0 | Marked** |

**Notes:**
- \* Credits for courses with F grade do not apply towards graduation
- \*\* Grades I, W, X do not apply towards graduation and are not included in CGPA calculation

### 4.2 Credit Requirements

| Category | BSCSE Credits | BSEEE Credits |
|----------|---------------|---------------|
| University Core | 34 | 34 |
| SEPS Core | 38 | 38 |
| Major Core | 42 | 42 |
| Major Capstone Design Project | 4 | 4 |
| Major Electives | 9 | 9 |
| Open Electives | 3 | 3 |
| **Total** | **130** | **130** |

### 4.3 CGPA Calculation Rules

1. **CGPA = Total Grade Points ÷ Total Credits Counted**
2. Only grades A through D are counted in CGPA
3. Grades I, W, X, F are **excluded** from CGPA calculation
4. Waived courses are **excluded** from CGPA calculation
5. For retaken courses, only the **best grade** is used in CGPA
6. Report CGPA with **2 decimal places**

**Formula:**
```
CGPA = Σ(Grade Point × Credits) / Σ(Credits for valid grades)
```

### 4.4 Retake Policy

- Students may retake any course with grade **B or lower**
- When a course is retaken, only the **best grade** is used for CGPA
- **Both attempts** appear on transcript
- The lower grade shows **0.0 grade points** in transcript
- **F grades must be cleared** by retaking or replacing with appropriate course

### 4.5 Waiver Policy

- **Common waivers:** ENG102 (for strong English background), MAT116 (for strong Math background)
- Waived courses **do not appear** on transcript
- Waived credits **count toward** degree requirements
- Waived courses are **excluded from CGPA** calculation
- System must **prompt admin** for waiver information

### 4.6 Academic Standing

| CGPA Range | Status |
|------------|--------|
| 3.80 - 4.00 | Summa Cum Laude |
| 3.65 - 3.79 | Magna Cum Laude |
| 3.50 - 3.64 | Cum Laude |
| 3.00 - 3.49 | First Class (Good Standing) |
| 2.50 - 2.99 | Second Class (Good Standing) |
| 2.00 - 2.49 | Third Class (Good Standing) |
| **Below 2.00** | **PROBATION - Not Eligible for Graduation** |

---

## 5. Implementation Levels

### 5.1 Level 1: Credit Tally Engine (10 Marks)

#### Objective
Calculate total valid earned credits from a student transcript, excluding invalid grades and handling 0-credit labs correctly.

#### Required Functionality
1. Read transcript CSV file
2. Identify courses with valid credits (grades A through D)
3. Exclude courses with grades F, I, W, X
4. Handle 0-credit lab courses correctly
5. Calculate total earned credits
6. Generate report showing:
   - Total Earned Credits
   - Breakdown by category

#### Edge Cases to Handle
- **0-credit labs** (CSE225L, EEE211L, etc.) - should be counted as course completion, not toward credit total
- **Courses with grade F** - attempted but not earned
- **Courses with grade W** - should not count toward any total
- **Courses with grade I or X** - incomplete/marked, not counted
- **Retaken courses** - both attempts appear, but only successful one counts

---

### 5.2 Level 2: CGPA Calculator & Waiver Handler (10 Marks)

#### Objective
Calculate weighted CGPA according to NSU grading scale, handle course retakes properly, and process course waivers.

#### Required Functionality
1. Map letter grades to grade points using NSU scale
2. Calculate weighted CGPA: `(Total Grade Points) / (Total Credits Counted)`
3. Handle retaken courses - use best grade only
4. Prompt admin for waiver information (ENG102, MAT116)
5. Exclude waived courses from CGPA calculation
6. Exclude grades I, W, X from CGPA calculation
7. Report CGPA with 2 decimal precision
8. Show breakdown:
   - Total Grade Points
   - Total Credits Counted
   - CGPA

#### Edge Cases to Handle
- **Retaken courses** - identify duplicate course codes, use best grade
- **Waived courses** - completely exclude from calculation
- **F grades** - count 0 grade points, but count toward attempted credits
- **0-credit labs** - should not affect CGPA calculation
- **Multiple waivers** - system must handle any combination

---

### 5.3 Level 3: Audit Engine & Deficiency Reporter (10 Marks)

#### Objective
Compare student transcript against complete program requirements, identify missing courses, check prerequisites, and generate comprehensive audit report.

#### Required Functionality
1. Load program requirements from knowledge file
2. Match completed courses against required courses
3. Check category-wise credit requirements (University Core, SEPS Core, Major Core, etc.)
4. Identify missing mandatory courses
5. Verify prerequisite requirements
6. Check elective requirements (specialized trails)
7. Flag probation status if CGPA < 2.0
8. Generate comprehensive deficiency report
9. Determine graduation eligibility (PASS/FAIL)

#### Edge Cases to Handle
- **Course equivalencies** (CSE115 = Programming Language I)
- **Retaken courses** - failed then passed, should clear requirement
- **Elective trail requirements** - minimum 2 courses from one trail
- **Prerequisite violations** - taking course before prerequisite
- **Missing capstone projects** (299, 499A, 499B)
- **0-credit labs** that are required separately from main course

---

## 6. Test Cases

Each level requires **3-4 comprehensive test cases** that validate both typical scenarios and edge cases. Test cases must include input files, expected outputs, and pass/fail criteria.

### 6.1 Level 1 Test Cases: Credit Tally Engine

#### Test Case L1-1: Standard Successful Student

| Field | Details |
|-------|---------|
| **Description** | Student who completed all courses successfully with grades A-D |
| **Input** | `test_L1_1.csv` - 130 credits worth of courses, all with valid grades (A through D)<br>Mix of 3-credit and 4-credit courses, plus 0-credit labs |
| **Expected Output** | Total Earned Credits: 130<br>All courses counted correctly<br>0-credit labs not counted toward credit total |
| **Validation Criteria** | Credit total must equal exactly 130 |

#### Test Case L1-2: Mixed Grades with Failures

| Field | Details |
|-------|---------|
| **Description** | Student with some F grades that should not count toward earned credits |
| **Input** | `test_L1_2.csv` - 140 credits attempted<br>125 credits with valid grades (A-D)<br>10 credits with grade F<br>5 credits with grade W |
| **Expected Output** | Total Earned Credits: 125<br>F grades excluded from earned credits<br>W grades excluded from earned credits |
| **Validation Criteria** | Must correctly exclude F and W grades, credit total = 125 |

#### Test Case L1-3: Incomplete and Withdrawn Courses

| Field | Details |
|-------|---------|
| **Description** | Student with I (Incomplete) and X grades that should not count |
| **Input** | `test_L1_3.csv` - 135 credits attempted<br>128 credits with valid grades<br>4 credits with grade I<br>3 credits with grade X |
| **Expected Output** | Total Earned Credits: 128<br>I and X grades excluded |
| **Validation Criteria** | System must exclude all non-earned grades (I, X) |

#### Test Case L1-4: Zero-Credit Labs Edge Case

| Field | Details |
|-------|---------|
| **Description** | Student with multiple 0-credit labs that should not add to total but should be recognized as completed |
| **Input** | `test_L1_4.csv` - 130 credits regular courses + 6 0-credit labs<br>Labs: CSE225L, CSE231L, CSE311L, CSE331L, EEE211L, EEE312L<br>All labs have grade A or B |
| **Expected Output** | Total Earned Credits: 130<br>0-credit labs recognized as completed but not counted in total |
| **Validation Criteria** | 0-credit courses should not affect credit total |

---

### 6.2 Level 2 Test Cases: CGPA & Waiver Handler

#### Test Case L2-1: Standard CGPA Calculation

| Field | Details |
|-------|---------|
| **Description** | Simple CGPA calculation with no retakes or waivers |
| **Input** | `test_L2_1.csv` - 130 credits with known grade distribution<br>Example: 50 credits at A (4.0), 40 credits at B+ (3.3), 30 credits at B (3.0), 10 credits at C (2.0)<br>No waivers |
| **Expected Output** | CGPA = [(50×4.0) + (40×3.3) + (30×3.0) + (10×2.0)] / 130<br>CGPA = 442 / 130 = 3.40 |
| **Validation Criteria** | CGPA must equal 3.40 with 2 decimal places |

#### Test Case L2-2: Retake Scenario

| Field | Details |
|-------|---------|
| **Description** | Student who retook courses and improved grades - only best grade should count |
| **Input** | `test_L2_2.csv`<br>CSE115: First attempt D (1.0), Retake A (4.0) - 4 credits<br>MAT120: First attempt C (2.0), Retake B+ (3.3) - 3 credits<br>CSE225: First attempt F (0.0), Retake A- (3.7) - 3 credits<br>Remaining 120 credits with average CGPA of 3.5 |
| **Expected Output** | Only best grades counted: CSE115 A (4.0), MAT120 B+ (3.3), CSE225 A- (3.7)<br>Lower grades show 0.0 grade points on transcript<br>Recalculated CGPA excluding failed attempts |
| **Validation Criteria** | System must identify duplicate courses and use best grade only |

#### Test Case L2-3: Course Waivers

| Field | Details |
|-------|---------|
| **Description** | Student with ENG102 and MAT116 waivers - should not count in CGPA |
| **Input** | `test_L2_3.csv` - 130 credits of completed courses<br>Admin input: Waivers granted = ENG102 (3 credits), MAT116 (0 credits)<br>Average CGPA of completed courses: 3.20 |
| **Expected Output** | CGPA calculated excluding ENG102 (3 credits)<br>Total Credits Counted = 127<br>Waived courses credited but not counted in CGPA |
| **Validation Criteria** | Waived credits must be excluded from CGPA calculation |

#### Test Case L2-4: Complex Scenario (Retakes + Waivers + F Grades)

| Field | Details |
|-------|---------|
| **Description** | Complex real-world scenario combining multiple edge cases |
| **Input** | `test_L2_4.csv`<br>3 retaken courses (improved from F to passing)<br>2 waivers (ENG102, MAT116)<br>1 current F grade (not yet retaken)<br>2 W grades<br>1 I grade |
| **Expected Output** | Only best retake grades used<br>Waivers excluded from calculation<br>Current F, W, I grades excluded<br>Accurate CGPA calculated from remaining valid courses |
| **Validation Criteria** | System must handle all conditions simultaneously and accurately |

---

### 6.3 Level 3 Test Cases: Audit & Deficiency Detection

#### Test Case L3-1: Graduation Ready Student

| Field | Details |
|-------|---------|
| **Description** | Perfect student meeting all graduation requirements |
| **Input** | `test_L3_1.csv` + `BSCSE program_knowledge.md`<br>All 130 credits completed with valid grades<br>CGPA = 3.55 (Good Standing)<br>All mandatory courses completed<br>All category requirements met<br>Electives from valid trail (2+ from same trail)<br>All capstone projects completed (CSE299, CSE499A, CSE499B) |
| **Expected Output** | **GRADUATION STATUS: ELIGIBLE**<br>No deficiencies found<br>Honor: Cum Laude (CGPA 3.50-3.64) |
| **Validation Criteria** | System must declare ELIGIBLE and show zero deficiencies |

#### Test Case L3-2: Missing Core Courses

| Field | Details |
|-------|---------|
| **Description** | Student missing mandatory core courses from multiple categories |
| **Input** | `test_L3_2.csv` + `BSCSE program_knowledge.md`<br>120 credits completed<br>CGPA = 3.20<br>Missing: CSE373 (Major Core), MAT350 (SEPS Core), HIS103 (University Core) |
| **Expected Output** | **GRADUATION STATUS: NOT ELIGIBLE**<br>**Missing Required Courses:**<br>- CSE373: Design and Analysis of Algorithms (Major Core, 3 credits)<br>- MAT350: Engineering Mathematics (SEPS Core, 3 credits)<br>- HIS103: Emergence of Bangladesh (University Core, 3 credits)<br>Total Deficiency: 9 credits |
| **Validation Criteria** | System must identify all missing mandatory courses by category |

#### Test Case L3-3: Probation Status (Low CGPA)

| Field | Details |
|-------|---------|
| **Description** | Student with CGPA below 2.0 - automatic probation |
| **Input** | `test_L3_3.csv` + `BSEEE program_knowledge.md`<br>All 130 credits completed<br>CGPA = 1.85 (Below 2.0)<br>All mandatory courses completed |
| **Expected Output** | **GRADUATION STATUS: NOT ELIGIBLE - ACADEMIC PROBATION**<br>Reason: CGPA (1.85) is below minimum requirement of 2.0<br>Student must improve CGPA to graduate |
| **Validation Criteria** | System must flag probation when CGPA < 2.0 regardless of credit completion |

#### Test Case L3-4: Elective Trail Violation

| Field | Details |
|-------|---------|
| **Description** | Student took 9 credits of electives but not minimum 2 from same trail |
| **Input** | `test_L3_4.csv` + `BSCSE program_knowledge.md`<br>130 credits completed, CGPA = 3.40<br>Electives taken: CSE401 (Algorithms Trail), CSE411 (Software Trail), CSE422 (Networks Trail)<br>Only 1 course from each trail, no trail has 2+ courses |
| **Expected Output** | **GRADUATION STATUS: NOT ELIGIBLE**<br>**Elective Trail Requirement Violation:**<br>Student must take minimum 2 courses (6 credits) from ONE specialized trail<br>Current: 1 course from each of 3 different trails<br>Action Required: Take 1 more course from any existing trail |
| **Validation Criteria** | System must enforce specialized trail concentration rule |

---

## 7. Data Structures & File Formats

### 7.1 Transcript CSV Format

The transcript CSV must contain the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `course_code` | String | Course identifier (e.g., CSE115, MAT120) |
| `course_name` | String | Full course name |
| `credits` | Integer/Float | Credit value (0, 1, 3, 4, etc.) |
| `grade` | String | Letter grade (A, A-, B+, B, ... F, I, W, X) |
| `semester` | String | When course was taken (e.g., Spring2023) |

**Example:**
```csv
course_code,course_name,credits,grade,semester
CSE115,Programming Language I,4,A,Spring2023
MAT120,Calculus I,3,B+,Spring2023
CSE225L,Data Structures Lab,0,A,Fall2023
```

### 7.2 Program Knowledge File (Markdown)

The `program_knowledge.md` file should contain structured information about degree requirements. Recommended sections:

1. **Program metadata** (name, total credits required)
2. **University Core courses** list
3. **SEPS Core courses** list
4. **Major Core courses** list
5. **Capstone project requirements**
6. **Elective trails and courses**
7. **Prerequisites mapping**
8. **Waivable courses** list

**Example Structure:**
```markdown
# BSCSE Program Requirements

## Total Credits Required: 130

## University Core (34 Credits)
- ENG102: Introduction to Composition (3 credits) - Waivable
- ENG103: Intermediate Composition (3 credits)
- ...

## SEPS Core (38 Credits)
- MAT116: Pre-Calculus (0 credits) - Waivable
- MAT120: Calculus I (3 credits) - Prerequisite: MAT116
- ...

## Major Core (42 Credits)
- CSE115: Programming Language I (4 credits)
- CSE225: Data Structures and Algorithm (3 credits) - Prerequisite: CSE215
- ...

## Elective Trails
### Algorithms and Computation Trail
- CSE401: Advanced Programming Techniques
- CSE417: Numerical Methods
- ...
```

### 7.3 Output Format Specification

The CLI tool should produce structured output for each level:

#### Level 1 Output
```
=== CREDIT AUDIT REPORT ===
Total Earned Credits: 128
Valid Course Count: 42
Excluded Courses (F/I/W/X): 3
  - CSE311 (F) - 3 credits
  - MAT361 (W) - 3 credits
```

#### Level 2 Output
```
=== CGPA CALCULATION REPORT ===
Total Grade Points: 435.2
Total Credits Counted: 128
CGPA: 3.40
Waivers Applied: ENG102 (3 credits)
Retaken Courses: 2
  - CSE115: D→A (used grade: A)
  - MAT120: C→B+ (used grade: B+)
```

#### Level 3 Output
```
=== GRADUATION AUDIT REPORT ===
GRADUATION STATUS: NOT ELIGIBLE
CGPA: 3.40
Total Credits: 128
Academic Standing: Good Standing (Cum Laude)

DEFICIENCIES:
Missing Core Courses (2):
  - CSE373: Design and Analysis of Algorithms (Major Core, 3 credits)
  - HIS103: Emergence of Bangladesh (University Core, 3 credits)

Elective Trail Status: VIOLATION
  - Requirement: Minimum 2 courses from one trail
  - Current: 1 course from each of 3 trails

ACTION REQUIRED:
1. Complete CSE373
2. Complete HIS103
3. Take one additional elective from existing trail
```

---

## 8. Deliverables

### 8.1 Required Deliverables

1. **Three CLI tools** (one per implementation level) or a single unified tool with level flags
2. **Optimized data files:**
   - `transcript.csv` template
   - `program_knowledge_BSCSE.md`
   - `program_knowledge_BSEEE.md`
3. **Test data files:**
   - `test_L1_1.csv` through `test_L1_4.csv`
   - `test_L2_1.csv` through `test_L2_4.csv`
   - `test_L3_1.csv` through `test_L3_4.csv`
4. **Source code** with clear documentation
5. **README.md** file with usage instructions

### 8.2 Submission Format

Submit a compressed archive (`.zip` or `.tar.gz`) containing:

```
project_root/
├── src/
│   ├── level1_credit_tally.py (or .js, .java, etc.)
│   ├── level2_cgpa_calculator.py
│   ├── level3_audit_engine.py
│   └── utils/
│       ├── grade_mapper.py
│       └── file_parser.py
├── data/
│   ├── program_knowledge_BSCSE.md
│   ├── program_knowledge_BSEEE.md
│   └── transcript_template.csv
├── tests/
│   ├── level1/
│   │   ├── test_L1_1.csv
│   │   ├── test_L1_2.csv
│   │   ├── test_L1_3.csv
│   │   └── test_L1_4.csv
│   ├── level2/
│   │   ├── test_L2_1.csv
│   │   ├── test_L2_2.csv
│   │   ├── test_L2_3.csv
│   │   └── test_L2_4.csv
│   └── level3/
│       ├── test_L3_1.csv
│       ├── test_L3_2.csv
│       ├── test_L3_3.csv
│       └── test_L3_4.csv
├── README.md
└── requirements.txt (or package.json)
```

### 8.3 Documentation Requirements

The **README.md** must include:

1. **Installation instructions**
   - Dependencies
   - Environment setup
2. **Usage examples** for each level
   ```bash
   # Level 1 Example
   python src/level1_credit_tally.py tests/level1/test_L1_1.csv
   
   # Level 2 Example  
   python src/level2_cgpa_calculator.py tests/level2/test_L2_1.csv
   
   # Level 3 Example
   python src/level3_audit_engine.py tests/level3/test_L3_1.csv BSCSE data/program_knowledge_BSCSE.md
   ```
3. **Test case execution guide**
4. **Known limitations** or assumptions
5. **Team member contributions** (if applicable)

---

## 9. Success Criteria & Evaluation

### 9.1 Grading Breakdown (Total: 30 Points)

| Component | Points | Details |
|-----------|--------|---------|
| **Level 1 Correctness** | 10 | Correct credit calculation on all test cases |
| **Level 2 Correctness** | 10 | Accurate CGPA with retakes and waivers |
| **Level 3 Correctness** | 10 | Complete audit with all deficiencies identified |
| **Edge Case Handling** | 5 | Properly handles 0-credit labs, F/I/W/X grades, retakes, waivers |
| **Code Quality** | 3 | Modular structure, clear naming, documentation |
| **Test Cases Quality** | 2 | Comprehensive coverage, realistic scenarios |

### 9.2 Functional Correctness (30%)

**Critical Success Factors:**
- ✅ All test cases pass
- ✅ NSU grading scale correctly implemented
- ✅ Retake logic uses best grade only
- ✅ Waivers properly excluded from CGPA
- ✅ Elective trail requirements validated
- ✅ Probation status correctly flagged

### 9.3 Edge Case Handling (5 Points)

Must correctly handle:
- 0-credit labs (counted as completed, not toward credit total)
- F, I, W, X grades (excluded from CGPA)
- Multiple course retakes
- Missing data or malformed input
- Elective trail concentration rule

### 9.4 Code Quality (3 Points)

Evaluated on:
- **Modularity:** Well-organized code structure
- **Readability:** Clear variable and function naming
- **Documentation:** Appropriate comments
- **Error handling:** Graceful handling of edge cases

### 9.5 Test Cases Quality (2 Points)

Evaluated on:
- **Coverage:** All scenarios tested
- **Realism:** Test cases reflect actual student situations
- **Documentation:** Clear test descriptions
- **Edge cases:** Challenging scenarios included

---

## 10. Additional Notes & Recommendations

### 10.1 Development Tips

1. **Start incrementally:** Build Level 1, test thoroughly, then move to Level 2
2. **Use data structures effectively:** 
   - Dictionaries/maps for grade lookups
   - Sets for tracking course codes
   - Lists for managing course sequences
3. **Test frequently:** Don't wait until the end to test
4. **Validate inputs:** Check for malformed CSV data
5. **Keep `program_knowledge.md` well-structured:** Use consistent formatting for easy parsing

### 10.2 Common Pitfalls to Avoid

- ❌ **Don't count 0-credit labs in credit totals**
- ❌ **Don't forget to exclude waived courses from CGPA**
- ❌ **Don't include F grades in CGPA calculation**
- ❌ **Don't count both attempts when a course is retaken**
- ❌ **Don't overlook elective trail concentration requirement**

### 10.3 Programming Language Recommendations

**Recommended:** Python, JavaScript/Node.js, Java

**Why Python is ideal:**
- Excellent CSV handling (`csv` module)
- Easy file I/O
- String manipulation
- Dictionary/list operations
- Clean, readable code

**Why JavaScript/Node.js works well:**
- Good for CLI tools
- JSON/CSV parsing libraries
- Modern async/await syntax
- npm ecosystem

### 10.4 Future Enhancements (Optional - Bonus)

While not required, consider these extensions:

1. **Multi-program support:** Add more programs (BSCS, BSEE, MBA)
2. **Transfer credit handling:** Support course equivalencies
3. **Semester progression tracking:** Show credit accumulation over time
4. **What-if analysis:** "What if I retake these courses?"
5. **Export to PDF:** Generate professional audit reports
6. **Prerequisite validator:** Flag courses taken before prerequisites

### 10.5 Recommended Tools & Libraries

**Python:**
- `csv` - CSV file handling
- `pandas` - Data manipulation (optional)
- `argparse` - CLI argument parsing
- `json` - JSON handling (if converting MD to JSON)

**JavaScript:**
- `csv-parser` - CSV parsing
- `commander` - CLI framework
- `fs` - File system operations
- `markdown-it` - Markdown parsing

**Java:**
- `OpenCSV` - CSV parsing
- `Apache Commons CLI` - Command-line parsing
- `Apache Commons IO` - File operations

### 10.6 Testing Strategy

1. **Unit testing:** Test individual functions (grade mapper, credit calculator)
2. **Integration testing:** Test complete workflows for each level
3. **Edge case testing:** Focus on boundary conditions
4. **Manual testing:** Run all provided test cases
5. **Cross-validation:** Compare results with manual calculations

### 10.7 Contact & Support

**For questions or clarifications:**
- Consult in-class discussions
- Review official NSU curriculum documents
- Ask during office hours
- Check project announcements

---

## Appendix A: NSU BSCSE Course List

### University Core Courses (34 Credits)

**Languages (12 Credits):**
- ENG102: Introduction to Composition (3)
- ENG103: Intermediate Composition (3)
- ENG111: Public Speaking (3)
- BEN205: Bangla Language (3)

**Humanities (9 Credits):**
- PHI104: Introduction to Ethics (3)
- HIS102: Introduction to World Civilization (3)
- HIS103: Emergence of Bangladesh (3)

**Social Sciences (9 Credits):**
- ECO101/ECO104: Economics (3)
- POL101/POL104: Political Science/Governance (3)
- SOC101/ANT101/ENV203/GEO205: Sociology/Anthropology/Environment/Geography (3)

**Sciences (4 Credits):**
- BIO103: Biology (4)
- PHY107: Physics I (4)
- CHE101: Chemistry I (4)

### SEPS Core (38 Credits)

- MAT116: Pre-Calculus (0)
- MAT120: Calculus I (3)
- MAT130: Calculus II (3)
- MAT250: Calculus III (3)
- MAT361: Probability and Statistics (3)
- MAT125: Linear Algebra (3)
- MAT350: Engineering Mathematics (3)
- PHY107: Physics I with lab (4)
- PHY108: Physics II with lab (4)
- CHE101: Chemistry I with lab (4)
- EEE452: Engineering Economics (3)
- CEE110: Engineering Drawing (1)
- CSE115: Programming Language I (3)
- CSE115L: Programming Language I Lab (1)

### CSE Major Core (42 Credits)

- CSE173: Discrete Mathematics (3)
- CSE215: Programming Language II (3)
- CSE215L: Programming Language II Lab (1)
- CSE225: Data Structures and Algorithm (3)
- CSE225L: Data Structures and Algorithm Lab (0)
- CSE231: Digital Logic Design (3)
- CSE231L: Digital Logic Design Lab (0)
- EEE141: Electrical Circuits I (3)
- EEE141L: Electrical Circuits I Lab (1)
- EEE111: Analog Electronics I (3)
- EEE111L: Analog Electronics I Lab (1)
- CSE311: Database Systems (3)
- CSE311L: Database Systems Lab (0)
- CSE323: Operating Systems Design (3)
- CSE327: Software Engineering (3)
- CSE331: Microprocessor Interfacing & Embedded Systems (3)
- CSE331L: Microprocessor Interfacing & Embedded Systems Lab (0)
- CSE373: Design and Analysis of Algorithms (3)
- CSE332: Computer Organization and Architecture (3)
- CSE425: Concepts of Programming Language (3)

### Capstone Projects (4 Credits)

- CSE299: Junior Design Project I (1)
- CSE499A: Senior Design Project I (1.5)
- CSE499B: Senior Design Project II (1.5)

### CSE Elective Trails

**Algorithms and Computation:**
- CSE401, CSE417, CSE418, CSE426, CSE473, CSE491

**Software Engineering:**
- CSE411, CSE427, CSE428, CSE429, CSE492

**Networks:**
- CSE422, CSE438, CSE482, CSE485, CSE486, CSE493

**Computer Architecture and VLSI:**
- CSE433, CSE435, CSE413, CSE414, CSE415, CSE494

**Artificial Intelligence:**
- CSE440, CSE445, CSE465, CSE467, CSE470, CSE419

**Bioinformatics:**
- CSE446, CSE447, CSE448, CSE449, CSE442, CSE496

---

## Appendix B: Sample CLI Interaction

```bash
$ ./audit_tool.py level1 tests/test_L1_1.csv

=== NSU AUDIT CORE - LEVEL 1 ===
Processing: tests/test_L1_1.csv

Credit Analysis:
  Total Courses: 45
  Valid Courses (A-D): 42
  Excluded Courses: 3
    - CSE311 (F) - 3 credits
    - MAT361 (W) - 3 credits
    - BIO103 (I) - 4 credits
  
Total Earned Credits: 128
0-Credit Labs Completed: 6

RESULT: ✓ PASSED

---

$ ./audit_tool.py level2 tests/test_L2_2.csv

=== NSU AUDIT CORE - LEVEL 2 ===
Processing: tests/test_L2_2.csv

Waivers? (comma-separated course codes, or NONE): ENG102,MAT116

CGPA Calculation:
  Total Grade Points: 442.8
  Total Credits Counted: 127
  Waivers Applied: 2 (3 credits)
    - ENG102 (3 credits)
    - MAT116 (0 credits)
  Retakes Processed: 3
    - CSE115: D (1.0) → A (4.0) ✓
    - MAT120: C (2.0) → B+ (3.3) ✓
    - CSE225: F (0.0) → A- (3.7) ✓

Final CGPA: 3.49
Academic Standing: First Class

RESULT: ✓ PASSED

---

$ ./audit_tool.py level3 tests/test_L3_2.csv BSCSE data/program_knowledge_BSCSE.md

=== NSU AUDIT CORE - LEVEL 3 ===
Program: BSCSE
Processing: tests/test_L3_2.csv

Audit Results:
  Total Credits: 120 / 130 required
  CGPA: 3.20
  Academic Standing: First Class (Good Standing)

DEFICIENCIES FOUND:
  
  Missing Core Courses:
    University Core:
      - HIS103: Emergence of Bangladesh (3 credits)
    
    SEPS Core:
      - MAT350: Engineering Mathematics (3 credits)
    
    Major Core:
      - CSE373: Design and Analysis of Algorithms (3 credits)
  
  Total Missing Credits: 9

  Elective Requirements: ✓ MET
    - AI Trail: 2 courses (CSE440, CSE445)
    - Additional: CSE401

  Capstone Projects: ✓ COMPLETE
    - CSE299, CSE499A, CSE499B

GRADUATION STATUS: ❌ NOT ELIGIBLE

Actions Required:
  1. Complete HIS103 (University Core)
  2. Complete MAT350 (SEPS Core)
  3. Complete CSE373 (Major Core)

RESULT: ✗ DEFICIENCIES DETECTED
```

---

**End of Document**

**Good luck with your implementation! 🚀**
