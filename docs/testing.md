# NSU Audit Core — Testing Plan

*Combined testing plan from Phase 1 and Phase 2*  
*Course: CSE226.1 — Vibe Coding | Instructor: Dr. Nabeel Mohammed*

---

## What "Testing" Means for NSU Audit Core

Testing means verifying that each script produces correct, complete output when given a transcript CSV containing specific edge cases. For Phase 2, testing also covers API endpoints, OCR accuracy, and concurrent user load.

---

# PART I: Phase 1 Testing

## Level 1 Test Cases

| # | Test Case | Input (course/grade) | Expected Output |
|---|-----------|---------------------|-----------------|
| 1 | Standard passing grades (A through D) | CSE115/A, MAT120/B, PHI104/B+ | Credits counted |
| 2 | F grade excluded | CSE173/F | Excluded, labeled FAILED |
| 3 | W grade excluded | CSE231/W | Excluded, labeled WITHDRAWN |
| 4 | I grade excluded | HIS102/I | Excluded, labeled INCOMPLETE |
| 5 | X grade excluded | ECO101/X | Excluded, labeled MARKED |
| 6 | 0-credit lab course | CSE225L/A (0 cr) | Counted as completed, 0 credits |
| 7 | Retake: F then pass | CSE173/F → CSE173/B | Only B counts: 3 credits |
| 8 | Multiple retakes (best counts) | MAT130/C → D → B+ | Only B+ counts: 3 credits |

---

## Level 2 Test Cases

| # | Test Case | Input Scenario | Expected Output |
|---|-----------|---------------|-----------------|
| 1 | All grade types mapped | A=4.0, A-=3.7, B+=3.3, etc. | Correct point values |
| 2 | W grade excluded from CGPA | HIS102/W | Not in CGPA calc |
| 3 | I grade excluded from CGPA | ECO101/I | Not in CGPA calc |
| 4 | F grade excluded from CGPA | CSE173/F | 0 pts, excluded from CGPA |
| 5 | 0-credit lab no CGPA effect | CSE225L/A (0 cr) | Does not affect CGPA |
| 6 | Retake F→B best grade | CSE173/F → B | Only B(3.0) used |
| 7 | ENG102 waived | Waiver: ENG102 | Excluded from CGPA, 3cr toward degree |
| 8 | CGPA calculation verified | Full transcript | 2.71 (no waiver), 2.66 (waiver) |

---

## Level 3 Test Cases

| # | Test Case | Input Scenario | Expected Output |
|---|-----------|---------------|-----------------|
| 1 | Failed then passed clears req | CSE225/F → A | RESOLVED, requirement cleared |
| 2 | Still failing after retakes | CSE311/F → F | STILL DEFICIENT |
| 3 | W then passed clears req | CSE327/W → B+ | RESOLVED, requirement cleared |
| 4 | NOT ELIGIBLE for graduation | Missing courses + credits | NOT ELIGIBLE with reasons |
| 5 | Missing capstone | No CSE499B | Flagged as CAPSTONE - REQUIRED |
| 6 | Prerequisite violation | MAT120 same semester as MAT116 | Flagged as prereq violation |
| 7 | Missing 0-credit lab | No CSE225L | Flagged in deficiency |
| 8 | Full retake history shown | 3 retake courses | All attempts, grades, resolution shown |

---

## Integration Tests

| Test | Status |
|------|--------|
| L3 with BSCSE transcript + program_knowledge_BSCSE.md | ✅ PASS |
| L1 with main transcript.csv | ✅ PASS |
| L2 with ENG102 waiver | ✅ PASS |

---

## Policy Enforcement Tests

| Test | Status |
|------|--------|
| Waiver validation: only allowed courses accepted per program | ✅ PASS |
| Retake policy: best grade always used | ✅ PASS |
| F grade excluded from CGPA but shown as attempted | ✅ PASS |
| 0-credit labs don't affect CGPA or credit totals | ✅ PASS |

---

# PART II: Phase 2 Testing

## Testing Layers

Phase 2 testing covers four layers:

1. **Unit tests** — individual service functions (audit, OCR, DB helpers) tested in isolation
2. **API integration tests** — full HTTP request/response cycle tested with `pytest` + `httpx`
3. **OCR tests** — image extraction accuracy tests with sample transcript images
4. **Load tests** — 20 concurrent users simulated with Locust

---

## Test Files

```
tests/
├── test_audit_service.py     # Unit tests for audit service wrapper
├── test_ocr.py               # OCR extraction tests
├── test_api.py               # API integration tests
├── test_history.py           # History routes tests
├── test_users.py             # Admin user management tests
├── locustfile.py             # Load test (20 concurrent users)
└── ocr_samples/
    ├── clean_transcript.png  # Clean, well-formatted transcript image
    └── low_quality.jpg       # Blurry/skewed image for confidence testing
```

---

## Audit Service Unit Tests

### AS-1: Level 1 — Valid CSV, BSCSE
**Input:** `tests/BSCSE/L1/L1_BSCSE_001_basic_passing.csv`, program=BSCSE, level=1, waivers=[]
**Expected:** `result_json.total_credits` matches Phase 1 Level 1 output

