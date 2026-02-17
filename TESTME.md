# TESTME - How to Run NSU Audit Core System

**Follow each step carefully. Do not skip any step.**

---

## What is this?

This is a program that checks if an NSU student can graduate. It looks at their transcript (list of courses and grades) and tells you:
- How many credits they earned
- What their CGPA (grade point average) is
- Whether they can graduate or what courses are missing

---

## Step 1: Check if Python is Installed

### On Windows:
1. Press `Windows + R` keys together
2. Type `cmd` and press Enter
3. A black window will open (called Command Prompt)
4. Type this and press Enter:
   ```
   python --version
   ```
5. If you see something like `Python 3.x.x`, it's installed!
6. If you see "python is not recognized", go to Step 1.1

### On Mac:
1. Open **Terminal** (press Cmd + Space, type "Terminal", press Enter)
2. Type:
   ```
   python3 --version
   ```
3. If you see `Python 3.x.x`, it's installed!

### On Linux:
1. Open **Terminal**
2. Type:
   ```
   python3 --version
   ```

---

## Step 1.1: Install Python (If Not Installed)

### On Windows:
1. Go to: https://www.python.org/downloads/
2. Click **Download Python 3.x.x** (latest version)
3. Run the downloaded file
4. **IMPORTANT**: Check the box that says "Add Python to PATH"
5. Click **Install Now**
6. Wait for it to finish
7. Close and reopen Command Prompt
8. Type `python --version` to verify

### On Mac:
1. If not installed, download from https://www.python.org/downloads/
2. Or install via Homebrew:
   ```
   brew install python3
   ```

### On Linux:
1. Open Terminal and type:
   ```
   sudo apt update
   sudo apt install python3
   ```

---

## Step 2: Get the Project Files

You need all the project files on your computer.

### Option A: Download ZIP (Easiest)
1. Go to the project folder on your computer
2. Select ALL these folders and files:
   - `src/` folder
   - `tests/` folder
   - `data/` folder
   - `README.md`
   - `testing_plan.md`
3. Right-click and "Send to > Compressed (zipped) folder"
4. Extract the ZIP file to your desktop

### Option B: Copy from Another Computer
1. Copy the entire project folder to a USB drive
2. Paste it on your computer

---

## Step 3: Open Terminal in Project Folder

### On Windows:
1. Open File Explorer
2. Go to the project folder
3. Click on the address bar at the top
4. Type `cmd` and press Enter
5. Command Prompt opens in that folder

### On Mac/Linux:
1. Open Terminal
2. Type `cd ` (with space after)
3. Drag the project folder into the Terminal window
4. Press Enter

---

## Step 4: Understanding the Test Files

The project has test files organized by level and program.

### Test File Categories:
- **Level 1**: Credit Tally (calculates earned credits)
- **Level 2**: CGPA Calculator (calculates GPA)
- **Level 3**: Full Audit (checks graduation eligibility)

### Programs Supported:
- **BSCSE**: Bachelor of Science in Computer Science and Engineering
- **BSEEE**: Bachelor of Science in Electrical and Electronic Engineering  
- **LLB**: Bachelor of Laws (LL.B Honors)

---

## Step 5: Understanding Grade System

The program understands these grades:

| Grade | Points | Meaning |
|-------|--------|---------|
| A | 4.0 | Excellent |
| A- | 3.7 | |
| B+ | 3.3 | |
| B | 3.0 | Good |
| B- | 2.7 | |
| C+ | 2.3 | |
| C | 2.0 | Average |
| C- | 1.7 | |
| D+ | 1.3 | |
| D | 1.0 | Poor |
| F | 0.0 | Fail (no credit) |
| I | 0.0 | Incomplete |
| W | 0.0 | Withdrawn |
| X | 0.0 | Marked |

Only grades A through D count toward graduation!

---

## Step 6: Running Tests

**IMPORTANT**: When asked for waivers, just press **Enter** to continue with no waivers.

---

### LEVEL 1 - Credit Tally Engine

Calculates total valid earned credits from transcript.

#### BSCSE Tests:

