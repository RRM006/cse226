# Level 1 - BSCSE Test Files

## Description
These test files are for Level 1 (Credit Tally Engine) testing with BSCSE program.

## Test Files

### test_bscse_standard.csv
- **Purpose**: Test basic credit calculation for a standard BSCSE student
- **Expected Credits**: ~123
- **What it tests**: Normal grade scenario with A, B, C, D grades

### test_bscse_mixed_grades.csv
- **Purpose**: Test handling of various letter grades
- **Expected Credits**: ~120
- **What it tests**: Mixed grades across the grading scale

### test_bscse_with_failures.csv
- **Purpose**: Test F grade exclusion from credit count
- **Expected Credits**: ~108 (fewer due to F grades)
- **What it tests**: How F grades are handled (excluded from credits)

### test_bscse_all_A.csv
- **Purpose**: Test maximum grade scenario
- **Expected Credits**: 120
- **What it tests**: All courses with A grade

### test_bscse_invalid_grades.csv
- **Purpose**: Test invalid grade handling (I, W, X)
- **Expected Credits**: ~92
- **What it tests**: How I (Incomplete), W (Withdrawn), X (Marked) grades are excluded
