# OpenCode Prompt — CSE226 Project 1: The Dept. Admin "Audit Core"
**Course:** CSE226.1 — Vibe Coding | **Instructor:** Dr. Nabeel Mohammed | **Due:** February 24, 2026
**Language:** Python | **Zero external dependencies**

---

## SETUP — Read Before Doing Anything Else

1. Read `CSE226_Proj_1.md` fully. Understand every requirement, every level, and every deliverable.
2. Read `README.md` fully. Understand the architecture, output formats, grading scale, policies, and edge cases.
3. Read all three knowledge files:
   - `program_knowledge_BSCSE.md`
   - `program_knowledge_BSEEE.md`
   - `program_knowledge_LLB.md`
   Understand each program's mandatory courses, credit requirements per category, elective trails, capstone requirements, waiver rules, and prerequisite chains.
4. If anything is ambiguous or unclear after reading all five files, **stop and ask the user for clarification before writing any code**.

---

## FILES TO CREATE AND MAINTAIN THROUGHOUT THE ENTIRE PROJECT

### `tracking.md`
Create this file immediately after reading the source files. Update it after **every significant action**.

It must always contain:
- A checklist of every feature/task across all three levels, marked ✅ Done, 🔄 In Progress, or ⬜ Not Started
- What was completed in the last session
- What is planned next
- Any blockers or open questions
- A **Bugs/Issues** section using this format:

```
## Bugs/Issues

| # | Layer | Description | Status | Fix Applied |
|---|-------|-------------|--------|-------------|
```

---

### `assumptions.md`
Every time you make an assumption — not just at the start, but **throughout the entire project** — log it immediately. Use this format:

```
## Assumption #N — [Step / Layer]

**Context:** What situation triggered this assumption
**Assumption:** What you assumed
**Reason:** Why you assumed instead of asking
**Impact:** What would change if this assumption is wrong
**Source:** [OpenCode assumption / User clarification]
```

- Never skip logging an assumption, no matter how small.
- If the user answers a clarification question, log it immediately as a **user-clarified assumption** with `Source: User clarification`.

---

### `testing_plan.md`
Create this file **before writing any code**. It must contain:
- A definition of what "testing" means for this project
- 8 test cases for L1, 8 test cases for L2, 8 test cases for L3 (as specified in README)
- Integration tests for multi-program support
- Policy enforcement tests
- Expected inputs and expected outputs for each test case
- Actual test results logged as each level is completed

---

### `transcript.csv`
Create with these exact columns:
```
course_code,course_name,credits,grade,semester
```
- All values are case-insensitive (ENG101, eng102, A, a, A- all accepted)
- Include realistic data consistent with the program knowledge files
- Include intentional edge cases: F grades, W grades, I grades, X grades, 0-credit labs, retakes, waivers

---

## NSU GRADING SCALE — Apply Exactly As Defined

| Grade | Points | Grade | Points |
|-------|--------|-------|--------|
| A     | 4.0    | C     | 2.0    |
| A-    | 3.7    | C-    | 1.7    |
| B+    | 3.3    | D+    | 1.3    |
| B     | 3.0    | D     | 1.0    |
| B-    | 2.7    | F/I/W/X | 0.0 (excluded from CGPA) |

**CGPA Formula:**
```
CGPA = Σ(Grade Point × Credits) / Σ(Credits for valid grades)
```
- Only grades A through D are counted in CGPA
- F, I, W, X are excluded from CGPA calculation entirely
- Waived courses are excluded from CGPA calculation
- For retaken courses, only the **best grade** is used in CGPA
- Report CGPA with exactly **2 decimal places**

---

## ACADEMIC STANDING TABLE — Apply Exactly As Defined

| CGPA Range   | Standing                    |
|--------------|-----------------------------|
| 3.80 – 4.00  | Summa Cum Laude             |
| 3.65 – 3.79  | Magna Cum Laude             |
| 3.50 – 3.64  | Cum Laude                   |
| 3.00 – 3.49  | First Class (Good Standing) |
| 2.50 – 2.99  | Second Class (Good Standing)|
| 2.00 – 2.49  | Third Class (Good Standing) |
| Below 2.00   | PROBATION                   |

---

## RETAKE POLICY — Apply Exactly As Defined

- Students may retake any course with grade B or lower
- When retaken, only the **best grade** is used for CGPA
- **Both attempts** appear on transcript
- The lower grade shows 0.0 grade points in transcript
- F grades must be cleared by retaking

---

## WAIVER POLICY — Apply Exactly As Defined

| Program   | Waivable Courses        |
|-----------|-------------------------|
| BSCSE     | ENG102, MAT116          |
| BSEEE     | ENG102, MAT116          |
| LL.B      | ENG102 only             |

