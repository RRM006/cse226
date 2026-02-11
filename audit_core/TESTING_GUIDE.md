# How to Run and Test NSU Audit Core

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.6 or higher
- No additional packages required (uses only standard library)

### Step 1: Navigate to Project Directory
```bash
cd E:\cse226\audit_core
```

### Step 2: Verify Project Structure
Your directory should look like this:
```
audit_core/
├── src/
│   ├── audit_core.py          # Base functionality
│   ├── level1_engine.py       # Level 1 (interactive)
│   ├── level2_engine.py       # Level 2 (interactive)
│   ├── level3_engine.py       # Level 3 (interactive)
│   ├── level2_engine_test.py  # Level 2 (non-interactive)
│   └── level3_engine_test.py  # Level 3 (non-interactive)
├── data/
│   ├── test_L1.csv           # Level 1 test data
│   ├── test_L2.csv           # Level 2 test data
│   └── retake_scenario.csv   # Retake scenario test data
├── pdf/
│   ├── transcript.csv        # Original transcript
│   ├── Audit Core.md         # Project requirements
│   └── program.md            # Program knowledge base
└── README.md                 # Main documentation
```

---

## 🧪 Testing Instructions

### Test Level 1: Credit Tally Engine
**Purpose**: Counts only valid earned credits for graduation

```bash
python src/level1_engine.py data/test_L1.csv
```

**Expected Output**:
- Total Valid Credits: 30.0
- Valid Courses: 10 courses
- Invalid Courses: 7 courses (withdrawals, failures, 0-credit labs)

### Test Level 2: CGPA Calculator with Waiver Handler
**Purpose**: Calculates weighted CGPA and handles waivers

#### Option A: Without Waivers
```bash
python src/level2_engine_test.py data/test_L2.csv
```

**Expected Output**:
- CGPA: ~2.674
- Status: Good Standing
- Graded Courses: 14
- Excluded Courses: 2 (withdrawals)

#### Option B: With Waivers
```bash
python src/level2_engine_test.py data/test_L2.csv "BUS112,ENG102"
```

**Expected Output**:
- CGPA: ~2.577 (lower due to waived courses)
- Waivers Granted: BUS112, ENG102
- Excluded Courses: 3 (including waived courses)

#### Option C: Interactive Version
```bash
python src/level2_engine.py data/test_L2.csv
```
Then enter waivers when prompted (press Enter to finish)

### Test Level 3: Comprehensive Audit & Deficiency Reporter
**Purpose**: Full audit against program requirements

#### Option A: Business Administration Program
```bash
python src/level3_engine_test.py data/test_L2.csv ../pdf/program.md "Business Administration" "BUS112"
```

**Expected Output**:
- Program: Business Administration
- Total Credits Required: 124
- Completed Credits: 38.0
- Graduation Status: NOT ELIGIBLE
- Multiple missing courses listed

#### Option B: Computer Science Program with Retake Scenarios
```bash
python src/level3_engine_test.py data/retake_scenario.csv ../pdf/program.md "Computer Science & Engineering"
```

**Expected Output**:
- Program: Computer Science & Engineering
- Total Credits Required: 130
- Completed Credits: 33.0
- CGPA: ~2.05
- Graduation Status: NOT ELIGIBLE
- Shows how retakes are handled

#### Option C: Interactive Version
```bash
python src/level3_engine.py data/test_L2.csv ../pdf/program.md
```
Then select program and enter waivers when prompted

---

## 📋 Test with Original Data

### Test with Provided Transcript
```bash
# Level 1
python src/level1_engine.py ../pdf/transcript.csv

# Level 2
python src/level2_engine_test.py ../pdf/transcript.csv

# Level 3
python src/level3_engine_test.py ../pdf/transcript.csv ../pdf/program.md "Computer Science & Engineering"
```

---

## 🔍 What to Verify in Each Test

### Level 1 Verification ✅
- [ ] Only passing grades (A, B, C, D) are counted
- [ ] Failed courses (F) are excluded
- [ ] Withdrawals (W) are excluded
- [ ] 0-credit courses are excluded
- [ ] Total credits calculation is correct

### Level 2 Verification ✅
- [ ] CGPA calculation uses correct grade points (A=4.0, B=3.0, etc.)
- [ ] Quality points calculation: Grade Points × Credits
- [ ] Waivered courses are excluded from CGPA
- [ ] Academic standing is correct (≥3.5 = Dean's List, ≥2.0 = Good Standing, <2.0 = Probation)

### Level 3 Verification ✅
- [ ] All mandatory courses are checked
- [ ] Missing courses are correctly identified
- [ ] Credit requirements are verified
- [ ] CGPA requirements are checked (≥2.0)
- [ ] Graduation status is correctly determined
- [ ] Deficiency report is comprehensive

---

## 🐛 Common Issues & Solutions

### Issue: "File not found" error
**Solution**: Make sure you're in the correct directory (`E:\cse226\audit_core`)

### Issue: "Permission denied" error
**Solution**: Run as administrator or check file permissions

### Issue: Unicode encoding error
**Solution**: The test versions handle this automatically. If using interactive versions, your terminal should support UTF-8.

### Issue: "Module not found" error
**Solution**: Ensure you're running from the `audit_core` directory where `src/` folder exists

---

## 📊 Sample Expected Outputs

### Level 1 Sample Output
```
============================================================
LEVEL 1: CREDIT TALLY ENGINE REPORT
============================================================
Total Valid Credits: 30.0
Valid Courses Count: 10
Invalid Courses Count: 7

VALID COURSES:
  ENG102 - 3.0 credits - Grade: A
  MAT116 - 3.0 credits - Grade: B
  ...
```

### Level 2 Sample Output
```
============================================================
LEVEL 2: CGPA CALCULATOR & WAIVER HANDLER REPORT
============================================================
Weighted CGPA: 2.674
Total Quality Points: 117.65
Total Credits for CGPA: 44.0
ACADEMIC STANDING:
  Status: Good Standing
```

### Level 3 Sample Output
```
======================================================================
LEVEL 3: COMPREHENSIVE AUDIT & DEFICIENCY REPORT
======================================================================
Program: Business Administration
Total Credits Required: 124
Completed Credits: 38.0
CGPA: 2.674
GRADUATION STATUS: NOT ELIGIBLE

MISSING REQUIREMENTS:
  GED: PHI101, ENV203
  Core Business: ACT202, MGT314, MGT368, MKT202
  ...

DEFICIENCIES:
  X Missing mandatory GED course: PHI101
  X Insufficient credits: 38.0/124 required
  ...
```

---

## 🎯 Success Criteria

Your testing is successful if:
1. ✅ All commands run without errors
2. ✅ Output shows correct calculations
3. ✅ Edge cases are handled (withdrawals, failures, retakes)
4. ✅ Waiver functionality works
5. ✅ Deficiency reports are accurate

---

## 📞 Need Help?

If you encounter issues:
1. Check Python version: `python --version` (should be 3.6+)
2. Verify directory structure
3. Check file paths in commands
4. Review the main README.md for additional information

**Ready for demonstration!** 🚀