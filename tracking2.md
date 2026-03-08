# Phase 2 — Progress Tracker
**NSU Audit Core | CSE226.1 | Due: March 8, 2026**
Last Updated: [update this after every session]

---

## Current Status: ⬜ NOT STARTED

---

## Part-by-Part Checklist

---

### PART 1 — Project Bootstrap & Supabase Setup
- ✅ Full folder structure created (backend/, frontend/, mobile/, cli/, tests/, .github/)
- ✅ All placeholder files created
- ✅ `tracking2.md` initialized and being maintained
- ✅ `assumptions2.md` created
- ✅ `testing_plan2.md` created
- ✅ `backend/supabase_schema.sql` written (profiles + scans tables + RLS)
- ✅ `backend/.env.example` created with all required variables
- ✅ `backend/requirements.txt` created with all dependencies
- ✅ `backend/main.py` FastAPI skeleton created
- ✅ `backend/config.py` pydantic settings created
- ✅ FastAPI starts with `uvicorn backend.main:app` — no errors
- ✅ `/health` endpoint returns `{"status": "ok", "version": "2.0"}`
- ✅ `tracking2.md` updated and presented to user
- [x] **USER CONFIRMED: GO AHEAD TO PART 2**

---

### PART 2 — Supabase Auth Middleware & Database Layer
- [x] `backend/database.py` created with all helper functions
  - [x] `get_profile(user_id)`
  - [x] `create_scan(scan_data)`
  - [x] `get_scans_by_user(user_id)`
  - [x] `get_all_scans()` (admin)
  - [x] `delete_scan(scan_id, user_id)`
- [x] `backend/auth.py` created
  - [x] `get_current_user()` dependency validates Supabase JWT
  - [x] `require_admin` dependency raises 403 for non-admin
  - [x] `CurrentUser` model with id, email, role
- [x] Supabase trigger for auto-creating profile on new Google login
- [x] Test endpoint `/api/v1/me` returns correct user info
- [x] Invalid JWT correctly returns 401
- [x] Non-admin correctly gets 403 on admin route
- [x] Real Google account tested — profile auto-created in DB
- [x] `tracking2.md` updated and presented to user
- ⬜ **USER CONFIRMED: GO AHEAD TO PART 3**

---

### PART 3 — Audit Service (Phase 1 Engine Wrapper)
- ⬜ Phase 1 scripts copied to `backend/core/`
  - ⬜ `level1_credit_tally.py`
  - ⬜ `level2_cgpa_calculator.py`
  - ⬜ `level3_audit_engine.py`
- ⬜ All `print()` calls refactored to return string (StringIO capture)
- ⬜ All `input()` prompts replaced with `waivers: list[str]` parameter
- ⬜ Each level exposes a callable function: `run_level1()`, `run_level2()`, `run_level3()`
- ⬜ Each function returns both `result_text` and `result_json`
- ⬜ `result_json` includes: student_id, program, audit_level, total_credits, cgpa, standing, eligible, missing_courses, excluded_courses, waivers_applied
- ⬜ `backend/services/audit_service.py` created
  - ⬜ `run_audit()` dispatches to correct level
  - ⬜ All 3 programs work (BSCSE, BSEEE, LLB)
  - ⬜ All 3 levels work (L1, L2, L3)
- ⬜ `backend/services/scan_service.py` created
  - ⬜ `save_scan()`
  - ⬜ `get_user_history()`
  - ⬜ `get_scan_by_id()`
  - ⬜ `delete_scan()`
- ⬜ `backend/routers/audit.py` created
  - ⬜ `POST /api/v1/audit/csv` works end-to-end
  - ⬜ Scan saved to Supabase DB after every audit
  - ⬜ Response matches PRD contract
- ⬜ Tested with all Phase 1 CSV test files — all pass
- ⬜ `tracking2.md` updated and presented to user
- ⬜ **USER CONFIRMED: GO AHEAD TO PART 4**

---

### PART 4 — OCR Service
- ⬜ `backend/services/ocr_service.py` created
  - ⬜ Image pre-processing (grayscale, contrast, deskew)
  - ⬜ EasyOCR text extraction
  - ⬜ Y-coordinate row clustering
  - ⬜ Column mapping (course_code, course_name, credits, grade, semester)
  - ⬜ Field validation (course_code regex, grade values, credit values)
  - ⬜ Confidence scoring per row
  - ⬜ Returns rows, csv_text, warnings, confidence_avg
- ⬜ `POST /api/v1/audit/ocr` endpoint created
  - ⬜ Accepts JPG, PNG, PDF (first page)
  - ⬜ Returns 422 if confidence_avg < 0.60
  - ⬜ Response includes ocr_confidence, ocr_warnings, ocr_extracted_rows
- ⬜ Test images created: `tests/ocr_samples/clean_transcript.png`
- ⬜ Test images created: `tests/ocr_samples/low_quality.jpg`
- ⬜ `tests/test_ocr.py` written and passing
  - ⬜ Clean image extracts all rows correctly
  - ⬜ Low-quality image returns confidence warnings
  - ⬜ Extracted CSV feeds into L3 audit correctly
- ⬜ `tracking2.md` updated and presented to user
- ⬜ **USER CONFIRMED: GO AHEAD TO PART 5**

---

### PART 5 — History Routes & Updated CLI
- ⬜ `backend/routers/history.py` created
  - ⬜ `GET /api/v1/history` — current user's scans, paginated
  - ⬜ `GET /api/v1/history/{scan_id}` — full scan for owner or admin
  - ⬜ `DELETE /api/v1/history/{scan_id}` — own scans only
  - ⬜ `GET /api/v1/history/user/{user_id}` — admin only
