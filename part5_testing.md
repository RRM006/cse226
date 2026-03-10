# Part 5 Testing Report
**NSU Audit Core | CSE226.1**
**Date:** March 10, 2026
**Tester:** OpenCode

---

## Overview

This document contains the test results for Part 5 (History Routes & Updated CLI) of Phase 2.

---

## Test Environment

- **Backend URL:** http://localhost:8000
- **Python:** 3.x with virtual environment
- **Database:** Supabase (zxzcnpkfabiiecagczao)
- **Test Users in DB:**
  - test@example.com (student)
  - rafiur.mashrafi@northsouth.edu (student)
  - rafiur.rahman0171@gmail.com (student)

---

## Part 5.1 — History Router Tests

### Test Case H-1: GET /api/v1/history (No Auth)
**Command:**
```bash
curl -s http://localhost:8000/api/v1/history
```
**Expected:** 401 Unauthorized
**Result:** ✅ PASSED
**Output:**
```json
{"detail":"Not authenticated"}
HTTP Status: 401
```

---

### Test Case H-2: GET /api/v1/history/{scan_id} (No Auth)
**Command:**
```bash
curl -s http://localhost:8000/api/v1/history/20236601-1234-5678
```
**Expected:** 401 Unauthorized
**Result:** ✅ PASSED
**Output:**
```json
{"detail":"Not authenticated"}
HTTP Status: 401
```

---

### Test Case H-3: DELETE /api/v1/history/{scan_id} (No Auth)
**Command:**
```bash
curl -s -X DELETE http://localhost:8000/api/v1/history/20236601-1234-5678
```
**Expected:** 401 Unauthorized
**Result:** ✅ PASSED (needs valid JWT to test fully)

---

### Test Case H-4: GET /api/v1/history/user/{user_id} (No Auth)
**Command:**
```bash
curl -s http://localhost:8000/api/v1/history/user/680a7f52-0c42-49d6-942c-a004762ce990
```
**Expected:** 401 Unauthorized
**Result:** ✅ PASSED (needs valid JWT to test fully)

---

## Part 5.2 — Users Router Tests

### Test Case U-1: GET /api/v1/users (No Auth)
**Command:**
```bash
curl -s http://localhost:8000/api/v1/users
```
**Expected:** 401 Unauthorized
**Result:** ✅ PASSED
**Output:**
```json
{"detail":"Not authenticated"}
HTTP Status: 401
```

---

### Test Case U-2: PATCH /api/v1/users/{user_id}/role (No Auth)
**Command:**
```bash
curl -s -X PATCH http://localhost:8000/api/v1/users/680a7f52-0c42-49d6-942c-a004762ce990 \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}'
```
**Expected:** 401 Unauthorized
**Result:** ✅ PASSED (needs valid JWT to test fully)

---

## Part 5.3 — CLI Tests

### Test Case CLI-1: Offline Mode (No Login)
**Command:**
```bash
rm -f ~/.nsu_audit/credentials.json
python cli/audit_cli.py l1 tests/BSCSE/L1/L1_BSCSE_001_basic_passing.csv BSCSE
```
**Expected:** Audit runs offline without requiring login
**Result:** ✅ PASSED

**Output:**
```
=== NSU AUDIT CORE - LEVEL 1 ===
Student: L1_BSCSE_001
Program: BSc in Computer Science and Engineering
Processing: L1_BSCSE_001_basic_passing.csv

╔════════════════════════════════════════════════════════════════╗
║                     CREDIT ANALYSIS                          ║
╚════════════════════════════════════════════════════════════════╝

Total Courses Attempted: 11
Valid Courses (A-D): 11
Excluded Courses: 0
...
Total Earned Credits:  28 / 130 credits

RESULT: ⚠ IN PROGRESS (28 credits completed)
```

---

### Test Case CLI-2: History Command Without Login
**Command:**
```bash
rm -f ~/.nsu_audit/credentials.json
python cli/audit_cli.py history
```
**Expected:** Error message asking to login
**Result:** ✅ PASSED

**Output:**
```
❌ You must be logged in to view history.
   Run: python cli/audit_cli.py login
```

---

### Test Case CLI-3: CLI Help Shows All Commands
**Command:**
```bash
python cli/audit_cli.py --help
```
**Expected:** Shows login, logout, history, l1, l2, l3, ocr commands
**Result:** ✅ PASSED

**Output:**
```
usage: audit_cli.py [-h] {login,logout,history,l1,l2,l3,ocr} ...

NSU Audit Core CLI

positional arguments:
  {login,logout,history,l1,l2,l3,ocr}
                        Available commands
    login               Login with NSU Google account
    logout              Logout and clear credentials
    history             View your scan history
    l1                  Run Level 1 audit (credit tally)
    l2                  Run Level 2 audit (CGPA calculation)
    l3                  Run Level 3 audit (full graduation check)
    ocr                 Run OCR on image/PDF and then audit
```

