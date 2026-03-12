# NSU Audit Core — Project Tracking

*Combined tracking from Phase 1 and Phase 2*  
*Course: CSE226.1 — Vibe Coding | Instructor: Dr. Nabeel Mohammed*

---

# PART I: Phase 1 Progress

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

---

## Phase 1 Bugs/Issues

| # | Layer | Description | Status | Fix Applied |
|---|-------|-------------|--------|-------------|
| 1 | L1 | Overlapping categories (PHY107 in both Univ Core and SEPS) | ✅ Fixed | Rewrote category assignment to allow multi-category membership |
| 2 | L3 | MAT120/MAT116 same-semester flagged as prereq violation | ℹ️ By Design | Same-semester treated as not "before" — correct behavior |

---

# PART II: Phase 2 Progress

## Current Status: ✅ PART 8 COMPLETE

---

## Part-by-Part Checklist

### PART 1 — Project Bootstrap & Supabase Setup
- ✅ Full folder structure created (backend/, frontend/, mobile/, cli/, tests/, .github/)
- ✅ All placeholder files created
- ✅ `tracking.md` created and being maintained
- ✅ `assumptions.md` created
- ✅ `testing_plan.md` created
- ✅ `backend/supabase_schema.sql` written (profiles + scans tables + RLS)
- ✅ `backend/.env.example` created with all required variables
- ✅ `backend/requirements.txt` created with all dependencies
- ✅ `backend/main.py` FastAPI skeleton created
- ✅ `backend/config.py` pydantic settings created
- ✅ FastAPI starts with `uvicorn backend.main:app` — no errors
- ✅ `/health` endpoint returns `{"status": "ok", "version": "2.0"}`

---

### PART 2 — Supabase Auth Middleware & Database Layer
- ✅ `backend/database.py` created with all helper functions
  - ✅ `get_profile(user_id)`
  - ✅ `create_scan(scan_data)`
  - ✅ `get_scans_by_user(user_id)`
  - ✅ `get_all_scans()` (admin)
  - ✅ `delete_scan(scan_id, user_id)`
- ✅ `backend/auth.py` created
  - ✅ `get_current_user()` dependency validates Supabase JWT
  - ✅ `require_admin` dependency raises 403 for non-admin
- ✅ `CurrentUser` model with id, email, role
- ✅ Supabase trigger for auto-creating profile on new Google login
- ✅ Test endpoint `/api/v1/me` returns correct user info
- ✅ Invalid JWT correctly returns 401
- ✅ Non-admin correctly gets 403 on admin route
- ✅ Real Google account tested — profile auto-created in DB

---

### PART 3 — Audit Service (Phase 1 Engine Wrapper)
- ✅ Phase 1 scripts copied to `backend/core/`
  - ✅ `level1_credit_tally.py`
  - ✅ `level2_cgpa_calculator.py`
  - ✅ `level3_audit_engine.py`
- ✅ All `print()` calls refactored to return string (StringIO capture)
- ✅ All `input()` prompts replaced with `waivers: list[str]` parameter
- ✅ Each level exposes a callable function: `run_level1()`, `run_level2()`, `run_level3()`
- ✅ Each function returns both `result_text` and `result_json`
- ✅ `result_json` includes: student_id, program, audit_level, total_credits, cgpa, standing, eligible, missing_courses, excluded_courses, waivers_applied
- ✅ `backend/services/audit_service.py` created
  - ✅ `run_audit()` dispatches to correct level
  - ✅ All 3 programs work (BSCSE, BSEEE, LLB)
  - ✅ All 3 levels work (L1, L2, L3)
- ✅ `backend/services/scan_service.py` created
  - ✅ `save_scan()`
  - ✅ `get_user_history()`
  - ✅ `get_scan_by_id()`
  - ✅ `delete_scan()`
- ✅ `backend/routers/audit.py` created
  - ✅ `POST /api/v1/audit/csv` works end-to-end
  - ✅ Scan saved to Supabase DB after every audit
  - ✅ Response matches PRD contract
