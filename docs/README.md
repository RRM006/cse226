# NSU Audit Core System

A **command-line graduation audit tool** for North South University (NSU), built in **Python** (zero external dependencies).This system validates student transcripts against BSCSE, BSEEE, and LL.B Honors program requirements.

## Project Overview

- **Version**: 1.0
- **Language**: Python 
- **Project Type**: CSE226 Project 1 - Spring 2026


---

## Architecture — Three Levels

Three independent CLI scripts in `src/`:

### Level 1: `level1_credit_tally.py` — Credit Tally Engine
- Reads transcript CSV → calculates **total earned credits**
- Count only valid earned credits .Excludes invalid grades (`F`, `I`, `W`, `X`)
- Handles **0-credit lab courses** (counted as completed, not toward credit total)
- Handles **retakes** (best grade used)
- For **Law**: validates GED Group 1 & 2 and shows credit breakdowns by year
- Report total valid credits with breakdown
- Distinguish between earned and attempted credits
- Handle 0-credit lab courses correctly

**Usage:**
```bash
python src/level1_credit_tally.py <transcript.csv> 
```

### Level 2: `level2_cgpa_calculator.py` — CGPA Calculator & Waiver Handler
- Calculates **weighted CGPA** (A=4.0 → D=1.0)
- alculate weighted CGPA using NSU grading scale
- Handles **retakes** (best grade only)
- Prompts for **waivers** (ENG102, MAT116) — excluded from CGPA
- Determines **academic standing** (Summa Cum Laude → Probation)
- **FR2.6:** Report CGPA with 2 decimal precision
- 

**Usage:**
```bash
python src/level2_cgpa_calculator.py <transcript.csv> 
```


### Level 3: `level3_audit_engine.py` — Full Audit Engine

- Takes transcript + program knowledge markdown file
- Match completed courses against required courses
- Parses requirements via regex from `.md` file
- Checks all categories: University Core, SEPS Core, Major Core, Capstone, Elective Trails
- Identify missing mandatory courses
- Verify prerequisite requirements
- Flag probation status if CGPA < 2.0
- Generate comprehensive deficiency report
- Determine graduation eligibility (PASS/FAIL)
- **Engineering**: validates elective trail concentration (min 2 from one trail)
- **Law**: validates GED groups, year-by-year core, 8 electives, dissertation (LLB407)
- Outputs deficiency report + graduation eligibility

**Usage:**
```bash
python src/level3_audit_engine.py <transcript.csv> <program_knowledge.md>
```

---


## Three Supported Programs

| Feature | BSCSE | BSEEE | LL.B Honors |
|---|---|---|---|
| **Total** | 130 credits | 130 credits | 130 credits |
| **Foundation** | University Core (34) + SEPS (38) | University Core (34) + SEPS (38) | GED Group 1 (16) + Group 2 (9) |
| **Major** | CSE Major Core (42) | EEE Major Core (42) | Core by Year 1-4 (81) |
| **Electives** | 6 trails (min 2 from 1) | 5 trails (min 2 from 1) | Pool of 19, pick 8 |
| **Capstone** | CSE299/499A/499B | EEE299/499A/499B | LLB407 Dissertation |
| **Waivers** | ENG102, MAT116 | ENG102, MAT116 | ENG102 only |


---


## NSU Grading Scale

| Grade | Points | Grade | Points |
|-------|--------|-------|--------|
| A | 4.0 | C | 2.0 |
| A- | 3.7 | C- | 1.7 |
| B+ | 3.3 | D+ | 1.3 |
| B | 3.0 | D | 1.0 |
| B- | 2.7 | F/I/W/X | 0.0 (excluded) |

**Notes:**
- \* Credits for courses with F grade do not apply towards graduation
- \*\* Grades I, W, X do not apply towards graduation and are not included in CGPA calculation

## Academic Standing

| CGPA Range | Standing |
|------------|----------|
| 3.80 – 4.00 | Summa Cum Laude |
| 3.65 – 3.79 | Magna Cum Laude |
| 3.50 – 3.64 | Cum Laude |
| 3.00 – 3.49 | First Class (Good Standing) |
| 2.50 – 2.99 | Second Class (Good Standing) |
| 2.00 – 2.49 | Third Class (Good Standing) |
| Below 2.00 | PROBATION |

## CGPA Calculation Rules

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

## Retake Policy

- Students may retake any course with grade **B or lower**
- When a course is retaken, only the **best grade** is used for CGPA
- **Both attempts** appear on transcript
- The lower grade shows **0.0 grade points** in transcript
- **F grades must be cleared** by retaking or replacing with appropriate course

## Waiver Policy

- **Common waivers:** ENG102 (for strong English background), MAT116 (for strong Math background)
- Waived courses **do not appear** on transcript
- Waived credits **count toward** degree requirements
- Waived courses are **excluded from CGPA** calculation
- System must **prompt admin** for waiver information

## Implementation Levels

### Level 1: Credit Tally Engine (10 Marks)

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



### Level 2: CGPA Calculator & Waiver Handler (10 Marks)

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

### Level 3: Audit Engine & Deficiency Reporter (10 Marks)

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
- **Missing capstone projects** (299, 499A, 499B etc)
- **0-credit labs** that are required separately from main course

---



## Project Structure

```
//
```



## Output Format Specifications

#### Level 1 Output Example  (Enhanced)

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

#### Level 2 Output Example (Enhanced)

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

#### Level 3 Output Example (Enhanced)

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

**Test Cases:**
   - 8  test cases for Level 1
   - 8  test cases for Level 2
   - 8 test cases for Level 3
   - Integration tests for multi-program support
   - Policy enforcement tests



## Notes

- All transcript CSVs must include: `course_code`, `course_name`, `credits`, `grade`, `semester`
- all are case-insensitive(ENG101,eng102, etc) (accepts 'A', 'a', 'A-', etc.)
- Program knowledge files define requirements in markdown format
- System supports both BSCSE,BSEEE and LLB programs with unified audit engine
