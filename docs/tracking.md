# NSU Audit Core — Project Tracking

## Feature Checklist

### Level 1: Credit Tally Engine (10 Marks)
| # | Feature | Status |
|---|---------|--------|
| 1 | CSV parser (case-insensitive) | ✅ Done |
| 2 | Grade validity (A-D valid, F/I/W/X excluded) | ✅ Done |
| 3 | 0-credit lab handling | ✅ Done |
| 4 | Retake detection (best grade) | ✅ Done |
| 5 | Credits-by-category breakdown | ✅ Done |
| 6 | LL.B GED Group 1 & 2 + year breakdown | ✅ Done |
| 7 | Exact box-drawing output format | ✅ Done |
| 8 | test_L1.csv (8 test cases) | ✅ Done |

### Level 2: CGPA Calculator & Waiver Handler (10 Marks)
| # | Feature | Status |
|---|---------|--------|
| 1 | NSU grade-to-point mapping | ✅ Done |
| 2 | CGPA formula (only A-D counted, 2 dp) | ✅ Done |
| 3 | Retake best-grade logic | ✅ Done |
| 4 | Waiver prompt + program validation | ✅ Done |
| 5 | Academic standing (7 ranges) | ✅ Done |
| 6 | Exact box-drawing output format | ✅ Done |
| 7 | test_L2.csv (8 test cases) | ✅ Done |

### Level 3: Audit & Deficiency Reporter (10 Marks)
| # | Feature | Status |
|---|---------|--------|
| 1 | Program knowledge file parser (regex) | ✅ Done |
| 2 | Course matching per category | ✅ Done |
| 3 | Retake resolution (full history) | ✅ Done |
| 4 | Elective trail validation | ✅ Done |
| 5 | Prerequisite checking | ✅ Done |
| 6 | Capstone verification | ✅ Done |
| 7 | 0-credit lab flagging | ✅ Done |
| 8 | Probation warning (CGPA < 2.0) | ✅ Done |
| 9 | Graduation eligibility verdict | ✅ Done |
| 10 | Deficiency report + action items | ✅ Done |
| 11 | Exact box-drawing output format | ✅ Done |
| 12 | test_L3_retake.csv (8 test cases) | ✅ Done |

## Last Session
- Implemented all 3 levels
- Created all test CSV files
- Verified L1, L2, L3 with test data
- All edge cases working correctly

## Next Steps
- User review and sign-off

## Bugs/Issues

| # | Layer | Description | Status | Fix Applied |
|---|-------|-------------|--------|-------------|
| 1 | L1 | Overlapping categories (PHY107 in both Univ Core and SEPS) | ✅ Fixed | Rewrote category assignment to allow multi-category membership |
| 2 | L3 | MAT120/MAT116 same-semester flagged as prereq violation | ℹ️ By Design | Same-semester treated as not "before" — correct behavior |
