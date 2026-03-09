# Testing Plan — Phase 2
**NSU Audit Core | CSE226.1**
Created before any code is written.

---

## What "Testing" Means for Phase 2

Phase 2 testing covers four layers:

1. **Unit tests** — individual service functions (audit, OCR, DB helpers) tested in isolation
2. **API integration tests** — full HTTP request/response cycle tested with `pytest` + `httpx`
3. **OCR tests** — image extraction accuracy tests with sample transcript images
4. **Load tests** — 20 concurrent users simulated with Locust

All tests live in `tests/`. All must pass before deployment.

---

## Test Files

```
tests/
├── test_audit_service.py     # Unit tests for audit service wrapper
├── test_ocr.py               # OCR extraction tests
├── test_api.py               # API integration tests (auth, CSV audit, history)
├── test_history.py           # History routes tests
├── test_users.py             # Admin user management tests
├── locustfile.py             # Load test (20 concurrent users)
└── ocr_samples/
    ├── clean_transcript.png  # Clean, well-formatted transcript image
    └── low_quality.jpg       # Blurry/skewed image for confidence testing
```

---

## Part 3 — Audit Service Unit Tests (`test_audit_service.py`)

### Test Case AS-1: Level 1 — Valid CSV, BSCSE
**Input:** `data/test_L1_cse_standard.csv`, program=BSCSE, level=1, waivers=[]
**Expected:** `result_json.total_credits` matches Phase 1 Level 1 output
**Status:** ✅ Passed

### Test Case AS-2: Level 2 — CGPA with Waivers, BSCSE
**Input:** `data/test_L2_cse_waivers.csv`, program=BSCSE, level=2, waivers=['ENG102', 'MAT116']
**Expected:** CGPA calculation matches Phase 1 Level 2 output; waivers excluded
**Status:** ✅ Passed

### Test Case AS-3: Level 3 — Full Audit, Graduation Eligible, BSCSE
**Input:** `data/test_L3_cse_eligible.csv`, program=BSCSE, level=3, waivers=[]
**Expected:** `result_json.eligible = true`, 0 missing courses
**Status:** ✅ Passed

### Test Case AS-4: Level 3 — Full Audit, Not Eligible, Missing Capstone
**Input:** `data/test_L3_cse_missing_capstone.csv`, program=BSCSE, level=3, waivers=[]
**Expected:** `result_json.eligible = false`, CSE499B in missing_courses
**Status:** ⬜ Not Run

### Test Case AS-5: Level 3 — LLB Program, Missing Core Year 4
**Input:** `data/test_L3_law_missing_core.csv`, program=LLB, level=3, waivers=['ENG102']
**Expected:** `result_json.eligible = false`, year 4 courses in missing_courses
**Status:** ✅ Passed

### Test Case AS-6: Level 3 — Retake Scenario, Passed After Fail
**Input:** `data/test_L3_retake.csv`, program=BSCSE, level=3, waivers=[]
**Expected:** Failed-then-passed course clears the requirement
**Status:** ✅ Passed

### Test Case AS-7: Level 1 — Invalid Grades Excluded
**Input:** CSV with F, W, I, X grades, program=BSCSE, level=1
**Expected:** Invalid grade rows excluded from credit total; `excluded_courses` populated
**Status:** ⬜ Not Run

### Test Case AS-8: Level 2 — Probation Flag
**Input:** CSV with CGPA < 2.0, program=BSCSE, level=2
**Expected:** `result_json.standing = "PROBATION"`, `result_json.eligible = false`
**Status:** ⬜ Not Run

---

## Part 4.0 — CLI Auth Tests (`test_cli_auth.py`)

### Test Case AUTH-1: Login with NSU Email — Success
**Command:** `python cli/audit_cli.py login` → authenticate with `<name>@northsouth.edu`
**Expected:** `✅ Logged in as <name>@northsouth.edu`; `~/.nsu_audit/credentials.json` created; `email` field in file ends with `@northsouth.edu`
**Status:** ⬜ Not Run (requires real Supabase OAuth)

### Test Case AUTH-2: Login with Non-NSU Gmail — Rejected
**Command:** `python cli/audit_cli.py login` → authenticate with any `@gmail.com` account
**Expected:** `❌ Login failed: only @northsouth.edu accounts are permitted.`; no credentials file written
**Status:** ✅ Tested via `validate_nsu_email()` unit test