- ✅ Tested with all Phase 1 CSV test files — all pass

---

### PART 4.0 — CLI Google Auth with NSU Email Restriction
- ✅ `cli/credentials.py` created
  - ✅ `save_credentials(access_token, refresh_token, email)`
  - ✅ `load_credentials()` returns dict or None
  - ✅ `delete_credentials()` removes file
  - ✅ `is_logged_in()` boolean check
  - ✅ `validate_nsu_email(email)` — enforces `@northsouth.edu` domain
- ✅ `login` command implemented in `cli/audit_cli.py`
  - ✅ Builds Supabase Google OAuth URL
  - ✅ Opens browser with `webbrowser.open()`
  - ✅ Local callback server on `localhost:54321` catches token
  - ✅ JWT email decoded without signature verification
  - ✅ Non-NSU email rejected with clear error message
  - ✅ NSU email saves credentials to `~/.nsu_audit/credentials.json`
  - ✅ Timeout after 120 seconds with error message
- ✅ `logout` command deletes credentials file, prints confirmation
- ✅ `require_login()` guard added — called at top of `cmd_l1`, `cmd_l2`, `cmd_l3`
- ✅ `build_supabase_oauth_url()` reads from `.env` via `python-dotenv`
- ✅ All manual test cases passed

---

### PART 4 — OCR Service
- ✅ `backend/services/ocr_service.py` created
  - ✅ Image pre-processing (grayscale, contrast, deskew)
  - ✅ EasyOCR text extraction
  - ✅ Y-coordinate row clustering
  - ✅ Column mapping (course_code, course_name, credits, grade, semester)
  - ✅ Field validation (course_code regex, grade values, credit values)
  - ✅ Confidence scoring per row
  - ✅ Returns rows, csv_text, warnings, confidence_avg
- ✅ `POST /api/v1/audit/ocr` endpoint created
  - ✅ Accepts JPG, PNG, PDF (first page)
  - ✅ Returns 422 if confidence_avg < 0.60
  - ✅ Response includes ocr_confidence, ocr_warnings, ocr_extracted_rows
- ✅ Test images in `tests/nsu_transcript_ocr/` used
  - ✅ Screenshot_20260309_214956.png: 16 rows, 0.96 conf
  - ✅ 681844277-Transcript.pdf: 22 rows, 0.95 conf
  - ✅ 585057865-Riyadh.pdf: 9 rows, 0.92 conf
- ✅ `tests/test_ocr.py` created
- ✅ OCR + audit pipeline tested end-to-end

---

### PART 5 — History Routes & Updated CLI
- ✅ `backend/routers/history.py` created
  - ✅ `GET /api/v1/history` — current user's scans, paginated
  - ✅ `GET /api/v1/history/{scan_id}` — full scan for owner or admin
  - ✅ `DELETE /api/v1/history/{scan_id}` — own scans only
  - ✅ `GET /api/v1/history/user/{user_id}` — admin only
- ✅ `backend/routers/users.py` created
  - ✅ `GET /api/v1/users` — admin only, with scan counts
  - ✅ `PATCH /api/v1/users/{user_id}/role` — admin only
- ✅ All routers registered in `main.py`
- ✅ CLI updated (`cli/audit_cli.py`)
  - ✅ `audit-cli login` — browser Google OAuth, saves JWT
  - ✅ `audit-cli logout` — clears saved JWT
  - ✅ `audit-cli history` — calls API, prints table
  - ✅ `--remote` flag — sends result to API after local audit
  - ✅ Offline mode (Phase 1 behavior) unchanged
- ✅ `cli/credentials.py` manages `~/.nsu_audit/credentials.json`
- ✅ `POST /api/v1/audit/save` endpoint added for CLI remote saves

---