**Test 1: Standard BSCSE Student**
```bash
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_standard.csv
```
What it tests: Basic credit calculation for a complete BSCSE student
Expected: ~123 credits

**Test 2: Mixed Grades**
```bash
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_mixed_grades.csv
```
What it tests: Handling various letter grades (A, B, C, D)
Expected: ~120 credits

**Test 3: With Failures**
```bash
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_with_failures.csv
```
What it tests: Excluding F grades from credit count
Expected: ~108 credits (fewer due to F grades)

**Test 4: All A Grades**
```bash
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_all_A.csv
```
What it tests: Perfect grades scenario
Expected: 120 credits

**Test 5: Invalid Grades**
```bash
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_invalid_grades.csv
```
What it tests: Handling I, W, X grades (excluded from credits)
Expected: ~92 credits (many excluded)

#### BSEEE Tests:

**Test 6: Standard BSEEE Student**
```bash
python src/level1_credit_tally.py tests/level1/bseee/test_bseee_standard.csv
```
What it tests: Basic credit calculation for BSEEE program
Expected: ~114 credits

**Test 7: BSEEE with Failures**
```bash
python src/level1_credit_tally.py tests/level1/bseee/test_bseee_with_failures.csv
```
What it tests: BSEEE with F grades
Expected: Fewer credits due to failures

#### Law Tests:

**Test 8: Standard Law Student**
```bash
python src/level1_credit_tally.py tests/level1/law/test_law_standard.csv
```
What it tests: Credit calculation for LL.B program
Expected: 130 credits (complete)

**Test 9: Law GED Incomplete**
```bash
python src/level1_credit_tally.py tests/level1/law/test_law_ged_incomplete.csv
```
What it tests: Law student missing GED requirements
Expected: Fewer credits, GED incomplete warning

#### Edge Case Tests:

**Test 10: All A Grades (Edge)**
```bash
python src/level1_credit_tally.py tests/level1/test_edge_all_A.csv
```
What it tests: Maximum grade scenario
Expected: 123 credits

**Test 11: All F Grades (Edge)**
```bash
python src/level1_credit_tally.py tests/level1/test_edge_all_F.csv
```
What it tests: Complete failure scenario - 0 credits
Expected: 0 credits

**Test 12: Mixed Invalid Grades (Edge)**
```bash
python src/level1_credit_tally.py tests/level1/test_edge_mixed_invalid.csv
```
What it tests: Mix of I, W, X grades
Expected: ~48 credits

---

### LEVEL 2 - CGPA Calculator

Calculates weighted CGPA using NSU grading scale. **When asked for waivers, press Enter.**

#### BSCSE Tests:

**Test 13: Standard CGPA**
```bash
python src/level2_cgpa_calculator.py tests/level2/bscse/test_bscse_standard.csv
```
Press Enter when asked for waivers.
What it tests: Basic CGPA calculation for BSCSE
Expected: ~3.64 CGPA

**Test 14: With Retakes**
```bash
python src/level2_cgpa_calculator.py tests/level2/bscse/test_bscse_retakes.csv
```
Press Enter when asked for waivers.
What it tests: Retake handling - uses best grade
Expected: Shows retake information, CGPA based on best grades

#### BSEEE Tests:

**Test 15: BSEEE Standard**
```bash
python src/level2_cgpa_calculator.py tests/level2/bseee/test_bseee_standard.csv
```
Press Enter when asked for waivers.
What it tests: CGPA calculation for BSEEE
Expected: ~3.63 CGPA

#### Law Tests:

**Test 16: Law Standard**
```bash
python src/level2_cgpa_calculator.py tests/level2/law/test_law_standard.csv
```
Press Enter when asked for waivers.
What it tests: CGPA calculation for LL.B program
Expected: ~3.62 CGPA

**Test 17: Law CGPA Standard**
```bash
python src/level2_cgpa_calculator.py tests/level2/law/test_L2_law_cgpa_standard.csv
```
Press Enter when asked for waivers.
What it tests: Alternative Law test file
Expected: ~3.61 CGPA

#### Edge Case Tests:

