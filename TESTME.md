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

The project has 27 test files. Each file represents a different student scenario.

### Level 1 Tests (Credit Counting):
| File | What it Tests |
|------|---------------|
| `tests/level1/bscse/test_bscse_standard.csv` | BSCSE standard student |
| `tests/level1/bscse/test_bscse_mixed_grades.csv` | BSCSE mixed grades |
| `tests/level1/bscse/test_bscse_with_failures.csv` | BSCSE with F grades |
| `tests/level1/bscse/test_bscse_all_A.csv` | BSCSE all A grades |
| `tests/level1/bscse/test_bscse_invalid_grades.csv` | BSCSE I, W, X grades |
| `tests/level1/bseee/test_bseee_standard.csv` | BSEEE standard student |
| `tests/level1/bseee/test_bseee_with_failures.csv` | BSEEE with F grades |
| `tests/level1/law/test_law_standard.csv` | Law standard student |
| `tests/level1/law/test_law_ged_incomplete.csv` | Law GED incomplete |

### Level 2 Tests (CGPA Calculation):
| File | What it Tests |
|------|---------------|
| `tests/level2/bscse/test_bscse_standard.csv` | BSCSE normal CGPA |
| `tests/level2/bscse/test_bscse_retakes.csv` | BSCSE with retakes |
| `tests/level2/bseee/test_bseee_standard.csv` | BSEEE normal CGPA |
| `tests/level2/law/test_law_standard.csv` | Law normal CGPA |

### Level 3 Tests (Full Audit):
| File | What it Tests |
|------|---------------|
| `tests/level3/bscse/test_bscse_complete.csv` | BSCSE graduation ready |
| `tests/level3/bscse/test_bscse_missing_electives.csv` | BSCSE missing electives |
| `tests/level3/bscse/test_bscse_probation.csv` | BSCSE low CGPA |
| `tests/level3/bseee/test_bseee_complete.csv` | BSEEE graduation ready |
| `tests/level3/law/test_law_complete.csv` | Law graduation ready |
| `tests/level3/law/test_law_missing_dissertation.csv` | Law missing LLB407 |
| `tests/level3/law/test_law_probation.csv` | Law low CGPA |

---

## Step 5: Run Level 1 - Credit Tally

This tells you how many credits a student earned.

### Command:
```bash
python src/level1_credit_tally.py tests/level1/test_L1_1.csv
```

### Example Output:
```
==================================================
=== NSU AUDIT CORE - LEVEL 1 ===
=== CREDIT TALLY ENGINE ===
==================================================
Processing: tests/level1/test_L1_1.csv

Credit Analysis:
  Valid Course Count (A-D): 45
  Excluded Courses (F/I/W/X): 0

Total Earned Credits: 123.0
0-Credit Labs Completed: 5
```

### Try Another Test:
```bash
python src/level1_credit_tally.py tests/level1/test_L1_2.csv
```

**Output will show fewer credits because some courses have F grade.**

---

## Step 6: Run Level 2 - CGPA Calculator

This calculates the student's Grade Point Average.

### Command:
```bash
python src/level2_cgpa_calculator.py tests/level2/test_L2_1.csv
```

### Example Output:
```
Enter waived courses (comma-separated course codes, or press Enter for NONE): 
==================================================
=== NSU AUDIT CORE - LEVEL 2 ===
=== CGPA CALCULATOR & WAIVER HANDLER ===
==================================================
Processing: tests/level2/test_L2_1.csv

CGPA Calculation:
  Total Grade Points: 454.3
  Total Credits Counted: 122

Final CGPA: 3.72
Academic Standing: Magna Cum Laude
```

### Understanding the Output:
- **CGPA 3.72** = Very good! (Above 3.65 = Magna Cum Laude)
- Press **Enter** when asked for waivers (empty = no waivers)

### Try with Waiver:
```bash
python src/level2_cgpa_calculator.py tests/level2/test_L2_3.csv
```

When it asks:
```
Enter waived courses (comma-separated course codes, or press Enter for NONE):
```

Type:
```
ENG102,MAT116
```

Then press Enter.

---

## Step 7: Run Level 3 - Full Graduation Audit

This checks if the student can graduate. It compares their courses against program requirements.

### Command:
```bash
python src/level3_audit_engine.py tests/level3/test_L3_1.csv data/program_knowledge_BSCSE.md
```