- Waived courses do not appear on transcript
- Waived credits **count toward** degree requirements
- Waived courses are **excluded from CGPA** calculation
- System must **prompt the admin** for waiver information during execution

---

## THREE SUPPORTED PROGRAMS — Credit Requirements

| Category       | BSCSE         | BSEEE         | LL.B Honors              |
|----------------|---------------|---------------|--------------------------|
| **Total**      | 130 credits   | 130 credits   | 130 credits              |
| **Foundation** | Univ Core (34) + SEPS (38) | Univ Core (34) + SEPS (38) | GED Group 1 (16) + Group 2 (9) |
| **Major**      | CSE Major Core (42) | EEE Major Core (42) | Core by Year 1–4 (81)  |
| **Electives**  | 6 trails, min 2 from 1 | 5 trails, min 2 from 1 | Pool of 19, pick 8 |
| **Capstone**   | CSE299/499A/499B | EEE299/499A/499B | LLB407 Dissertation    |

---

---

# LEVEL 1 — The Credit Tally Engine (10 Marks)

## Goal
Build a CLI Python script that reads a student transcript CSV and calculates total **valid earned credits**, correctly excluding invalid grades and handling edge cases.

## Script Name and Location
```
src/level1_credit_tally.py
```

## CLI Usage
```bash
python src/level1_credit_tally.py <transcript.csv>
```

## What to Build

- Parse `transcript.csv` — all values are case-insensitive
- Apply this exact credit validity policy:
  - **Valid (count toward credits):** Grades A, A-, B+, B, B-, C+, C, C-, D+, D
  - **Invalid — FAILED:** Grade F — attempted but not earned, excluded from credit total
  - **Invalid — WITHDRAWN:** Grade W — excluded from all totals
  - **Invalid — INCOMPLETE:** Grade I — excluded from all totals
  - **Invalid — MARKED:** Grade X — excluded from all totals
  - **0-credit lab courses** (e.g., CSE225L, EEE211L): counted as completed, do NOT add to credit total
  - **Retaken courses:** both attempts appear in transcript, only the successful/best attempt counts toward credit total
- For **LL.B program:** validate GED Group 1 & 2 separately and show credit breakdowns by year
- Sum only valid earned credits
- Generate output exactly matching this format:

```
=== NSU AUDIT CORE - LEVEL 1 ===
Student: [Student ID]
Program: [Program Name]
Processing: [filename]

╔════════════════════════════════════════════════════════════════╗
║                     CREDIT ANALYSIS                            ║
╚════════════════════════════════════════════════════════════════╝

Total Courses Attempted: [N]
Valid Courses (A-D): [N]
Excluded Courses: [N]
  ├─ [COURSE_CODE] ([GRADE]) - [N] credits [FAILED/WITHDRAWN/INCOMPLETE]
  └─ ...

╔════════════════════════════════════════════════════════════════╗
║                   CREDITS BY CATEGORY                          ║
╚════════════════════════════════════════════════════════════════╝

[Category]:    [earned] / [required] credits  [✓ COMPLETE / ⚠ IN PROGRESS]

Total Earned Credits:  [N] / 130 credits

RESULT: [✓ COMPLETE / ⚠ IN PROGRESS] ([N] credits completed)
```

## Required Test File: `test_L1.csv`
Design 8 test cases that prove the solution handles all edge cases. Must include:
1. Standard passing grades (A through D) — counted
2. F grade — excluded, labeled FAILED
3. W grade — excluded, labeled WITHDRAWN
4. I grade — excluded, labeled INCOMPLETE
5. X grade — excluded, labeled MARKED
6. 0-credit lab course — counted as completed, not toward credit total
7. Retaken course (failed first, passed second) — only passing attempt counts
8. Course attempted multiple times — only best/successful attempt counts

## Edge Cases to Handle
- 0-credit labs (CSE225L, EEE211L, etc.) — completed but 0 credits
- F grade — attempted, not earned
- W grade — not counted toward anything
- I and X grades — incomplete/marked, not counted
- Retaken courses — both appear, only successful one counts
- Case-insensitive input (grade "a" = grade "A")

## Testing Checklist (L1)
Before moving to L2, verify ALL of the following:
- [ ] F grades are excluded from credit count, labeled FAILED
- [ ] W grades are excluded, labeled WITHDRAWN
- [ ] I and X grades are excluded with correct labels
- [ ] 0-credit labs appear in completed courses but add 0 to credit total
- [ ] Retaken courses: only successful attempt counts toward credits
- [ ] Credit total is mathematically correct
- [ ] Output matches the exact format specified above
- [ ] All 8 test cases in `test_L1.csv` pass correctly
- [ ] Case-insensitive input works (a = A, eng102 = ENG102)
- [ ] Log all results in `testing_plan.md`

