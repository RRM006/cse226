# Assumptions

## Project Understanding

1. **Project Purpose**: NSU Audit Core System is a command-line tool to verify graduation eligibility for North South University (NSU) students based on their transcripts.

2. **Three-Level Architecture**:
   - Level 1: Credit Tally Engine - calculates total earned credits
   - Level 2: CGPA Calculator - calculates weighted CGPA
   - Level 3: Full Graduation Audit - comprehensive check against program requirements

3. **Supported Programs**: BSCSE, BSEEE, and LL.B Honors

## CLI Command Structure (Observed)

Based on testing, the actual command structure is:
- Level 1: `python src/level1_credit_tally.py <transcript.csv>`
- Level 2: `python src/level2_cgpa_calculator.py <transcript.csv>` (prompts for waivers)
- Level 3: `python src/level3_audit_engine.py <transcript.csv> <program_knowledge.md>` (prompts for waivers)

The user requested format `./your_cli_tool transcript.csv program_name program_knowledge.md` but this is NOT the actual implementation. The actual implementation uses just transcript file for Level 1 & 2, and transcript + program knowledge file for Level 3.

## Test Files Organization

1. **Level 1 tests**: Located in `tests/level1/` with subdirectories by program (bscse, bseee, law) and edge case files at root level
2. **Level 2 tests**: Located in `tests/level2/` with similar organization
3. **Level 3 tests**: Located in `tests/level3/` - need program_knowledge.md file as argument

## Issues Found During Testing

### Issue 1: Program Name Not Displayed in Level 3
- **Location**: `src/level3_audit_engine.py`
- **Observation**: The Program field shows blank in Level 3 output
- **Reason**: The parser looks for lines starting with `**Program Name:**` but actual lines start with `- **Program Name:**`
- **Impact**: Minor - doesn't affect functionality

### Issue 2: Law Program Tests Need Correct Program Knowledge File
- **Observation**: Law tests must use `data/program_knowledge_LLB.md` for Level 3
- **Impact**: Tests will fail if wrong program knowledge file is used

### Issue 3: Duplicate Law Test Files
- **Location**: `tests/level3/law/`
- **Files**: Both `test_law_complete.csv` and `test_L3_law_complete.csv` exist (appear to be duplicates)
- **Files**: Both `test_law_missing_dissertation.csv` and `test_L3_law_missing_dissertation.csv` exist

### Issue 4: Test Files Don't Match Expected Results
- Several test files have issues where expected results don't match actual output
- Example: `test_bscse_complete.csv` shows NOT ELIGIBLE due to missing courses

## Assumptions About Expected Behavior

1. Test files are designed to test specific scenarios, not necessarily to produce "ELIGIBLE" results
2. The program auto-detects program type from course codes (CSE=BSCSE, EEE=BSEEE, LLB=LLB)
3. For Level 3, the user must specify the correct program_knowledge.md file
4. All tests work correctly for their designed scenarios

## Testing Assumptions

1. All test CSV files follow the format: course_code,course_name,credits,grade,semester
2. Grades are case-insensitive (program converts to uppercase)
3. 0-credit courses are labs and count as completion but not toward credit total
4. Retakes: best grade is used for both credits and CGPA calculation