### AS-2: Level 2 — CGPA with Waivers, BSCSE
**Input:** `tests/BSCSE/L2/L2_BSCSE_002_waiver.csv`, program=BSCSE, level=2, waivers=['ENG102', 'MAT116']
**Expected:** CGPA calculation matches Phase 1 Level 2 output; waivers excluded

### AS-3: Level 3 — Full Audit, Graduation Eligible, BSCSE
**Input:** `tests/BSCSE/L3/L3_BSCSE_001_complete.csv`, program=BSCSE, level=3, waivers=[]
**Expected:** `result_json.eligible = true`, 0 missing courses

### AS-4: Level 3 — Full Audit, Not Eligible, Missing Capstone
**Input:** `tests/BSCSE/L3/L3_BSCSE_006_missing_capstone.csv`, program=BSCSE, level=3, waivers=[]
**Expected:** `result_json.eligible = false`, CSE499B in missing_courses

### AS-5: Level 3 — LLB Program, Missing Core Year 4
**Input:** `tests/LLB/L3/L3_LLB_002_deficient.csv`, program=LLB, level=3, waivers=['ENG102']
**Expected:** `result_json.eligible = false`, year 4 courses in missing_courses

### AS-6: Level 3 — Retake Scenario, Passed After Fail
**Input:** `tests/BSCSE/L3/L3_BSCSE_003_retakes.csv`, program=BSCSE, level=3, waivers=[]
**Expected:** Failed-then-passed course clears the requirement

---

## CLI Auth Tests

### AUTH-1: Login with NSU Email — Success
**Command:** `python cli/audit_cli.py login` → authenticate with `<name>@northsouth.edu`
**Expected:** Credentials saved to `~/.nsu_audit/credentials.json`

### AUTH-2: Login with Non-NSU Gmail — Rejected
**Command:** `python cli/audit_cli.py login` → authenticate with any `@gmail.com` account
**Expected:** Error message: "only @northsouth.edu accounts are permitted"

### AUTH-3: Audit Command Without Login — Blocked
**Command:** `python cli/audit_cli.py l1 tests/BSCSE/L1/L1_BSCSE_001_basic_passing.csv BSCSE` (no prior login)
**Expected:** Error message: "You must be logged in to run audits"

### AUTH-4: Logout — Credentials Deleted
**Command:** `python cli/audit_cli.py logout`
**Expected:** Credentials file deleted

---

## OCR Tests

### OCR-1: PNG Transcript Image — Rows Extracted
**Input:** `tests/nsu_transcript_ocr/Screenshot_20260309_214956.png`
**Expected:** 15+ rows extracted with confidence ≥ 0.90

### OCR-2: PDF Transcript — Rows Extracted
**Input:** `tests/nsu_transcript_ocr/681844277-Transcript.pdf`
**Expected:** 20+ rows extracted with confidence ≥ 0.90

### OCR-3: OCR Output → Audit Engine
**Input:** OCR output from PDF, program=BSEEE, level=1
**Expected:** Extracted CSV feeds into audit engine without error

### OCR-4: Confidence Warning Rules
**Input:** Any transcript with mixed quality
**Expected:** Rows < 0.70 excluded, 0.70-0.84 with warning, ≥ 0.85 accepted

---

## API Integration Tests

### API-1: Health Check — No Auth
**Request:** `GET /health`
**Expected:** 200, `{"status": "ok", "version": "2.0"}`

### API-2: Protected Route — No Token
**Request:** `GET /api/v1/history` (no Authorization header)
**Expected:** 401 Unauthorized

### API-3: CSV Audit — Valid Request
**Request:** `POST /api/v1/audit/csv` with valid JWT + BSCSE CSV + level=3
**Expected:** 200, response contains scan_id, result_text, result_json.cgpa

### API-4: Admin Cannot Be Accessed by Student
**Request:** `GET /api/v1/users` with student JWT
**Expected:** 403 Forbidden

### API-5: Delete Own Scan
**Request:** `DELETE /api/v1/history/{scan_id}` with owner's JWT
**Expected:** 200, scan no longer appears in history

---

## Load Tests

### LT-1: 20 Concurrent Users — CSV Audit
**Setup:** 20 virtual users, ramp-up 4 users/sec, run 60 seconds
**Tasks:** CSV audit (weight 3) + history fetch (weight 1)

**Pass Criteria:**
- Failure rate = 0%
- P50 CSV audit latency < 2000ms
- P95 CSV audit latency < 5000ms
- P95 history latency < 500ms

### LT-2: Sustained 20 Users — History Only
**Setup:** 20 users, run 30 seconds, history fetch only
**Pass Criteria:**
- Failure rate = 0%
- P95 latency < 200ms

---

## Running Tests

```bash
# Install test dependencies
pip install pytest httpx locust

# Run unit tests
pytest tests/ -v

# Run load test (requires deployed backend)
locust -f tests/locustfile.py --headless -u 20 -r 4 --run-time 60s \
  --host https://nsu-audit-api.railway.app \
  --html tests/load_test_report.html
```