## Completion Gate — L1
After L1 is fully tested and complete:
- Mark all L1 tasks ✅ in `tracking.md`
- Log all 8 L1 test results in `testing_plan.md`
- **Present `tracking.md` to the user**
- **Wait for the user's explicit confirmation before starting L2**

---

---

# LEVEL 2 — The CGPA Calculator & Waiver Handler (10 Marks)

> ⚠️ Do NOT begin L2 until the user has explicitly confirmed L1 is complete.

## Goal
Extend the tool to calculate weighted **CGPA** using the NSU grading scale, handle course retakes using best-grade policy, process admin-entered waivers, and determine academic standing.

## Script Name and Location
```
src/level2_cgpa_calculator.py
```

## CLI Usage
```bash
python src/level2_cgpa_calculator.py <transcript.csv>
```

## What to Build

- Parse `transcript.csv` — case-insensitive
- Map all letter grades to the NSU grade points table (defined above — use it exactly)
- Apply CGPA calculation rules exactly:
  - Only grades A through D count in CGPA
  - F, I, W, X are excluded from CGPA calculation entirely
  - 0-credit labs do not affect CGPA
  - Waived courses are excluded from CGPA
  - For retaken courses, only the best grade counts — lower grade shows 0.0 grade points
  - Report CGPA to exactly 2 decimal places
- **Waiver prompt interface:** During execution, prompt the admin:
  ```
  Enter waived courses (comma-separated, or NONE):
  ```
  - Accept ENG102 and MAT116 for BSCSE/BSEEE
  - Accept ENG102 only for LLB
  - Waived credits count toward degree requirements but are excluded from CGPA
- Determine academic standing from the table defined above
- Generate output exactly matching this format:

```
=== NSU AUDIT CORE - LEVEL 2 ===
Student: [Student ID]
Program: [Program Name]
Processing: [filename]

Enter waived courses (comma-separated, or NONE): [admin input]

╔════════════════════════════════════════════════════════════════╗
║                     CGPA CALCULATION                           ║
╚════════════════════════════════════════════════════════════════╝

Waivers Applied: [N] course ([N] credits)
  └─ [COURSE_CODE]: [Course Name] ([N] credits)

Retakes Processed: [N] courses
  ├─ [CODE]: [old grade] ([old points]) → [new grade] ([new points])  ✓ IMPROVED
  └─ ...

Calculation:
  Total Grade Points:    [N]
  Total Credits Counted: [N]
  
  CGPA = [points] / [credits] = [X.XX]

╔════════════════════════════════════════════════════════════════╗
║                   ACADEMIC STANDING                            ║
╚════════════════════════════════════════════════════════════════╝

CGPA:             [X.XX]
Standing:         [Standing Label]
Honors:           [None / Cum Laude / Magna / Summa]
Status:           [✓ GOOD STANDING / ⚠ PROBATION]

RESULT: [✓ PASSED / ❌ FAILED] (CGPA = [X.XX])
```

## Required Test File: `test_L2.csv`
Design 8 test cases that stress-test CGPA math and waiver logic. Must include:
1. All grade types (A through D) — verify full mapping is correct
2. W grade present — excluded from CGPA
3. I grade present — excluded from CGPA
4. F grade present — 0 points, excluded from earned credits but shown in attempted
5. 0-credit lab — does not affect CGPA
6. Retaken course (F → B) — verify only best grade used
7. ENG102 waived — excluded from CGPA, credits still count toward degree
8. Scenario where CGPA falls below 2.0 — triggers PROBATION standing

## Edge Cases to Handle
- Retaken courses — detect by duplicate course code, use best grade
- Waived courses — completely exclude from CGPA
- F grades — 0 grade points, count in attempted but not earned
- 0-credit labs — must not affect CGPA calculation
- Multiple waivers — handle any combination
- CGPA exactly at a boundary (e.g., exactly 2.00, exactly 3.50) — check rounding

## Testing Checklist (L2)
Before moving to L3, verify ALL of the following:
- [ ] Full NSU grade-to-point mapping is correct for every grade
- [ ] CGPA formula is mathematically correct to 2 decimal places
- [ ] W, I, X entries are fully excluded from CGPA calculation
- [ ] F grade shows 0.0 grade points and does not count in credit total
- [ ] 0-credit labs do not corrupt CGPA
- [ ] Retake handling: best grade is used, lower grade shows 0.0 points
- [ ] Waiver prompt appears and correctly accepts ENG102/MAT116 input
- [ ] Waived courses are excluded from CGPA but their credits count toward degree
- [ ] PROBATION status triggers correctly when CGPA < 2.00
- [ ] Academic standing label is correct for all 7 ranges
- [ ] Output matches the exact format specified above
- [ ] All 8 test cases in `test_L2.csv` pass correctly
- [ ] Log all results in `testing_plan.md`

