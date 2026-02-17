# Level 1 - BSEEE Test Files

## Description
These test files are for Level 1 (Credit Tally Engine) testing with BSEEE program.

## Test Files

### test_bseee_standard.csv
- **Purpose**: Test basic credit calculation for a standard BSEEE student
- **Expected Credits**: ~114
- **What it tests**: Normal BSEEE course load with typical grades

### test_bseee_with_failures.csv
- **Purpose**: Test F grade exclusion from credit count for BSEEE
- **Expected Credits**: Fewer than 114 (varies)
- **What it tests**: How F grades affect BSEEE credit calculation
