# Version 2.0 - Changes and New Features

## Overview

Version 2.0 of the NSU Audit Core System expands the graduation eligibility verification to support multi-department auditing, adding the **LL.B Honors (Law)** program alongside the existing Engineering programs (BSCSE, BSEEE).

---

## What's New in v2.0

### 1. Multi-Department Support
- **Added**: LL.B Honors (Law) program
- **Now supports**: 3 programs across 2 departments
  - BSCSE (Engineering)
  - BSEEE (Engineering)
  - LL.B Honors (Law)

### 2. Law Program Requirements
- **GED Group 1**: 16 credits (5 required + 1 science)
- **GED Group 2**: 9 credits (choose 3 from 11)
- **Core Program**: 81 credits (27 courses across 4 years)
- **Electives**: 24 credits (choose 8 from 19 - pool-based)
- **Capstone**: LLB407 Law Dissertation (required)

### 3. GED Validation for Law
- Validates GED Group 1 completion (fixed courses + science)
- Validates GED Group 2 selection (3 from 11)
- Checks alternative course conflicts (e.g., ECO101 OR ECO104, not both)

### 4. Year-wise Progression Tracking
- Core courses tracked by academic year (Year 1-4)
- Identifies missing courses by year

### 5. Elective Model Differences
- **Engineering**: Trail-based (concentration in one area, min 2 courses)
- **Law**: Pool-based (any 8 courses from 19, no concentration required)

### 6. Dissertation Requirement
- LLB407 (Law Dissertation) is mandatory for graduation
- Must complete LLB404 (Legal Research) first
- Must have 100+ credits before taking LLB407

---

## Technical Changes

### Source Files Updated

| File | Changes |
|------|---------|
| `level1_credit_tally.py` | Added Law GED validation, auto-detect program |
| `level2_cgpa_calculator.py` | Added program detection for display |
| `level3_audit_engine.py` | Added Law program audit logic |

### New Data Files

| File | Description |
|------|-------------|
| `data/program_knowledge_LLB.md` | Law program requirements knowledge base |

### New Test Files

| File | Description |
|------|-------------|
| `tests/level1/law/test_L1_law_standard.csv` | Standard Law student |
| `tests/level1/law/test_L1_law_ged_incomplete.csv` | GED incomplete |
| `tests/level2/law/test_L2_law_cgpa_standard.csv` | Standard CGPA |
| `tests/level3/law/test_L3_law_complete.csv` | Graduation ready |
| `tests/level3/law/test_L3_law_missing_dissertation.csv` | Missing dissertation |

---

## Usage

### Auto-detect Program
The system now auto-detects the program from course codes:
- Contains "LLB" → LL.B Honors
- Contains "EEE" → BSEEE
- Otherwise → BSCSE

### Running Tests

```bash
# Law program tests
python src/level1_credit_tally.py tests/level1/law/test_L1_law_standard.csv
python src/level2_cgpa_calculator.py tests/level2/law/test_L2_law_cgpa_standard.csv
python src/level3_audit_engine.py tests/level3/law/test_L3_law_complete.csv data/program_knowledge_LLB.md
```

---

## Key Differences: Engineering vs. Law

| Feature | Engineering (BSCSE/BSEEE) | Law (LL.B) |
|---------|---------------------------|------------|
| Total Credits | 130 | 130 |
| GED | 34 credits (fixed) | 25 credits (Group 1 + 2) |
| Core Courses | 80 credits | 81 credits |
| Electives | 9-12 credits (trails) | 24 credits (pool) |
| Capstone | 3 courses | 1 dissertation |
| Year Tracking | Not required | By year (1-4) |
| Prerequisite Chain | Course-based | Course-based + 100 cr for LLB407 |

---

## Backward Compatibility

- All existing Engineering tests still work
- Existing BSCSE and BSEEE workflows unchanged
- Program is auto-detected but can be specified manually

---

## Future Enhancements (v3.0 Roadmap)

- Interactive CLI with menus
- Colored output
- Batch processing for multiple students
- Database integration
- PDF/HTML report export

---

## Version History

- **v1.0**: Initial release - Engineering programs only (BSCSE, BSEEE)
- **v2.0**: Multi-department support - Added Law program (LL.B Honors)

---

*Last Updated: February 15, 2026*
