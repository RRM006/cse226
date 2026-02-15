# Testing Plan - NSU Audit Core System v2.0

## Overview

This document outlines the testing strategy, test coverage, and validation criteria for the NSU Audit Core System version 2.0.

## Test Strategy

### Testing Levels

1. **Unit Testing**: Individual function testing (grade mapping, credit calculation)
2. **Integration Testing**: Complete workflows for each level
3. **Edge Case Testing**: Boundary conditions and error scenarios

### Test Data Categories

| Category | Count | Purpose |
|----------|-------|---------|
| BSCSE Tests | 11 | Computer Science program |
| BSEEE Tests | 4 | Electrical Engineering program |
| Law Tests | 7 | LL.B Honors program |
| **Total** | **22** | |

## Test Case Inventory

### Level 1: Credit Tally Engine (9 test files)

| Test File | Description | Program | Expected Credits |
|-----------|-------------|---------|-----------------|
| `test_bscse_standard.csv` | Standard successful student | BSCSE | 123 |
| `test_bscse_mixed_grades.csv` | Mixed grades | BSCSE | ~120 |
| `test_bscse_with_failures.csv` | With F grades | BSCSE | <120 |
| `test_bscse_all_A.csv` | All A grades | BSCSE | 123 |
| `test_bscse_invalid_grades.csv` | I, W, X grades | BSCSE | ~110 |
| `test_bseee_standard.csv` | Standard student | BSEEE | 114 |
| `test_bseee_with_failures.csv` | With F grades | BSEEE | <114 |
| `test_law_standard.csv` | Complete student | Law | 130 |
| `test_law_ged_incomplete.csv` | GED incomplete | Law | <130 |

### Level 2: CGPA Calculator (4 test files)

| Test File | Description | Program | Expected CGPA |
|-----------|-------------|---------|----------------|
| `test_bscse_standard.csv` | Standard CGPA | BSCSE | ~3.64 |
| `test_bscse_retakes.csv` | With retakes | BSCSE | Based on best grades |
| `test_bseee_standard.csv` | Standard CGPA | BSEEE | ~3.5-4.0 |
| `test_law_standard.csv` | Standard CGPA | Law | ~3.6 |

### Level 3: Audit Engine (9 test files)

| Test File | Description | Program | Expected Result |
|-----------|-------------|---------|-----------------|
| `test_bscse_complete.csv` | Complete BSCSE | BSCSE | ELIGIBLE |
| `test_bscse_missing_electives.csv` | Missing electives | BSCSE | NOT ELIGIBLE |
| `test_bscse_probation.csv` | Low CGPA | BSCSE | NOT ELIGIBLE |
| `test_bseee_complete.csv` | Complete BSEEE | BSEEE | ELIGIBLE |
| `test_law_complete.csv` | Complete Law | Law | ELIGIBLE |
| `test_law_missing_dissertation.csv` | Missing LLB407 | Law | NOT ELIGIBLE |
| `test_law_probation.csv` | Low CGPA | Law | NOT ELIGIBLE |

## Program Coverage

### BSCSE Tests
- `test_L1_1.csv`, `test_L1_2.csv`, `test_L1_3.csv`, `test_L1_4.csv`
- `test_L2_1.csv`, `test_L2_2.csv`, `test_L2_3.csv`, `test_L2_4.csv`
- `test_L3_1.csv`, `test_L3_2.csv`, `test_L3_4.csv`
- Edge cases: all except bseee_complete

### BSEEE Tests
- `test_L3_3.csv` (probation)
- `test_edge_bseee_complete.csv`
- `test_edge_eee_power_trail.csv`

## Validation Criteria

### Level 1 - Credit Tally
- [ ] Correctly excludes F, I, W, X grades from credit count
- [ ] Handles 0-credit labs (counted as completion, not credits)
- [ ] Processes retakes correctly (uses best grade)
- [ ] Reports accurate total earned credits