## Completion Gate — L2
After L2 is fully tested and complete:
- Mark all L2 tasks ✅ in `tracking.md`
- Log all 8 L2 test results in `testing_plan.md`
- **Present `tracking.md` to the user**
- **Wait for the user's explicit confirmation before starting L3**

---

---

# LEVEL 3 — The Audit & Deficiency Reporter (10 Marks)

> ⚠️ Do NOT begin L3 until the user has explicitly confirmed L2 is complete.

## Goal
Build the full **graduation audit engine**: load the program knowledge file, compare the student's transcript against all requirements, handle retakes accurately, verify electives and prerequisites, flag probation, and produce a complete deficiency report with a graduation eligibility verdict.

## Script Name and Location
```
src/level3_audit_engine.py
```

## CLI Usage
```bash
python src/level3_audit_engine.py <transcript.csv> <program_knowledge.md>
```

## What to Build

- Load program requirements from the provided `program_knowledge.md` file via regex parsing
- Match completed courses against all required categories:
  - **BSCSE/BSEEE:** University Core, SEPS Core, Major Core, Elective Trails, Capstone
  - **LL.B:** GED Group 1, GED Group 2, Core by Year 1–4, Electives (8 from pool of 19), Dissertation (LLB407)
- For each requirement, report as one of:
  - ✅ **COMPLETE** — course passed
  - ❌ **MISSING** — never attempted or never passed
  - ⚠️ **INCOMPLETE** — attempted but not passed (failed or withdrawn)
  - 🔄 **RETAKE** — attempted more than once, show full history
- **Retake Scenario — handle with full accuracy:**
  - Detect all courses with multiple attempts (duplicate course codes)
  - Show: number of attempts, all grades received, which attempt counts (best grade)
  - A failed-then-passed course must clear the requirement — do not list it as missing
  - A course still failing after retakes must still be listed as deficient
  - Log retake resolution policy in `assumptions.md`
- **Elective trail validation:**
  - BSCSE/BSEEE: verify minimum 2 courses from at least one trail
  - LL.B: verify 8 electives completed from the pool of 19
- **Prerequisite check:** flag any course taken before its prerequisite was satisfied
- **Capstone check:** verify capstone courses are complete (CSE299/499A/499B or LLB407)
- **Missing 0-credit labs:** flag required labs (e.g., CSE225L) as missing separately from main course
- **Probation flag:** if CGPA < 2.0, show a clear dedicated warning
- **Graduation Eligibility Verdict** at end of report:
  - `✅ ELIGIBLE FOR GRADUATION` — all requirements met, CGPA ≥ 2.0, credits ≥ 130
  - `❌ NOT ELIGIBLE FOR GRADUATION` — with an exact itemized list of reasons
- Generate output exactly matching this format:

```
=== NSU AUDIT CORE - LEVEL 3 ===
Student: [Student ID]
Program: [Program Name]
Processing: [filename]
Knowledge Base: [program_knowledge file]

╔════════════════════════════════════════════════════════════════╗
║                    GRADUATION AUDIT                            ║
╚════════════════════════════════════════════════════════════════╝

Credits:          [N] / 130 required
CGPA:             [X.XX]
Standing:         [Standing Label]

╔════════════════════════════════════════════════════════════════╗
║                   REQUIREMENT ANALYSIS                         ║
╚════════════════════════════════════════════════════════════════╝

[Category Requirements with ✓ COMPLETE / ⚠ INCOMPLETE breakdown]
  Missing:
    ├─ [COURSE_CODE]: [Course Name] ([N] cr)
    └─ ...

╔════════════════════════════════════════════════════════════════╗
║                   DEFICIENCY REPORT                            ║
╚════════════════════════════════════════════════════════════════╝

Missing Courses: [N] ([N] credits)

[Category]:
  [N]. [COURSE_CODE]: [Course Name] ([N] cr)
       └─ [Year/Semester info]
       └─ Prerequisite: [CODE] ([✓ Complete / ❌ Missing])

╔════════════════════════════════════════════════════════════════╗
║                   ACTION ITEMS                                 ║
╚════════════════════════════════════════════════════════════════╝

To graduate, you must:
  1. Complete [COURSE_CODE] ([N] credits)
  ...

Total credits needed: [N]
Estimated completion: [N] semester(s)

╔════════════════════════════════════════════════════════════════╗
║                  GRADUATION ELIGIBILITY                        ║
╚════════════════════════════════════════════════════════════════╝

RESULT: [✅ ELIGIBLE FOR GRADUATION / ❌ NOT ELIGIBLE FOR GRADUATION]

Reasons:
  ├─ [Reason 1]
  └─ [Reason 2]

Status: [Message]
```