**Test 18: Borderline CGPA**
```bash
python src/level2_cgpa_calculator.py tests/level2/test_edge_borderline_cgpa.csv
```
Press Enter when asked for waivers.
What it tests: CGPA near 2.0 threshold
Expected: ~2.0-2.5 CGPA

**Test 19: Multiple Retakes**
```bash
python src/level2_cgpa_calculator.py tests/level2/test_edge_multiple_retakes.csv
```
Press Enter when asked for waivers.
What it tests: Multiple course retakes
Expected: Shows multiple retake info

---

### LEVEL 3 - Full Graduation Audit

Compares student transcript against program requirements. **When asked for waivers, press Enter.**

**KEY**: You MUST specify the correct program knowledge file:
- For BSCSE students: use `data/program_knowledge_BSCSE.md`
- For BSEEE students: use `data/program_knowledge_BSEEE.md`
- For LL.B students: use `data/program_knowledge_LLB.md`

#### BSCSE Tests:

**Test 20: BSCSE Complete Student**
```bash
python src/level3_audit_engine.py tests/level3/bscse/test_bscse_complete.csv data/program_knowledge_BSCSE.md
```
Press Enter when asked for waivers.
What it tests: Complete BSCSE student - should show graduation eligibility
Expected: Check for missing courses and eligibility status

**Test 21: BSCSE Missing Electives**
```bash
python src/level3_audit_engine.py tests/level3/bscse/test_bscse_missing_electives.csv data/program_knowledge_BSCSE.md
```
Press Enter when asked for waivers.
What it tests: Missing elective trail courses
Expected: NOT ELIGIBLE - elective trail violation

**Test 22: BSCSE Probation**
```bash
python src/level3_audit_engine.py tests/level3/bscse/test_bscse_probation.csv data/program_knowledge_BSCSE.md
```
Press Enter when asked for waivers.
What it tests: Low CGPA (below 2.0)
Expected: NOT ELIGIBLE - PROBATION status

#### BSEEE Tests:

**Test 23: BSEEE Complete**
```bash
python src/level3_audit_engine.py tests/level3/bseee/test_bseee_complete.csv data/program_knowledge_BSEEE.md
```
Press Enter when asked for waivers.
What it tests: Complete BSEEE student
Expected: Check graduation eligibility

#### Law Tests:

**Test 24: Law Complete**
```bash
python src/level3_audit_engine.py tests/level3/law/test_law_complete.csv data/program_knowledge_LLB.md
```
Press Enter when asked for waivers.
What it tests: Complete LL.B student
Expected: Check graduation eligibility

**Test 25: Law Missing Dissertation**
```bash
python src/level3_audit_engine.py tests/level3/law/test_law_missing_dissertation.csv data/program_knowledge_LLB.md
```
Press Enter when asked for waivers.
What it tests: Missing LLB407 (dissertation)
Expected: NOT ELIGIBLE - dissertation required

**Test 26: Law Probation**
```bash
python src/level3_audit_engine.py tests/level3/law/test_law_probation.csv data/program_knowledge_LLB.md
```
Press Enter when asked for waivers.
What it tests: Low CGPA for Law
Expected: NOT ELIGIBLE - PROBATION

**Test 27: Law Complete (Alt)**
```bash
python src/level3_audit_engine.py tests/level3/law/test_L3_law_complete.csv data/program_knowledge_LLB.md
```
Press Enter when asked for waivers.
What it tests: Alternative Law complete test
Expected: Check graduation eligibility

**Test 28: Law Missing Dissertation (Alt)**
```bash
python src/level3_audit_engine.py tests/level3/law/test_L3_law_missing_dissertation.csv data/program_knowledge_LLB.md
```
Press Enter when asked for waivers.
What it tests: Alternative missing dissertation test
Expected: NOT ELIGIBLE

#### Edge Case Tests (Level 3):

**Test 29: Edge - BSEEE Complete**
```bash
python src/level3_audit_engine.py tests/level3/test_edge_bseee_complete.csv data/program_knowledge_BSEEE.md
```
Press Enter when asked for waivers.
What it tests: BSEEE edge case complete student