### Level 2 - CGPA Calculator
- [ ] Maps all NSU letter grades to correct grade points
- [ ] Calculates weighted CGPA correctly
- [ ] Handles course retakes (uses best grade only)
- [ ] Excludes waived courses from calculation
- [ ] Excludes I, W, X grades from calculation
- [ ] Reports CGPA with 2 decimal precision

### Level 3 - Audit Engine
- [ ] Loads program requirements from knowledge file
- [ ] Identifies all missing required courses by category
- [ ] Checks elective trail concentration (min 2 from one trail)
- [ ] Verifies capstone project completion
- [ ] Flags probation status when CGPA < 2.0
- [ ] Determines graduation eligibility correctly

## Edge Cases Coverage

| Edge Case | Test File(s) | Covered |
|-----------|---------------|---------|
| 0-credit labs | `test_L1_4.csv` | ✓ |
| All A grades (4.0 CGPA) | `test_edge_all_A.csv` | ✓ |
| All F grades (0 credits) | `test_edge_all_F.csv` | ✓ |
| Probation threshold | `test_edge_borderline_cgpa.csv` | ✓ |
| Multiple retakes | `test_edge_multiple_retakes.csv` | ✓ |
| Prerequisite violation | `test_edge_prerequisite_violation.csv` | ✓ |
| Missing capstone | `test_edge_missing_capstone.csv` | ✓ |
| Extra credits | `test_edge_extra_credits.csv` | ✓ |
| Missing open elective | `test_edge_missing_open_elective.csv` | ✓ |
| Single elective trail | `test_edge_single_elective_trail.csv` | ✓ |
| Multiple trails met | `test_edge_ai_arch_trails.csv` | ✓ |
| BSEEE program | `test_edge_bseee_complete.csv`, `test_edge_eee_power_trail.csv` | ✓ |

## Running Tests

### Individual Level Tests
```bash
# Level 1
python src/level1_credit_tally.py tests/level1/test_L1_1.csv

# Level 2 (will prompt for waivers)
python src/level2_cgpa_calculator.py tests/level2/test_L2_3.csv

# Level 3
python src/level3_audit_engine.py tests/level3/test_L3_1.csv data/program_knowledge_BSCSE.md
```

### Batch Testing (Manual)
Loop through test files and verify expected outputs match.

## Expected Output Formats

### Level 1 Output
```
=== NSU AUDIT CORE - LEVEL 1 ===
=== CREDIT TALLY ENGINE ===
Processing: tests/level1/test_L1_1.csv

Credit Analysis:
  Valid Course Count (A-D): 42
  Excluded Courses (F/I/W/X): 3

Total Earned Credits: 130
0-Credit Labs Completed: 6
```

### Level 2 Output
```
=== NSU AUDIT CORE - LEVEL 2 ===
=== CGPA CALCULATOR & WAIVER HANDLER ===
Processing: tests/level2/test_L2_1.csv

Waivers Applied: 0 (0 credits)

CGPA Calculation:
  Total Grade Points: 442.0
  Total Credits Counted: 130

Final CGPA: 3.40
Academic Standing: First Class (Good Standing)
```

### Level 3 Output
```
=== NSU AUDIT CORE - LEVEL 3 ===
=== GRADUATION AUDIT REPORT ===
Program: Bachelor of Science in Computer Science and Engineering
Processing: tests/level3/test_L3_1.csv

Audit Results:
  Total Credits: 130 / 130 required
  CGPA: 3.55
  Academic Standing: Cum Laude

GRADUATION STATUS: ✓ ELIGIBLE
```

## Known Limitations

1. Prerequisite validation is basic (checks existence, not timing)
2. Transfer credit equivalencies not implemented
3. "What-if" analysis not supported
4. PDF export not available

## Test Maintenance

- Update test CSVs when course codes change
- Verify grade point mappings against official NSU grading scale
- Test with real transcript data when available