### Test Case AUTH-3: Audit Command Without Login — Blocked
**Command:** `python cli/audit_cli.py l1 data/test_L1_cse_standard.csv BSCSE` (no prior login)
**Expected:** `❌ You must be logged in to run audits.` printed; process exits with code 1; no audit output
**Status:** ✅ Passed

### Test Case AUTH-4: Audit Command After Valid Login — Succeeds
**Command:** After AUTH-1 login, run `python cli/audit_cli.py l1 data/test_L1_cse_standard.csv BSCSE`
**Expected:** Audit runs normally; output matches Phase 1 Level 1 output
**Status:** ✅ Passed (tested with manual credentials)

### Test Case AUTH-5: Logout — Credentials Deleted
**Command:** `python cli/audit_cli.py logout`
**Expected:** `Logged out.` printed; `~/.nsu_audit/credentials.json` no longer exists
**Status:** ✅ Passed

### Test Case AUTH-6: Audit Command After Logout — Blocked
**Command:** After AUTH-5 logout, run `python cli/audit_cli.py l3 data/test_L3_cse_eligible.csv BSCSE`
**Expected:** `❌ You must be logged in to run audits.`; exits with code 1
**Status:** ⬜ Not Run

---

## Part 4 — OCR Tests (`test_ocr.py`)

### Test Case OCR-1: Clean Transcript Image — All Rows Extracted
**Input:** `tests/ocr_samples/clean_transcript.png`
**Expected:** All rows extracted with confidence ≥ 0.85; course_codes match expected values; no warnings
**Status:** ⬜ Not Run

### Test Case OCR-2: Low Quality Image — Confidence Warnings Returned
**Input:** `tests/ocr_samples/low_quality.jpg`
**Expected:** At least one row with confidence < 0.70 flagged in `warnings`; overall confidence_avg < 0.70
**Status:** ⬜ Not Run

### Test Case OCR-3: OCR Output → Audit Engine
**Input:** `tests/ocr_samples/clean_transcript.png`, program=BSCSE, level=3
**Expected:** Extracted CSV feeds into audit engine without error; result matches expected output
**Status:** ⬜ Not Run

### Test Case OCR-4: Very Low Confidence → 422 Response
**Input:** Blank or near-blank image
**Expected:** API returns HTTP 422 with message explaining low confidence
**Status:** ⬜ Not Run

### Test Case OCR-5: Course Code Validation
**Input:** Image where one row has an invalid course code pattern
**Expected:** Invalid row flagged in warnings; valid rows still processed
**Status:** ⬜ Not Run

---

## Part 3+5 — API Integration Tests (`test_api.py`)

### Test Case API-1: Health Check — No Auth
**Request:** `GET /health`
**Expected:** 200, `{"status": "ok", "version": "2.0"}`
**Status:** ⬜ Not Run

### Test Case API-2: Protected Route — No Token
**Request:** `GET /api/v1/history` (no Authorization header)
**Expected:** 401 Unauthorized
**Status:** ⬜ Not Run

### Test Case API-3: Protected Route — Invalid Token
**Request:** `GET /api/v1/history`, Authorization: `Bearer bad_token`
**Expected:** 401 Unauthorized
**Status:** ⬜ Not Run

### Test Case API-4: CSV Audit — Valid Request
**Request:** `POST /api/v1/audit/csv` with valid JWT + BSCSE CSV + level=3
**Expected:** 200, response contains scan_id, result_text, result_json.cgpa
**Status:** ⬜ Not Run

### Test Case API-5: CSV Audit — Missing Program Field
**Request:** `POST /api/v1/audit/csv` with valid JWT + CSV, no program field
**Expected:** 422 Unprocessable Entity with validation error
**Status:** ✅ Passed

### Test Case API-6: CSV Audit — Scan Saved to DB
**Request:** `POST /api/v1/audit/csv`, then `GET /api/v1/history`
**Expected:** History list contains the new scan_id from the audit
**Status:** ⬜ Not Run

### Test Case API-7: OCR Audit — Valid Image
**Request:** `POST /api/v1/audit/ocr` with valid JWT + PNG image + BSCSE + level=3
**Expected:** 200, response contains ocr_confidence, ocr_extracted_rows, result_text
**Status:** ⬜ Not Run

