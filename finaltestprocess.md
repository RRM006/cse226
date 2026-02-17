# Final Test Process Guide

This document explains how to test the NSU Audit Core System from console (terminal) and VS Code.

---

## Part 1: Testing from Console (Terminal)

### Step 1: Open Terminal in Project Folder

**On Windows:**
1. Open File Explorer
2. Navigate to the project folder (Project_1)
3. Click on the address bar at top
4. Type `cmd` and press Enter

**On Mac:**
1. Open Terminal (Cmd + Space, type "Terminal")
2. Type: `cd ` (with space at end)
3. Drag the project folder into Terminal window
4. Press Enter

**On Linux:**
1. Open Terminal
2. Type: `cd ` (with space at end)
3. Drag the project folder into Terminal window
4. Press Enter

---

### LEVEL 1 - Credit Tally Engine

**Purpose:** Calculates total earned credits from transcript

**Command Format:**
```
python src/level1_credit_tally.py <test_file_path>
```

**Example:**
```
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_standard.csv
```

**What to Type in Console:**
```
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_standard.csv
```

**Input Required:** None - just run the command

---

### LEVEL 2 - CGPA Calculator

**Purpose:** Calculates weighted CGPA with retake and waiver handling

**Command Format:**
```
python src/level2_cgpa_calculator.py <test_file_path>
```

**Example:**
```
python src/level2_cgpa_calculator.py tests/level2/bscse/test_bscse_standard.csv
```

**What to Type in Console:**
```
python src/level2_cgpa_calculator.py tests/level2/bscse/test_bscse_standard.csv
```

**Input Required:** When you see this message:
```
Enter waived courses (comma-separated course codes, or press Enter for NONE):
```
**Action:** Just press **Enter** (empty = no waivers)

---

### LEVEL 3 - Full Graduation Audit

**Purpose:** Checks graduation eligibility against program requirements

**Command Format:**
```
python src/level3_audit_engine.py <test_file_path> <program_knowledge_file>
```

**Important:** You MUST use the correct program knowledge file:
- BSCSE → `data/program_knowledge_BSCSE.md`
- BSEEE → `data/program_knowledge_BSEEE.md`
- LLB → `data/program_knowledge_LLB.md`

**Example (BSCSE):**
```
python src/level3_audit_engine.py tests/level3/bscse/test_bscse_complete.csv data/program_knowledge_BSCSE.md
```

**What to Type in Console:**
```
python src/level3_audit_engine.py tests/level3/bscse/test_bscse_complete.csv data/program_knowledge_BSCSE.md
```

**Input Required:** When you see this message:
```
Enter waived courses (comma-separated codes, or press Enter for NONE):
```
**Action:** Just press **Enter** (empty = no waivers)

---

## Part 2: Testing from VS Code

### Step 1: Open Project in VS Code
1. Open VS Code
2. Click **File** → **Open Folder**
3. Select the `Project_1` folder
4. Click **Select Folder**

### Step 2: Run Using VS Code Terminal

**Method 1 - Using Built-in Terminal:**
1. Press `Ctrl + `` (backtick) to open Terminal panel
2. Terminal opens at bottom of VS Code
3. Type the same commands as Console section above

**Method 2 - Using Run Button:**
1. Install **Python** extension by Microsoft (if not installed)
2. Open any file in `src/` folder (e.g., `level1_credit_tally.py`)
3. Look for **"Run Python File"** button in top-right corner
4. Click the button to run

**Method 3 - Using Debug Mode:**
1. Click **Run and Debug** icon in left sidebar (or press `Ctrl + Shift + D`)
2. Click **"create a launch.json file"** link
3. Select **Python** from the dropdown
4. Replace the content with this:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Level 1 - Credit Tally",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/level1_credit_tally.py",
            "args": ["tests/level1/bscse/test_bscse_standard.csv"],
            "console": "integratedTerminal"
        },
        {
            "name": "Level 2 - CGPA Calculator",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/level2_cgpa_calculator.py",
            "args": ["tests/level2/bscse/test_bscse_standard.csv"],
            "console": "integratedTerminal"
        },
        {
            "name": "Level 3 - Audit Engine (BSCSE)",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/level3_audit_engine.py",
            "args": ["tests/level3/bscse/test_bscse_complete.csv", "data/program_knowledge_BSCSE.md"],
            "console": "integratedTerminal"
        },
        {
            "name": "Level 3 - Audit Engine (BSEEE)",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/level3_audit_engine.py",
            "args": ["tests/level3/bseee/test_bseee_complete.csv", "data/program_knowledge_BSEEE.md"],
            "console": "integratedTerminal"
        },
        {
            "name": "Level 3 - Audit Engine (LLB)",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/level3_audit_engine.py",
            "args": ["tests/level3/law/test_law_complete.csv", "data/program_knowledge_LLB.md"],
            "console": "integratedTerminal"
        }
    ]
}
```

5. Save the file (Ctrl + S)
6. Select the test configuration from dropdown at top
7. Press **F5** to run

---

## Quick Copy-Paste Commands

### Level 1 Tests (No input needed):
```bash
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_standard.csv
python src/level1_credit_tally.py tests/level1/bscse/test_bscse_with_failures.csv
python src/level1_credit_tally.py tests/level1/bseee/test_bseee_standard.csv
python src/level1_credit_tally.py tests/level1/law/test_law_standard.csv
```

### Level 2 Tests (Press Enter when asked):
```bash
python src/level2_cgpa_calculator.py tests/level2/bscse/test_bscse_standard.csv
python src/level2_cgpa_calculator.py tests/level2/bscse/test_bscse_retakes.csv
python src/level2_cgpa_calculator.py tests/level2/bseee/test_bseee_standard.csv
python src/level2_cgpa_calculator.py tests/level2/law/test_law_standard.csv
```

### Level 3 Tests (Press Enter when asked):

**For BSCSE program:**
```bash
python src/level3_audit_engine.py tests/level3/bscse/test_bscse_complete.csv data/program_knowledge_BSCSE.md
python src/level3_audit_engine.py tests/level3/bscse/test_bscse_probation.csv data/program_knowledge_BSCSE.md
```

**For BSEEE program:**
```bash
python src/level3_audit_engine.py tests/level3/bseee/test_bseee_complete.csv data/program_knowledge_BSEEE.md
```

**For LLB program:**
```bash
python src/level3_audit_engine.py tests/level3/law/test_law_complete.csv data/program_knowledge_LLB.md
python src/level3_audit_engine.py tests/level3/law/test_law_missing_dissertation.csv data/program_knowledge_LLB.md
```

---

## Summary Table

| Level | Console Command | VS Code | Input Required |
|-------|-----------------|---------|----------------|
| 1 | `python src/level1_credit_tally.py <file>` | Terminal or Run Button | None |
| 2 | `python src/level2_cgpa_calculator.py <file>` | Terminal or Run Button | Press Enter |
| 3 | `python src/level3_audit_engine.py <file> <program.md>` | Terminal or Run Button | Press Enter |

---

## Important Notes

1. **For Level 3**: Always use the correct program knowledge file:
   - BSCSE students → `data/program_knowledge_BSCSE.md`
   - BSEEE students → `data/program_knowledge_BSEEE.md`
   - LLB students → `data/program_knowledge_LLB.md`

2. **Waiver Input**: When asked for waivers, just press Enter to continue with no waivers

3. **Working Directory**: Make sure you're in the `Project_1` folder when running commands

4. **Test Files**: All test files are in the `tests/` folder organized by level and program

---

**End of Guide**
