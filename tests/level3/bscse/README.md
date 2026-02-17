# Level 3 - BSCSE Test Files

## Description
These test files are for Level 3 (Full Graduation Audit) testing with BSCSE program.

**IMPORTANT**: Use `data/program_knowledge_BSCSE.md` with these tests.

## Test Files

### test_bscse_complete.csv
- **Purpose**: Test complete BSCSE student audit
- **Expected**: Shows missing courses (ENV203, GEO205, elective trail)
- **What it tests**: Audit engine detecting missing University Core and elective trails

### test_bscse_missing_electives.csv
- **Purpose**: Test detection of missing elective trail courses
- **Expected**: NOT ELIGIBLE - elective trail violation
- **What it tests**: Elective trail requirement checking

### test_bscse_probation.csv
- **Purpose**: Test low CGPA (probation) detection
- **Expected**: NOT ELIGIBLE - PROBATION status
- **What it tests**: CGPA threshold checking (below 2.0 = probation)