### Test Case API-8: Admin Cannot Be Accessed by Student
**Request:** `GET /api/v1/users` with student JWT
**Expected:** 403 Forbidden
**Status:** ⬜ Not Run

### Test Case API-9: Admin Can Access All Scans
**Request:** `GET /api/v1/history/user/{another_user_id}` with admin JWT
**Expected:** 200, returns that user's scan history
**Status:** ⬜ Not Run

### Test Case API-10: Delete Own Scan
**Request:** `DELETE /api/v1/history/{scan_id}` with owner's JWT
**Expected:** 200, scan no longer appears in history
**Status:** ⬜ Not Run

### Test Case API-11: Delete Someone Else's Scan (Student)
**Request:** `DELETE /api/v1/history/{other_users_scan_id}` with student JWT
**Expected:** 403 Forbidden
**Status:** ⬜ Not Run

### Test Case API-12: Role Change by Admin
**Request:** `PATCH /api/v1/users/{user_id}/role` with admin JWT, body: `{"role": "admin"}`
**Expected:** 200, user's role changed in DB
**Status:** ⬜ Not Run

---

## Part 8 — Load Tests (`locustfile.py`)

### Load Test LT-1: 20 Concurrent Users — CSV Audit
**Setup:** 20 virtual users, ramp-up 4 users/sec, run 60 seconds
**Tasks:** CSV audit (weight 3) + history fetch (weight 1)
**Pass Criteria:**
- Failure rate = 0%
- P50 CSV audit latency < 2000ms
- P95 CSV audit latency < 5000ms
- P95 history latency < 500ms
**Status:** ⬜ Not Run

### Load Test LT-2: Sustained 20 Users — History Only
**Setup:** 20 users, run 30 seconds, history fetch only
**Pass Criteria:**
- Failure rate = 0%
- P95 latency < 200ms
**Status:** ⬜ Not Run

---

## Test Results Log

Update this table as tests are completed.

| Test ID | Part | Date Run | Result | Notes |
|---------|------|----------|--------|-------|
| AS-1 | 3 | 2026-03-08 | ✅ | Passed via Part 3 manual script run |
| AS-2 | 3 | 2026-03-08 | ✅ | Passed via Part 3 manual script run |
| AS-3 | 3 | 2026-03-08 | ✅ | Passed via Part 3 manual script run |
| AS-4 | 3 | — | ⬜ | — |
| AS-5 | 3 | 2026-03-08 | ✅ | Passed via Part 3 manual script run |
| AS-6 | 3 | 2026-03-08 | ✅ | Passed via Part 3 manual script run |
| AS-7 | 3 | — | ⬜ | — |
| AS-8 | 3 | — | ⬜ | — |
| AUTH-1 | 4.0 | — | ⬜ | Requires real Supabase OAuth |
| AUTH-2 | 4.0 | 2026-03-09 | ✅ | Tested via validate_nsu_email() unit test |
| AUTH-3 | 4.0 | 2026-03-09 | ✅ | Passed |
| AUTH-4 | 4.0 | 2026-03-09 | ✅ | Passed with manual credentials |
| AUTH-5 | 4.0 | 2026-03-09 | ✅ | Passed |
| AUTH-6 | 4.0 | 2026-03-09 | ✅ | Passed |
| OCR-1 | 4 | — | ⬜ | — |
| OCR-2 | 4 | — | ⬜ | — |
| OCR-3 | 4 | — | ⬜ | — |
| OCR-4 | 4 | — | ⬜ | — |
| OCR-5 | 4 | — | ⬜ | — |
| API-1 | 3 | — | ⬜ | — |
| API-2 | 2 | — | ⬜ | — |
| API-3 | 2 | — | ⬜ | — |
| API-4 | 3 | — | ⬜ | — |
| API-5 | 3 | 2026-03-08 | ✅ | Passed via Part 3 manual script run |
| API-6 | 3 | — | ⬜ | — |
| API-7 | 4 | — | ⬜ | — |
| API-8 | 2 | — | ⬜ | — |
| API-9 | 5 | — | ⬜ | — |
| API-10 | 5 | — | ⬜ | — |
| API-11 | 5 | — | ⬜ | — |
| API-12 | 5 | — | ⬜ | — |
| LT-1 | 8 | — | ⬜ | — |
| LT-2 | 8 | — | ⬜ | — |