**Test 30: Edge - EEE Power Trail**
```bash
python src/level3_audit_engine.py tests/level3/test_edge_eee_power_trail.csv data/program_knowledge_BSEEE.md
```
Press Enter when asked for waivers.
What it tests: EEE Power System elective trail

**Test 31: Edge - AI Arch Trails**
```bash
python src/level3_audit_engine.py tests/level3/test_edge_ai_arch_trails.csv data/program_knowledge_BSCSE.md
```
Press Enter when asked for waivers.
What it tests: Multiple elective trails completed

**Test 32: Edge - Single Elective Trail**
```bash
python src/level3_audit_engine.py tests/level3/test_edge_single_elective_trail.csv data/program_knowledge_BSCSE.md
```
Press Enter when asked for waivers.
What it tests: Only one elective trail completed

**Test 33: Edge - Missing Capstone**
```bash
python src/level3_audit_engine.py tests/level3/test_edge_missing_capstone.csv data/program_knowledge_BSCSE.md
```
Press Enter when asked for waivers.
What it tests: Missing capstone projects (CSE499A/B)

**Test 34: Edge - Extra Credits**
```bash
python src/level3_audit_engine.py tests/level3/test_edge_extra_credits.csv data/program_knowledge_BSCSE.md
```
Press Enter when asked for waivers.
What it tests: More than required credits

**Test 35: Edge - Missing Open Elective**
```bash
python src/level3_audit_engine.py tests/level3/test_edge_missing_open_elective.csv data/program_knowledge_BSEEE.md
```
Press Enter when asked for waivers.
What it tests: Missing open elective for BSEEE

**Test 36: Edge - Prerequisite Violation**
```bash
python src/level3_audit_engine.py tests/level3/test_edge_prerequisite_violation.csv data/program_knowledge_BSCSE.md
```
Press Enter when asked for waivers.
What it tests: Prerequisite course not taken

---

## Quick Reference - All Commands

### Level 1 Commands:
```bash
# BSCSE
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_standard.csv
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_mixed_grades.csv
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_with_failures.csv
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_all_A.csv
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_invalid_grades.csv

# BSEEE
python src/level1_credit_tally.py tests/level1/bseee/test_bseee_standard.csv
python src/level1_credit_tally.py tests/level1/bseee/test_bseee_with_failures.csv

# Law
python src/level1_credit_tally.py tests/level1/law/test_law_standard.csv
python src/level1_credit_tally.py tests/level1/law/test_law_ged_incomplete.csv

# Edge Cases
python src/level1_credit_tally.py tests/level1/test_edge_all_A.csv
python src/level1_credit_tally.py tests/level1/test_edge_all_F.csv
python src/level1_credit_tally.py tests/level1/test_edge_mixed_invalid.csv
```

### Level 2 Commands (press Enter for waivers):
```bash
# BSCSE
echo "" | python src/level2_cgpa_calculator.py tests/level2/bscse/test_bscse_standard.csv
echo "" | python src/level2_cgpa_calculator.py tests/level2/bscse/test_bscse_retakes.csv

# BSEEE
echo "" | python src/level2_cgpa_calculator.py tests/level2/bseee/test_bseee_standard.csv

# Law
echo "" | python src/level2_cgpa_calculator.py tests/level2/law/test_law_standard.csv
echo "" | python src/level2_cgpa_calculator.py tests/level2/law/test_L2_law_cgpa_standard.csv

# Edge Cases
echo "" | python src/level2_cgpa_calculator.py tests/level2/test_edge_borderline_cgpa.csv
echo "" | python src/level2_cgpa_calculator.py tests/level2/test_edge_multiple_retakes.csv
```

