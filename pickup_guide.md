# NSU Audit Core Phase 2 — Pickup Guide
**Last Updated:** March 12, 2026

---

## Current State

### Fully Complete Parts (1-6)
- **Part 1:** Project Bootstrap & Supabase Setup - COMPLETE
- **Part 2:** Supabase Auth Middleware & Database Layer - COMPLETE
- **Part 3:** Audit Service (Phase 1 Engine Wrapper) - COMPLETE
- **Part 4.0:** CLI Google Auth with NSU Email Restriction - COMPLETE
- **Part 4:** OCR Service - COMPLETE
- **Part 5:** History Routes & Updated CLI - COMPLETE
- **Part 6:** React Web App - COMPLETE

### Part 7 - Flutter Mobile App (Code Complete, APK Pending)
- All Flutter screens created: login, upload, result, history
- All services created: auth_service, api_service
- Supabase credentials added
- APK build requires local Android SDK (not available in current environment)

### Part 8 - CI/CD, Load Testing & Final Deployment - NOT STARTED
- .pre-commit-config.yaml - not created
- .github/workflows/ci.yml - not created
- Locust load testing - not done
- README_PHASE2.md - not written

---

## What Was Just Done

### Session: March 12, 2026

**Files Modified:**
1. `mobile/lib/services/auth_service.dart`
   - Added real Supabase URL: `https://zxzcnpkfabiiecagczao.supabase.co`
   - Added real Supabase anon key: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4emNucGtmYWJpaWVjYWdjemFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI4MDExNDMsImV4cCI6MjA4ODM3NzE0M30.0Qo8IT6gBIOF3YMlHZm4dnh47lMUW5QesD_f3EVf9tM`
   - Fixed return type: changed `Future<AuthResponse> signInWithGoogle()` to `Future<bool> signInWithGoogle()`

**Decisions Made:**
- Android SDK is not available in the current environment (tried /opt/android-sdk, /usr/lib/android-sdk - neither exists)
- APK build must be done locally by the user
- Flutter SDK was successfully cloned and built (version 3.41.4 with Dart 3.11.1)

**Files Created Previously (from earlier sessions):**
- `backend/main.py` - FastAPI app entry point
- `backend/config.py` - Pydantic settings
- `backend/auth.py` - Supabase JWT validation middleware
- `backend/database.py` - DB helpers (get_profile, create_scan, get_scans_by_user, etc.)
- `backend/routers/audit.py` - /api/v1/audit/* routes
- `backend/routers/history.py` - /api/v1/history/* routes
- `backend/routers/users.py` - /api/v1/users/* routes
- `backend/services/audit_service.py` - Wraps Phase 1 engine
- `backend/services/ocr_service.py` - EasyOCR pipeline
- `backend/services/scan_service.py` - Save/retrieve scans
- `backend/core/` - Phase 1 audit engine (level1, level2, level3)
- `backend/supabase_schema.sql` - DB schema with RLS
- `backend/requirements.txt` - All Python dependencies
- `cli/audit_cli.py` - Updated CLI with login, logout, history, --remote
- `cli/credentials.py` - Token management
- `frontend/` - React + Vite web app with all pages
- `mobile/` - Flutter app (all screens and services)

**Assumptions Logged (in assumptions2.md):**
- Assumption #1-26 covering all technical decisions
- Key ones: EasyOCR for OCR, Supabase for Auth/DB, Railway for hosting, Vercel for frontend

---

## Exact Next Step

### Primary Task: Complete Part 8 - CI/CD, Load Testing & Final Deployment

**Steps to do:**
1. Create `.pre-commit-config.yaml` with black, flake8, isort, trailing-whitespace, large-file hooks
2. Create `.github/workflows/ci.yml` with:
   - Run on push to main and PRs
   - black --check
   - flake8 check
   - isort check
   - pytest tests/
   - Auto-deploy to Railway on main
   - Auto-deploy to Vercel on main
3. Create `tests/locustfile.py` for 20 concurrent user load testing
4. Run load test and verify: 0% failure rate, P95 CSV < 5s, P95 history < 500ms
5. Create `backend/Procfile` for Railway
6. Write `README_PHASE2.md` with setup and deployment instructions

**File to open first:** Check if `.pre-commit-config.yaml` exists
```bash
ls -la .pre-commit-config.yaml
```

---

## Open Items

### Bugs/Issues
1. **Android SDK unavailable** - Cannot build APK in current environment
   - User must build APK locally with Android Studio or Android SDK installed
   - Command: `cd mobile && flutter build apk --release`

2. **Flutter redirect URI** - May need to configure in Supabase dashboard:
   - Redirect URL: `nsu-audit-mobile://login-callback`
   - This must be added to Supabase Authentication > URL Configuration > Redirect URLs

### Questions
1. Should Part 8 start now or wait for APK build confirmation?
2. Are there any specific Railway/Vercel credentials to use?

### Skipped/Deferred
1. APK build - requires local environment with Android SDK
2. Load testing - requires deployed backend
3. CI/CD pipeline - requires Part 8 to be started

---

