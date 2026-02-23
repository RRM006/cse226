# NSU Audit Core — Testing Plan

## Definition of Testing

Testing for this project means verifying that each CLI script produces correct, complete output when given a transcript CSV containing specific edge cases. Each test case is a row (or set of rows) in the test CSV that exercises one specific behavior. We verify by running the script and checking the output against expected results.

---

## Level 1 Test Cases (`test_L1.csv`)

| # | Test Case | Input (course/grade) | Expected Output | Result |
|---|-----------|---------------------|-----------------|--------|
| 1 | Standard passing grades (A through D) | CSE115/A, MAT120/B, PHI104/B+ | Credits counted | ✅ PASS |
| 2 | F grade excluded | CSE173/F | Excluded, labeled FAILED | ✅ PASS |
| 3 | W grade excluded | CSE231/W | Excluded, labeled WITHDRAWN | ✅ PASS |
| 4 | I grade excluded | HIS102/I | Excluded, labeled INCOMPLETE | ✅ PASS |
| 5 | X grade excluded | ECO101/X | Excluded, labeled MARKED | ✅ PASS |
| 6 | 0-credit lab course | CSE225L/A (0 cr) | Counted as completed, 0 credits | ✅ PASS |
| 7 | Retake: F then pass | CSE173/F → CSE173/B | Only B counts: 3 credits | ✅ PASS |
| 8 | Multiple retakes (best counts) | MAT130/C → D → B+ | Only B+ counts: 3 credits | ✅ PASS |

### L1 Verification Notes
- Total attempted: 25 rows, Valid: 19 courses, Excluded: 4 (I, X, F, W)
- Case insensitive: "b+" correctly normalized to "B+"
- Total earned: 48 credits (correct for partial transcript)

---

## Level 2 Test Cases (`test_L2.csv`)

| # | Test Case | Input Scenario | Expected Output | Result |
|---|-----------|---------------|-----------------|--------|
| 1 | All grade types mapped | A=4.0, A-=3.7, B+=3.3, etc. | Correct point values | ✅ PASS |
| 2 | W grade excluded from CGPA | HIS102/W | Not in CGPA calc | ✅ PASS |
| 3 | I grade excluded from CGPA | ECO101/I | Not in CGPA calc | ✅ PASS |
| 4 | F grade excluded from CGPA | CSE173/F | 0 pts, excluded from CGPA | ✅ PASS |
| 5 | 0-credit lab no CGPA effect | CSE225L/A (0 cr) | Does not affect CGPA | ✅ PASS |
| 6 | Retake F→B best grade | CSE173/F → B | Only B(3.0) used | ✅ PASS |
| 7 | ENG102 waived | Waiver: ENG102 | Excluded from CGPA, 3cr toward degree | ✅ PASS |
| 8 | CGPA calculation verified | Full transcript | 2.71 (no waiver), 2.66 (waiver) | ✅ PASS |

### L2 Verification Notes
- Without waiver: CGPA = 176.2 / 65 = 2.71 (manually verified)
- With ENG102 waiver: CGPA = 165.1 / 62 = 2.66 (manually verified)
- Standing: Second Class (Good Standing) — correct for 2.50-2.99 range

---

## Level 3 Test Cases (`test_L3_retake.csv`)

| # | Test Case | Input Scenario | Expected Output | Result |
|---|-----------|---------------|-----------------|--------|
| 1 | Failed then passed clears req | CSE225/F → A | ✅ RESOLVED, requirement cleared | ✅ PASS |
| 2 | Still failing after retakes | CSE311/F → F | ❌ STILL DEFICIENT | ✅ PASS |
| 3 | W then passed clears req | CSE327/W → B+ | ✅ RESOLVED, requirement cleared | ✅ PASS |
| 4 | NOT ELIGIBLE for graduation | Missing courses + credits | ❌ NOT ELIGIBLE with reasons | ✅ PASS |
| 5 | Missing capstone | No CSE499B | Flagged as CAPSTONE - REQUIRED | ✅ PASS |
| 6 | Prerequisite violation | MAT120 same semester as MAT116 | Flagged as prereq violation | ✅ PASS |
| 7 | Missing 0-credit lab | No CSE225L | Flagged in deficiency | ✅ PASS |
| 8 | Full retake history shown | 3 retake courses | All attempts, grades, resolution shown | ✅ PASS |

### L3 Verification Notes
- Audit correctly identifies 4 missing items (CSE225L, CSE311, CSE499B, Open Elective)
- Trail requirement: Artificial Intelligence Trail satisfied (2 courses: CSE440, CSE445)
- CGPA: 3.18, First Class standing
- Retake analysis shows full history with attempt count and grade progression

---

## Integration Tests

| Test | Status |
|------|--------|
| L3 with BSCSE transcript + program_knowledge_BSCSE.md | ✅ PASS |
| L1 with main transcript.csv | ✅ PASS |
| L2 with ENG102 waiver | ✅ PASS |

## Policy Enforcement Tests

| Test | Status |
|------|--------|
| Waiver validation: only allowed courses accepted per program | ✅ PASS |
| Retake policy: best grade always used | ✅ PASS |
| F grade excluded from CGPA but shown as attempted | ✅ PASS |
| 0-credit labs don't affect CGPA or credit totals | ✅ PASS |