### Example Output (Graduation Eligible):
```
Enter waived courses (comma-separated codes, or press Enter for NONE): 
============================================================
=== NSU AUDIT CORE - LEVEL 3 ===
=== GRADUATION AUDIT REPORT ===
============================================================
Program: Bachelor of Science in Computer Science and Engineering
Processing: tests/level3/test_L3_1.csv

Audit Results:
  Total Credits: 123.0 / 130 required
  CGPA: 3.64
  Academic Standing: Cum Laude

DEFICIENCIES FOUND:

  Missing Required Courses:
    University Core:
      - ECO104 (3 credits)
      - POL104 (3 credits)

  Total Missing Credits: 19

GRADUATION STATUS: ✗ NOT ELIGIBLE
```

### Example Output (Eligible Student):
Try with a complete student:
```bash
python src/level3_audit_engine.py tests/level3/test_edge_bseee_complete.csv data/program_knowledge_BSEEE.md
```

### Output:
```
Enter waived courses (comma-separated codes, or press Enter for NONE): 

[...]

GRADUATION STATUS: ✓ ELIGIBLE
```

---

## Step 8: Test with Different Programs

### For BSCSE (Computer Science):
```bash
python src/level3_audit_engine.py tests/level3/test_L3_1.csv data/program_knowledge_BSCSE.md
```

### For BSEEE (Electrical Engineering):
```bash
python src/level3_audit_engine.py tests/level3/test_edge_bseee_complete.csv data/program_knowledge_BSEEE.md
```

### For LL.B Honors (Law):
```bash
python src/level3_audit_engine.py tests/level3/law/test_L3_law_complete.csv data/program_knowledge_LLB.md
```

---

## Step 9: Understanding Grade System

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

## Step 10: What If Scenarios

### Try these tests and see what happens:

#### Test 1: All F grades (No credits)
```bash
python src/level1_credit_tally.py tests/level1/test_edge_all_F.csv
```

**Expected:** 0 credits earned

#### Test 2: Probation (Low CGPA)
```bash
python src/level3_audit_engine.py tests/level3/test_L3_3.csv data/program_knowledge_BSEEE.md
```

**Expected:** Shows "PROBATION" - cannot graduate

#### Test 3: Missing Elective Trail
```bash
python src/level3_audit_engine.py tests/level3/test_L3_4.csv data/program_knowledge_BSCSE.md
```

**Expected:** Shows elective trail violation

---

## Quick Reference Commands

All commands to copy-paste:

```bash
# Level 1 - Credit Tally (BSCSE)
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_standard.csv
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_mixed_grades.csv
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_with_failures.csv
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_all_A.csv

# Level 1 - Credit Tally (BSEEE)
python src/level1_credit_tally.py tests/level1/bseee/test_bseee_standard.csv

# Level 1 - Credit Tally (Law)
python src/level1_credit_tally.py tests/level1/law/test_law_standard.csv

# Level 2 - CGPA Calculator (press Enter when asked)
python src/level2_cgpa_calculator.py tests/level2/bscse/test_bscse_standard.csv
python src/level2_cgpa_calculator.py tests/level2/bscse/test_bscse_retakes.csv
python src/level2_cgpa_calculator.py tests/level2/bseee/test_bseee_standard.csv
python src/level2_cgpa_calculator.py tests/level2/law/test_law_standard.csv

# Level 3 - Full Audit (press Enter when asked)
python src/level3_audit_engine.py tests/level3/bscse/test_bscse_complete.csv data/program_knowledge_BSCSE.md
python src/level3_audit_engine.py tests/level3/bscse/test_bscse_probation.csv data/program_knowledge_BSCSE.md
python src/level3_audit_engine.py tests/level3/bseee/test_bseee_complete.csv data/program_knowledge_BSEEE.md
python src/level3_audit_engine.py tests/level3/law/test_law_complete.csv data/program_knowledge_LLB.md
python src/level3_audit_engine.py tests/level3/law/test_law_missing_dissertation.csv data/program_knowledge_LLB.md
```

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

## Summary

1. Install Python if needed
2. Get project files
3. Open terminal in project folder
4. Run commands:
   - Level 1: `python src/level1_credit_tally.py <testfile>`
   - Level 2: `python src/level2_cgpa_calculator.py <testfile>` (press Enter)
   - Level 3: `python src/level3_audit_engine.py <testfile> <programfile>` (press Enter)

---

**End of Guide**