- ⬜ `backend/routers/users.py` created
  - ⬜ `GET /api/v1/users` — admin only, with scan counts
  - ⬜ `PATCH /api/v1/users/{user_id}/role` — admin only
- ⬜ All routers registered in `main.py`
- ⬜ CLI updated (`cli/audit_cli.py`)
  - ⬜ `audit-cli login` — browser Google OAuth, saves JWT
  - ⬜ `audit-cli logout` — clears saved JWT
  - ⬜ `audit-cli history` — calls API, prints table
  - ⬜ `--remote` flag — sends result to API after local audit
  - ⬜ Offline mode (Phase 1 behavior) unchanged
- ⬜ `cli/credentials.py` manages `~/.nsu_audit/credentials.json`
- ⬜ History tested: 3 audits run, all appear in history
- ⬜ Delete tested: scan removed correctly
- ⬜ Admin tested: can see all users' scans
- ⬜ `tracking2.md` updated and presented to user
- ⬜ **USER CONFIRMED: GO AHEAD TO PART 6**

---

### PART 6 — React Web App
- ⬜ Vite + React project scaffolded in `frontend/`
- ⬜ `frontend/src/lib/supabase.js` — Supabase client initialized
- ⬜ `frontend/src/lib/api.js` — all API call functions with auth headers
- ⬜ Pages built:
  - ⬜ `Login.jsx` — Google OAuth button, redirect after success
  - ⬜ `Upload.jsx` — file input, program/level dropdowns, waiver field, submit
  - ⬜ `Result.jsx` — summary card + full result text + action buttons
  - ⬜ `History.jsx` — table of past scans, view and delete
  - ⬜ `AdminPanel.jsx` — user list, scan counts, role management
- ⬜ React Router v6 routing configured
- ⬜ `AuthGuard` component redirects unauthenticated users
- ⬜ Admin panel only visible to admin role
- ⬜ `vercel.json` SPA rewrite rules added
- ⬜ Environment variables set in Vercel dashboard
- ⬜ App deployed and live on Vercel
- ⬜ End-to-end tested with real Google login
- ⬜ CSV audit tested on web
- ⬜ OCR audit tested on web
- ⬜ History page tested
- ⬜ `tracking2.md` updated and presented to user
- ⬜ **USER CONFIRMED: GO AHEAD TO PART 7**

---

### PART 7 — Flutter Mobile App
- ⬜ Flutter project created in `mobile/`
- ⬜ `pubspec.yaml` dependencies added (supabase_flutter, image_picker, http, file_picker, flutter_secure_storage)
- ⬜ Screens built:
  - ⬜ `login_screen.dart` — Google OAuth, navigate on success
  - ⬜ `upload_screen.dart` — CSV picker + camera/gallery, dropdowns, submit
  - ⬜ `result_screen.dart` — summary card + scrollable result text
  - ⬜ `history_screen.dart` — ListView, tap to view, swipe to delete
- ⬜ Services built:
  - ⬜ `auth_service.dart` — signIn, signOut, getSession, isAdmin
  - ⬜ `api_service.dart` — all API calls with auth header
- ⬜ Google login works on Android device/emulator
- ⬜ CSV upload → audit works
- ⬜ Camera photo → OCR audit works
- ⬜ History screen shows correct data
- ⬜ APK built successfully: `flutter build apk --release`
- ⬜ `tracking2.md` updated and presented to user
- ⬜ **USER CONFIRMED: GO AHEAD TO PART 8**

---

### PART 8 — CI/CD, Load Testing & Final Deployment
- ⬜ `.pre-commit-config.yaml` created (black, flake8, isort, trailing-whitespace, large-file)
- ⬜ `pre-commit install` run — hooks active
- ⬜ All existing code passes pre-commit hooks
- ⬜ `.github/workflows/ci.yml` created
  - ⬜ Runs on push to `main` and on PRs
  - ⬜ black check passes
  - ⬜ flake8 check passes
  - ⬜ isort check passes
  - ⬜ pytest passes
  - ⬜ Auto-deploy to Railway on main
  - ⬜ Auto-deploy to Vercel on main
- ⬜ `tests/locustfile.py` created
  - ⬜ CSV audit task (weight 3)
  - ⬜ History fetch task (weight 1)
- ⬜ Load test run: 20 concurrent users, 60 seconds
- ⬜ Load test results: 0% failure rate
- ⬜ P95 CSV audit latency < 5000ms ✓
- ⬜ P95 history latency < 500ms ✓
- ⬜ Load test HTML report saved: `tests/load_test_report.html`
- ⬜ `backend/Procfile` created for Railway
- ⬜ Railway environment variables set
- ⬜ Backend live on Railway
- ⬜ `README_PHASE2.md` written (setup, run, deploy, API docs, env vars)
- ⬜ Final check: all parts' tasks are ✅
- ⬜ `tracking2.md` presented to user for final sign-off
- ⬜ **USER FINAL SIGN-OFF — PHASE 2 COMPLETE**

---

## Session Log

| Session | Date | Parts Worked | What Was Done | Next Steps |
|---------|------|-------------|---------------|------------|
| 1 | Mar 7 | 1 | Project started, DB schema, FastAPI skeleton | Begin Part 2 |
| 2 | Mar 7 | 2 | Supabase Auth middleware, database.py | Begin Part 3 |
---

## Bugs / Issues

| # | Part | Layer | Description | Status | Fix Applied |
|---|------|-------|-------------|--------|-------------|
| — | — | — | No bugs yet | — | — |

---

## Open Questions

| # | Question | Raised In | Resolved? | Answer |
|---|----------|-----------|-----------|--------|
| — | — | — | — | — |
