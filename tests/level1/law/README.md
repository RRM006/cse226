# Level 1 - Law (LLB) Test Files

## Description
These test files are for Level 1 (Credit Tally Engine) testing with LL.B Honors program.

## Test Files

### test_law_standard.csv
- **Purpose**: Test credit calculation for a complete LL.B student
- **Expected Credits**: 130
- **What it tests**: Full Law program with all required courses

### test_law_ged_incomplete.csv
- **Purpose**: Test GED (General Education) incomplete detection
- **Expected Credits**: Less than 130
- **What it tests**: Law student missing GED requirements

### test_L1_law_standard.csv
- **Purpose**: Alternative standard Law test (equivalent to test_law_standard.csv)
- **Expected Credits**: 130
- **What it tests**: Same as test_law_standard.csv

### test_L1_law_ged_incomplete.csv
- **Purpose**: Alternative GED incomplete test (equivalent to test_law_ged_incomplete.csv)
- **Expected Credits**: Less than 130
- **What it tests**: Same as test_law_ged_incomplete.csv