### Level 3 Commands (press Enter for waivers):
```bash
# BSCSE - use program_knowledge_BSCSE.md
echo "" | python src/level3_audit_engine.py tests/level3/bscse/test_bscse_complete.csv data/program_knowledge_BSCSE.md
echo "" | python src/level3_audit_engine.py tests/level3/bscse/test_bscse_missing_electives.csv data/program_knowledge_BSCSE.md
echo "" | python src/level3_audit_engine.py tests/level3/bscse/test_bscse_probation.csv data/program_knowledge_BSCSE.md

# BSEEE - use program_knowledge_BSEEE.md
echo "" | python src/level3_audit_engine.py tests/level3/bseee/test_bseee_complete.csv data/program_knowledge_BSEEE.md

# Law - use program_knowledge_LLB.md
echo "" | python src/level3_audit_engine.py tests/level3/law/test_law_complete.csv data/program_knowledge_LLB.md
echo "" | python src/level3_audit_engine.py tests/level3/law/test_law_missing_dissertation.csv data/program_knowledge_LLB.md
echo "" | python src/level3_audit_engine.py tests/level3/law/test_law_probation.csv data/program_knowledge_LLB.md
echo "" | python src/level3_audit_engine.py tests/level3/law/test_L3_law_complete.csv data/program_knowledge_LLB.md
echo "" | python src/level3_audit_engine.py tests/level3/law/test_L3_law_missing_dissertation.csv data/program_knowledge_LLB.md

# Edge Cases
echo "" | python src/level3_audit_engine.py tests/level3/test_edge_bseee_complete.csv data/program_knowledge_BSEEE.md
echo "" | python src/level3_audit_engine.py tests/level3/test_edge_eee_power_trail.csv data/program_knowledge_BSEEE.md
echo "" | python src/level3_audit_engine.py tests/level3/test_edge_ai_arch_trails.csv data/program_knowledge_BSCSE.md
echo "" | python src/level3_audit_engine.py tests/level3/test_edge_single_elective_trail.csv data/program_knowledge_BSCSE.md
echo "" | python src/level3_audit_engine.py tests/level3/test_edge_missing_capstone.csv data/program_knowledge_BSCSE.md
echo "" | python src/level3_audit_engine.py tests/level3/test_edge_extra_credits.csv data/program_knowledge_BSCSE.md
echo "" | python src/level3_audit_engine.py tests/level3/test_edge_missing_open_elective.csv data/program_knowledge_BSEEE.md
echo "" | python src/level3_audit_engine.py tests/level3/test_edge_prerequisite_violation.csv data/program_knowledge_BSCSE.md
```

---

## What Each Test File Contains

You can open any test CSV file in Excel or Notepad to see the student data:

```
course_code,course_name,credits,grade,semester
ENG102,Introduction to Composition,3,A,Spring2023
MAT116,Pre-Calculus,0,B,Spring2023
CSE115,Programming Language I,4,A-,Summer2023
HIS103,Emergence of Bangladesh,3,F,Summer2023
```

- `course_code` = Course ID (like CSE115)
- `course_name` = Course name
- `credits` = How many credits (0 = lab)
- `grade` = Letter grade earned
- `semester` = When taken

---

## Troubleshooting

### Problem: "python is not recognized"
**Solution:** Python is not in your PATH. Add it or reinstall with "Add to PATH" checked.

### Problem: "File not found"
**Solution:** You're not in the right folder. Make sure Command Prompt/Terminal is in the project folder.

### Problem: "No module named 'csv'"
**Solution:** You might be using Python 2. Use `python3` instead of `python`.

### Problem: Program asks for input and waits forever
**Solution:** Type your answer and press Enter. If you don't know, just press Enter.

### Problem: Wrong program requirements shown
**Solution:** Make sure you're using the correct program_knowledge.md file for the program (BSCSE/BSEEE/LLB)

---

## Summary

1. Install Python if needed
2. Get project files
3. Open terminal in project folder
4. Run commands:
   - Level 1: `python src/level1_credit_tally.py <testfile>`
   - Level 2: `python src/level2_cgpa_calculator.py <testfile>` (press Enter)
   - Level 3: `python src/level3_audit_engine.py <testfile> <programfile>` (press Enter)
5. For Level 3, always use the correct program knowledge file:
   - BSCSE: `data/program_knowledge_BSCSE.md`
   - BSEEE: `data/program_knowledge_BSEEE.md`
   - LLB: `data/program_knowledge_LLB.md`

---

**End of Guide**
