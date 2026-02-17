# Level 3 - Law (LLB) Test Files

## Description
These test files are for Level 3 (Full Graduation Audit) testing with LL.B Honors program.

**IMPORTANT**: Use `data/program_knowledge_LLB.md` with these tests.

## Test Files

### test_law_complete.csv
- **Purpose**: Test complete Law student audit
- **Expected**: Shows missing University Core courses
- **What it tests**: Full LL.B audit with all Law-specific requirements

### test_law_missing_dissertation.csv
- **Purpose**: Test missing LLB407 (dissertation) detection
- **Expected**: NOT ELIGIBLE - dissertation required
- **What it tests**: Capstone/dissertation requirement checking

### test_law_probation.csv
- **Purpose**: Test low CGPA (probation) detection for Law
- **Expected**: NOT ELIGIBLE - PROBATION status
- **What it tests**: CGPA threshold for Law program

### test_L3_law_complete.csv
- **Purpose**: Alternative complete Law test
- **Expected**: Similar to test_law_complete.csv
- **What it tests**: Duplicate of test_law_complete.csv

### test_L3_law_missing_dissertation.csv
- **Purpose**: Alternative missing dissertation test
- **Expected**: Similar to test_law_missing_dissertation.csv
- **What it tests**: Duplicate of test_law_missing_dissertation.csv