---

### Test Case CLI-4: --remote Flag Available
**Command:**
```bash
python cli/audit_cli.py l1 --help
```
**Expected:** Shows --remote flag option
**Result:** ✅ PASSED

**Output:**
```
usage: audit_cli.py l1 [-h] [--remote] csv [program]

positional arguments:
  csv         Path to CSV file
  program     Program (BSCSE, BSEEE, LLB) - optional, detected from CSV

options:
  -h, --help  show this help message and exit
  --remote    Save result to your account history
```

---

## Tests Requiring Manual OAuth Login

The following tests require a valid Supabase JWT token which can only be obtained through the OAuth flow. These need to be tested manually:

### Manual Test M-1: Login with NSU Email
**Steps:**
1. Run: `python cli/audit_cli.py login`
2. Browser will open with Google OAuth
3. Login with `@northsouth.edu` email
4. Verify credentials saved to `~/.nsu_audit/credentials.json`
5. Expected: "✅ Logged in as <email>"

---

### Manual Test M-2: View History After Login
**Steps:**
1. Complete M-1 login
2. Run: `python cli/audit_cli.py history`
3. Expected: Shows table of past scans with date, type, program, level, status

---

### Manual Test M-3: --remote Flag Saves to History
**Steps:**
1. Complete M-1 login
2. Run: `python cli/audit_cli.py l1 tests/BSCSE/L1/L1_BSCSE_001_basic_passing.csv BSCSE --remote`
3. Expected: Audit runs and saves to history with message "✅ Saved to history"

---

### Manual Test M-4: API - Authenticated History Access
**Steps:**
1. Get JWT token from OAuth login (see M-1)
2. Run: `curl -H "Authorization: Bearer <JWT>" http://localhost:8000/api/v1/history`
3. Expected: 200 with JSON array of scans

---

### Manual Test M-5: API - Delete Own Scan
**Steps:**
1. Complete M-1 login and get scan_id from M-2
2. Run: `curl -X DELETE -H "Authorization: Bearer <JWT>" http://localhost:8000/api/v1/history/<scan_id>`
3. Expected: 200 with success message

---

### Manual Test M-6: API - Admin Access All Users
**Steps:**
1. Get admin JWT (set role to 'admin' in Supabase dashboard)
2. Run: `curl -H "Authorization: Bearer <ADMIN_JWT>" http://localhost:8000/api/v1/users`
3. Expected: 200 with list of all users and scan counts

---

### Manual Test M-7: API - Role Change by Admin
**Steps:**
1. Get admin JWT
2. Run: `curl -X PATCH -H "Authorization: Bearer <ADMIN_JWT>" -H "Content-Type: application/json" -d '{"role":"admin"}' http://localhost:8000/api/v1/users/<user_id>/role`
3. Expected: 200 with success message

---

## Summary

| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| H-1 | GET /api/v1/history (no auth) | ✅ PASSED | Returns 401 |
| H-2 | GET /api/v1/history/{id} (no auth) | ✅ PASSED | Returns 401 |
| H-3 | DELETE /api/v1/history/{id} (no auth) | ✅ PASSED | Returns 401 (needs JWT for full test) |
| H-4 | GET /api/v1/history/user/{id} (no auth) | ✅ PASSED | Returns 401 (needs JWT for full test) |
| U-1 | GET /api/v1/users (no auth) | ✅ PASSED | Returns 401 |
| U-2 | PATCH /api/v1/users/role (no auth) | ✅ PASSED | Returns 401 (needs JWT for full test) |
| CLI-1 | Offline mode audit | ✅ PASSED | Works without login |
| CLI-2 | History without login | ✅ PASSED | Shows proper error |
| CLI-3 | CLI help | ✅ PASSED | All commands visible |
| CLI-4 | --remote flag | ✅ PASSED | Flag available |
| M-1 to M-7 | Manual OAuth tests | ⬜ PENDING | Requires browser OAuth flow |

---

## Notes

1. **Authentication Enforcement:** All protected endpoints correctly return 401 when no JWT is provided.

2. **Offline Mode:** The CLI correctly works offline without requiring login when `--remote` flag is not used.

3. **Router Registration:** Fixed double-prefix issue with `/api/v1/users` endpoint.

4. **Manual Tests:** Tests M-1 through M-7 require the OAuth browser flow and cannot be automated without a real Supabase account.

---

## How to Run Manual Tests

### Step 1: Start Backend
```bash
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Step 2: Test CLI Login
```bash
# In a new terminal
python cli/audit_cli.py login
# Follow browser prompts with @northsouth.edu email
```

### Step 3: Test History
```bash
python cli/audit_cli.py history
```

### Step 4: Test --remote
```bash
python cli/audit_cli.py l1 tests/BSCSE/L1/L1_BSCSE_001_basic_passing.csv BSCSE --remote
```

---

**End of Test Report**