### PART 6 — React Web App
- ✅ Vite + React project scaffolded in `frontend/`
- ✅ `frontend/src/lib/supabase.js` — Supabase client initialized
- ✅ `frontend/src/lib/api.js` — all API call functions with auth headers
- ✅ Pages built:
  - ✅ `Login.jsx` — Google OAuth button, redirect after success
  - ✅ `Upload.jsx` — file input, program/level dropdowns, waiver field, submit
  - ✅ `Result.jsx` — summary card + full result text + action buttons
  - ✅ `History.jsx` — table of past scans, view and delete
  - ✅ `AdminPanel.jsx` — user list, scan counts, role management
- ✅ React Router v6 routing configured
- ✅ `AuthGuard` component redirects unauthenticated users
- ✅ Admin panel only visible to admin role
- ✅ `vercel.json` SPA rewrite rules added
- ✅ `frontend/.env.example` created with environment variables template
- ✅ Frontend builds successfully (npm run build)

---

### PART 7 — Flutter Mobile App
- ✅ Flutter project created via `flutter create mobile --org com.nsu`
- ✅ `pubspec.yaml` dependencies added
- ✅ Screens built:
  - ✅ `login_screen.dart` — Google OAuth, navigate on success
  - ✅ `upload_screen.dart` — CSV picker + camera/gallery, dropdowns, submit
  - ✅ `result_screen.dart` — summary card + scrollable result text
  - ✅ `history_screen.dart` — ListView, tap to view, swipe to delete
- ✅ Services built:
  - ✅ `auth_service.dart` — signIn, signOut, getSession, isAdmin
  - ✅ `api_service.dart` — all API calls with auth header
- ✅ `main.dart` created with navigation flow
- ✅ Supabase credentials added (URL + anon key)
- ⬜ APK BUILD: Run locally with Android SDK installed

---

### PART 8 — CI/CD, Load Testing & Final Deployment
- ✅ `.pre-commit-config.yaml` created (black, flake8, isort, trailing-whitespace, large-file)
- ✅ `.github/workflows/ci.yml` created
  - ✅ Runs on push to `master` and on PRs
  - ✅ black check
  - ✅ flake8 check
  - ✅ isort check
  - ✅ pytest
  - ✅ Auto-deploy to Railway on master (requires RAILWAY_TOKEN)
  - ✅ Auto-deploy to Vercel on master (requires VERCEL_TOKEN)
- ✅ `tests/locustfile.py` created
  - ✅ CSV audit task (weight 3)
  - ✅ History fetch task (weight 1)
- ⬜ Load test run: 20 concurrent users, 60 seconds (requires deployed backend)
- ⬜ Load test results: 0% failure rate
- ✅ `backend/Procfile` created for Railway
- ⬜ Railway environment variables set (user must configure)
- ⬜ Backend live on Railway (user must deploy)
- ✅ `README.md` written (setup, run, deploy, API docs, env vars)
- ⬜ **AWAITING DEPLOYMENT & FINAL SIGN-OFF**

---

## Session Log

| Session | Date | Parts Worked | What Was Done |
|---------|------|-------------|---------------|
| 1 | Mar 7 | 1 | Project started, DB schema, FastAPI skeleton |
| 2 | Mar 7 | 2 | Supabase Auth middleware, database.py |
| 3 | Mar 8 | 3 | Audit service wrapping Phase 1, CSV endpoint |
| 4 | Mar 9 | 4.0 | CLI Google Auth with NSU email restriction |
| 5 | Mar 9 | 4 | OCR service implemented, tested with real transcripts |
| 6 | Mar 10 | 5 | History routes & users routers created, CLI updated |
| 7 | Mar 10 | 6 | React web app scaffolded, all pages built |
| 8 | Mar 11 | 7 | Flutter mobile app created - all screens and services |
| 9 | Mar 12 | 7-8 | Added Supabase credentials, CI/CD, project cleanup |
| 10 | Mar 12 | 8 | Consolidated docs/, organized project structure |

---

## Remaining Tasks

1. Deploy backend to Railway
2. Deploy frontend to Vercel
3. Run load test (20 concurrent users)
4. Build Flutter APK locally
5. Final sign-off