## Required Test File: `test_L3_retake.csv`
Design 8 test cases. The file must specifically cover the Retake Scenario. Must include:
1. Course failed then retaken and passed — must clear the requirement
2. Course attempted multiple times and still failing — must still appear as deficient
3. Course withdrawn (W) then retaken and passed — must clear the requirement
4. Student fully ELIGIBLE for graduation — all requirements met, CGPA ≥ 2.0
5. Student NOT ELIGIBLE — missing mandatory course + CGPA below threshold
6. Missing capstone (CSE499B or LLB407) — flagged as REQUIRED in deficiency
7. Prerequisite violation — course taken before prerequisite was satisfied
8. 0-credit required lab missing — flagged separately from main course

## Edge Cases to Handle
- Course equivalencies (e.g., CSE115 = Programming Language I) — check knowledge file
- Retaken courses: failed then passed → clears requirement
- Elective trail requirements: minimum 2 from one trail (BSCSE/BSEEE)
- Prerequisite violations: taking course before prerequisite completed
- Missing capstone projects (299, 499A, 499B, LLB407)
- 0-credit labs required separately from main course
- All three program types must work: BSCSE, BSEEE, LLB

## Testing Checklist (L3)
Before declaring the project complete, verify ALL of the following:
- [ ] All mandatory courses from the program knowledge file are checked per category
- [ ] Missing courses are correctly identified and listed with reasons
- [ ] Retake: failed-then-passed correctly clears the requirement
- [ ] Retake: still-failing after multiple attempts still shows as deficient
- [ ] Retake: W-then-passed correctly clears the requirement
- [ ] Retake history shows all attempts, grades, and which one counts
- [ ] Elective trail validation works (min 2 from one trail for BSCSE/BSEEE)
- [ ] LL.B elective check: 8 from pool of 19
- [ ] Capstone requirements checked and flagged correctly
- [ ] Prerequisite violations are detected and flagged
- [ ] Required 0-credit labs flagged when missing
- [ ] Probation flag appears when CGPA < 2.0
- [ ] Graduation verdict is correct for both ELIGIBLE and NOT ELIGIBLE scenarios
- [ ] Deficiency report states exact reasons why student cannot graduate
- [ ] Tool works correctly for BSCSE, BSEEE, and LLB programs
- [ ] Output matches the exact format specified above
- [ ] All 8 test cases in `test_L3_retake.csv` pass correctly
- [ ] Integration tests pass for multi-program support
- [ ] Policy enforcement tests pass
- [ ] Log all results in `testing_plan.md`

## Completion Gate — L3
After L3 is fully tested and complete:
- Mark all L3 tasks ✅ in `tracking.md`
- Log all 8 L3 test results in `testing_plan.md`
- **Present the final `tracking.md` to the user for final review**

---

## BUGS AND ISSUES

If anything breaks or behaves unexpectedly at any point, **immediately log it in `tracking.md`** under the Bugs/Issues section:

```
## Bugs/Issues

| # | Layer | Description | Status | Fix Applied |
|---|-------|-------------|--------|-------------|
```

- Do not continue to the next step until the bug is resolved or explicitly deferred by the user.
- If the user defers a bug, mark it as `⏸ Deferred` in the table.

---

## RULES TO FOLLOW AT ALL TIMES

- Never skip a level or begin the next level while the current one is incomplete or unconfirmed by the user.
- Never make an assumption silently — always log it in `assumptions.md` immediately.
- Always update `tracking.md` after completing any task.
- If you are unsure about a requirement, **ask the user** — do not guess silently.
- When the user answers any question, log it in `assumptions.md` as a user-clarified assumption.
- After each level, present `tracking.md` to the user and **wait for explicit confirmation** before proceeding to the next level.
- If something breaks, log it in the **Bugs/Issues** section of `tracking.md` immediately.
- All input is case-insensitive — normalize course codes and grades on read.
- Use zero external dependencies — pure Python only.
- The three scripts must be exactly: `src/level1_credit_tally.py`, `src/level2_cgpa_calculator.py`, `src/level3_audit_engine.py`
- All output must match the exact box-drawing format shown in each level.
