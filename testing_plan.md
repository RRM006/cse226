# Testing Plan - NSU Audit Core System

## Overview

This document outlines the testing strategy, test coverage, and validation criteria for the NSU Audit Core System.

## Test Strategy

### Testing Levels

1. **Unit Testing**: Individual function testing (grade mapping, credit calculation)
2. **Integration Testing**: Complete workflows for each level
3. **Edge Case Testing**: Boundary conditions and error scenarios

### Test Data Categories

| Category | Count | Purpose |
|----------|-------|---------|
| PRD-specified tests | 12 | Core functionality validation |
| Edge case tests | 12 | Boundary conditions |
| **Total** | **24** | |

## Test Case Inventory

### Level 1: Credit Tally Engine (7 test files)

| Test File | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_L1_1.csv` | Standard successful student (130 credits, all A-D) | Total: 130 credits |
| `test_L1_2.csv` | Mixed grades with failures (125 valid, 10 F, 5 W) | Total: 125 credits |
| `test_L1_3.csv` | Incomplete and withdrawn (128 valid, 4 I, 3 X) | Total: 128 credits |
| `test_L1_4.csv` | Zero-credit labs (130 + 6 labs) | Total: 130 credits, 6 labs |
| `test_edge_all_A.csv` | All A grades - maximum CGPA scenario | Total: 130 credits |
| `test_edge_all_F.csv` | All F grades - zero credits | Total: 0 credits |
| `test_edge_mixed_invalid.csv` | Mix of I, W, X grades | Total: based on valid grades |

### Level 2: CGPA Calculator (5 test files)

| Test File | Description | Expected Result |
|-----------|-------------|-----------------|
| `test_L2_1.csv` | Standard CGPA (50 A + 40 B+ + 30 B + 10 C) | CGPA: 3.40 |
| `test_L2_2.csv` | Retake scenario (CSE115: D→A, MAT120: C→B+, CSE225: F→A-) | Best grades used |
| `test_L2_3.csv` | Course waivers (ENG102, MAT116) | Waivers excluded from CGPA |
| `test_L2_4.csv` | Complex (3 retakes + 2 waivers + F + W + I) | All conditions handled |
| `test_edge_borderline_cgpa.csv` | CGPA just below 2.0 (probation) | CGPA: ~1.85 |
| `test_edge_multiple_retakes.csv` | Multiple course retakes | Best grades used |

### Level 3: Audit Engine (12 test files)

| Test File | Description | Program | Expected Result |
|-----------|-------------|---------|-----------------|
| `test_L3_1.csv` | Graduation ready student | BSCSE | ELIGIBLE |
| `test_L3_2.csv` | Missing core courses | BSCSE | NOT ELIGIBLE - missing CSE373, HIS103, MAT350 |
| `test_L3_3.csv` | Probation status | BSEEE | NOT ELIGIBLE - CGPA < 2.0 |
| `test_L3_4.csv` | Elective trail violation | BSCSE | NOT ELIGIBLE - 1 from each trail |
| `test_edge_bseee_complete.csv` | Complete BSEEE student | BSEEE | ELIGIBLE |
| `test_edge_missing_capstone.csv` | Missing capstone projects | BSCSE | NOT ELIGIBLE - missing 499A/499B |
| `test_edge_extra_credits.csv` | Extra credits beyond 130 | BSCSE | ELIGIBLE |
| `test_edge_missing_open_elective.csv` | Missing open elective | BSCSE | NOT ELIGIBLE |
| `test_edge_dual_program_cse_ece.csv` | Both CSE and EEE courses | BSCSE | Check major core |
| `test_edge_prerequisite_violation.csv` | Course before prerequisite | BSCSE | Flag in report |
| `test_edge_eee_power_trail.csv` | EEE power system trail | BSEEE | ELIGIBLE |
| `test_edge_single_elective_trail.csv` | Single trail only (1 course) | BSCSE | NOT ELIGIBLE |
| `test_edge_ai_arch_trails.csv` | Two trails with 2+ each | BSCSE | ELIGIBLE |
| `test_edge_open_elective.csv` | With open elective | BSCSE | ELIGIBLE |

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
