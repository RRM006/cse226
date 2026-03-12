# Phase 2 — Progress Tracker
**NSU Audit Core | CSE226.1 | Due: March 8, 2026**
Last Updated: March 10, 2026

---

## Current Status: ✅ PART 6 COMPLETE — Ready for Part 7

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
- ✅ **USER CONFIRMED: GO AHEAD TO PART 2**

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
- ✅ `tracking2.md` updated and presented to user
- ✅ **USER CONFIRMED: GO AHEAD TO PART 3**

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
- ✅ `tracking2.md` updated and presented to user
- ✅ **USER CONFIRMED: GO AHEAD TO PART 4**

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
- ✅ `decode_jwt_email()` helper implemented
- ✅ All 6 manual test cases passed (see Part 4.0 Step 4.0.9)
- ✅ `tracking2.md` updated and presented to user
- ✅ **USER CONFIRMED: GO AHEAD TO PART 4**

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
- ✅ `part4_testing.md` created with manual test steps
- ✅ `testing_plan2.md` updated with test results
- ✅ **USER CONFIRMED: GO AHEAD TO PART 5**

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
- ✅ CLI help verified: all commands visible
- ✅ **USER CONFIRMED: GO AHEAD TO PART 6**

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
- ✅ **USER CONFIRMED: GO AHEAD TO PART 7**

---

### PART 7 — Flutter Mobile App
- ✅ Flutter project created via `flutter create mobile --org com.nsu`
- ✅ `pubspec.yaml` dependencies added (supabase_flutter, image_picker, http, file_picker, flutter_secure_storage, go_router)
- ✅ `flutter pub get` completed successfully
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
- ✅ **APK BUILD: Run locally with Android SDK installed:**
  ```bash
  cd mobile
  flutter build apk --release
  ```

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
- ⬜ Final check: all parts' tasks are done or not done
- ⬜ `tracking2.md` presented to user for final sign-off
- ⬜ **USER FINAL SIGN-OFF — PHASE 2 COMPLETE**

---

## Session Log

| Session | Date | Parts Worked | What Was Done | Next Steps |
|---------|------|-------------|---------------|------------|
| 1 | Mar 7 | 1 | Project started, DB schema, FastAPI skeleton | Begin Part 2 |
| 2 | Mar 7 | 2 | Supabase Auth middleware, database.py | Begin Part 3 |
| 3 | Mar 8 | 3 | Audit service wrapping Phase 1, CSV endpoint | Begin Part 4 |
| 4 | Mar 9 | 4.0 | CLI Google Auth with NSU email restriction | Begin Part 4 (OCR) |
| 5 | Mar 9 | 4 | OCR service implemented, tested with real transcripts | Begin Part 5 |
| 6 | Mar 10 | 5 | History routes & users routers created, CLI updated with history & --remote | Begin Part 6 |
| 7 | Mar 10 | 6 | React web app scaffolded, all pages built, routing configured | Begin Part 7 |
| 8 | Mar 11 | 7 | Flutter mobile app created - all screens and services built, waiting for Flutter SDK | Continue Part 7 |
| 9 | Mar 12 | 7 | Added Supabase credentials to auth_service.dart, code complete, Android SDK unavailable for APK build | Build APK locally |
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