## Key Files Reference

### Backend (FastAPI)
| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app entry, all routers registered |
| `backend/config.py` | Pydantic settings from environment |
| `backend/auth.py` | Supabase JWT validation middleware |
| `backend/database.py` | Supabase client + DB helper functions |
| `backend/routers/audit.py` | POST /api/v1/audit/csv, /api/v1/audit/ocr |
| `backend/routers/history.py` | GET/DELETE /api/v1/history/* |
| `backend/routers/users.py` | GET /api/v1/users, PATCH /users/{id}/role |
| `backend/services/audit_service.py` | Wraps Phase 1 engine, run_audit() |
| `backend/services/ocr_service.py` | EasyOCR pipeline with row parsing |
| `backend/services/scan_service.py` | save_scan, get_user_history, delete_scan |
| `backend/core/level1_credit_tally.py` | Phase 1 Level 1 logic |
| `backend/core/level2_cgpa_calculator.py` | Phase 1 Level 2 logic |
| `backend/core/level3_audit_engine.py` | Phase 1 Level 3 logic |
| `backend/supabase_schema.sql` | profiles + scans tables + RLS policies |
| `backend/requirements.txt` | All Python dependencies |
| `backend/Procfile` | Railway web: uvicorn main:app |

### Frontend (React)
| File | Purpose |
|------|---------|
| `frontend/src/App.jsx` | Main React app with routing |
| `frontend/src/pages/Login.jsx` | Google OAuth login |
| `frontend/src/pages/Upload.jsx` | CSV/image upload form |
| `frontend/src/pages/Result.jsx` | Audit result display |
| `frontend/src/pages/History.jsx` | Scan history list |
| `frontend/src/pages/AdminPanel.jsx` | Admin user/scan management |
| `frontend/src/lib/supabase.js` | Supabase client |
| `frontend/src/lib/api.js` | API call helpers |
| `frontend/vercel.json` | SPA rewrite rules |

### Mobile (Flutter)
| File | Purpose |
|------|---------|
| `mobile/lib/main.dart` | App entry with AuthWrapper |
| `mobile/lib/services/auth_service.dart` | Supabase auth (credentials added) |
| `mobile/lib/services/api_service.dart` | API calls to backend |
| `mobile/lib/screens/login_screen.dart` | Google OAuth login UI |
| `mobile/lib/screens/upload_screen.dart` | CSV picker + camera/gallery |
| `mobile/lib/screens/result_screen.dart` | Summary card + result text |
| `mobile/lib/screens/history_screen.dart` | ListView with delete |
| `mobile/pubspec.yaml` | Flutter dependencies |

### CLI
| File | Purpose |
|------|---------|
| `cli/audit_cli.py` | Main CLI with l1/l2/l3/ocr/login/logout/history commands |
| `cli/credentials.py` | Token storage in ~/.nsu_audit/credentials.json |

### Tests
| File | Purpose |
|------|---------|
| `tests/test_audit_service.py` | Unit tests for audit service |
| `tests/test_ocr.py` | OCR extraction tests |
| `tests/test_api.py` | API integration tests |
| `tests/locustfile.py` | Load test (NOT YET CREATED) |

### Configuration
| File | Purpose |
|------|---------|
| `phase2_prd2.md` | Full requirements document |
| `tracking2.md` | Progress tracker with checklist |
| `assumptions2.md` | All logged assumptions |
| `testing_plan2.md` | All test cases with status |
| `pickup_guide.md` | This file |

### Data
| File | Purpose |
|------|---------|
| `data/transcripts/` | Sample CSV transcripts |
| `data/program_knowledge/` | BSCSE, BSEEE, LLB requirement files |
| `tests/nsu_transcript_ocr/` | Sample images for OCR testing |

---

## Supabase Configuration

**Project URL:** `https://zxzcnpkfabiiecagczao.supabase.co`

**Tables:**
- `profiles` - user_id, email, full_name, role (student/admin)
- `scans` - user_id, student_id, program, input_type, raw_input, waivers, audit_level, result_json, result_text

**Authentication:**
- Provider: Google OAuth
- Email restriction: @northsouth.edu only

**Environment Variables Needed:**
- SUPABASE_URL
- SUPABASE_ANON_KEY
- SUPABASE_SERVICE_KEY (for backend)

---

## API Endpoints

Base URL: `https://nsu-audit-api.railway.app`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /health | No | Health check |
| POST | /api/v1/audit/csv | JWT | Upload CSV, run audit |
| POST | /api/v1/audit/ocr | JWT | Upload image, OCR + audit |
| GET | /api/v1/history | JWT | Get user's scan history |
| DELETE | /api/v1/history/{scan_id} | JWT | Delete own scan |
| GET | /api/v1/users | Admin | List all users |
| PATCH | /api/v1/users/{id}/role | Admin | Change user role |

---

## Build Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Mobile (requires Android SDK)
cd mobile
flutter pub get
flutter build apk --release

# Tests
cd ..
pytest tests/
locust -f tests/locustfile.py --headless -u 20 -r 4 --run-time 60s
```
