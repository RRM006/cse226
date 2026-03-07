# Architecture Reference — Phase 2
**NSU Audit Core | Quick reference for vibe coding**

---

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                          CLIENTS                                 │
│                                                                  │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │   Web App        │  │  Flutter Mobile  │  │  CLI (Python)  │  │
│  │  React + Vite    │  │  Android / iOS   │  │  audit_cli.py  │  │
│  │  Vercel          │  │  APK             │  │  --remote flag │  │
│  └────────┬────────┘  └────────┬─────────┘  └───────┬────────┘  │
└───────────┼────────────────────┼────────────────────┼───────────┘
            │                    │                    │
            └────────────────────┴────────────────────┘
                                 │
                         HTTPS REST API
                                 │
┌────────────────────────────────▼─────────────────────────────────┐
│                       FastAPI Backend                            │
│                       Railway deployment                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                   Auth Middleware                          │  │
│  │   Validates Supabase JWT on every request                  │  │
│  │   Extracts: user_id, email, role (student|admin)           │  │
│  └──────────────────────────┬─────────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────▼─────────────────────────────────┐  │
│  │                     Routers                                │  │
│  │   /api/v1/audit/csv    → audit.py                         │  │
│  │   /api/v1/audit/ocr    → audit.py                         │  │
│  │   /api/v1/history/*    → history.py                       │  │
│  │   /api/v1/users/*      → users.py (admin only)            │  │
│  │   /health              → main.py                          │  │
│  └──────┬───────────────────────────────────┬────────────────┘  │
│         │                                   │                    │
│  ┌──────▼──────────────┐     ┌──────────────▼──────────────┐    │
│  │   Audit Service      │     │       OCR Service           │    │
│  │  audit_service.py    │     │    ocr_service.py           │    │
│  │                      │     │                             │    │
│  │  ┌────────────────┐  │     │  1. OpenCV pre-process      │    │
│  │  │  backend/core/ │  │     │  2. EasyOCR extract         │    │
│  │  │  level1_*.py   │  │     │  3. Row cluster by Y-coord  │    │
│  │  │  level2_*.py   │  │     │  4. Map to CSV columns      │    │
│  │  │  level3_*.py   │  │     │  5. Validate + confidence   │    │
│  │  │  (Phase 1      │  │     │  6. Return csv_text         │    │
│  │  │   logic)       │  │     └─────────────────────────────┘    │
│  │  └────────────────┘  │                                        │
│  └──────────────────────┘                                        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                   Scan Service                           │    │
│  │  scan_service.py — save / get / delete scans from DB     │    │
│  └──────────────────────────────┬───────────────────────────┘    │
└─────────────────────────────────┼────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────┐
│                    Supabase (PostgreSQL)                         │
│                    + Google OAuth                                │
│                                                                  │
│   Tables: profiles | scans                                       │
│   RLS: student sees own | admin sees all                        │
│   Auth: Google OAuth → JWT                                       │
└──────────────────────────────────────────────────────────────────┘
```

---

## File-by-File Responsibility Map

### Backend (`backend/`)

| File | Responsibility |
|------|---------------|
| `main.py` | FastAPI app entry, CORS, router registration, /health |
| `config.py` | Pydantic settings, loads env vars |
| `auth.py` | JWT validation, `get_current_user`, `require_admin` |
| `database.py` | Supabase client, all raw DB helper functions |
| `routers/audit.py` | POST /audit/csv and POST /audit/ocr |
| `routers/history.py` | GET/DELETE /history/* |
| `routers/users.py` | GET/PATCH /users/* (admin only) |
| `services/audit_service.py` | Calls Phase 1 core functions, returns result_text + result_json |
| `services/ocr_service.py` | EasyOCR pipeline, returns csv_text + confidence + warnings |
| `services/scan_service.py` | save_scan, get_user_history, get_scan_by_id, delete_scan |
| `core/level1_credit_tally.py` | Phase 1 L1 logic (refactored, no print/input) |
| `core/level2_cgpa_calculator.py` | Phase 1 L2 logic (refactored) |
| `core/level3_audit_engine.py` | Phase 1 L3 logic (refactored) |

### Frontend (`frontend/src/`)

| File | Responsibility |
|------|---------------|
| `lib/supabase.js` | Supabase JS client singleton |
| `lib/api.js` | All fetch() wrappers with auto-auth headers |
| `pages/Login.jsx` | Google OAuth login button |
| `pages/Upload.jsx` | File input, program/level/waiver selects, submit |
| `pages/Result.jsx` | Audit result display |
| `pages/History.jsx` | Scan history table |
| `pages/AdminPanel.jsx` | User management (admin only) |
| `components/AuthGuard.jsx` | Redirects unauthenticated users |

### Mobile (`mobile/lib/`)

| File | Responsibility |
|------|---------------|
| `main.dart` | App entry, Supabase init, routing |
| `screens/login_screen.dart` | Google sign-in button |
| `screens/upload_screen.dart` | CSV/image upload, program select |
| `screens/result_screen.dart` | Display audit result |
| `screens/history_screen.dart` | List + delete past scans |
| `services/auth_service.dart` | signIn, signOut, getSession, isAdmin |
| `services/api_service.dart` | All API calls with auth |

### CLI (`cli/`)

| File | Responsibility |
|------|---------------|
| `audit_cli.py` | All CLI commands including new login/logout/history/--remote |
| `credentials.py` | Read/write `~/.nsu_audit/credentials.json` |

---

## Data Flow: CSV Audit

```
Client (Web/Mobile/CLI)
  │
  ├─ POST /api/v1/audit/csv
  │   multipart: file=<csv>, program=BSCSE, audit_level=3, waivers=ENG102
  │   headers: Authorization: Bearer <jwt>
  │
FastAPI auth middleware
  ├─ Validate JWT → get user_id, role
  │
audit.py router
  ├─ Read CSV bytes → decode to string
  ├─ Call audit_service.run_audit(csv_text, program, level, waivers)
  │     └─ calls level3_audit_engine.run_level3(csv_text, waivers, knowledge_file)
  │           └─ returns {result_text, result_json}
  ├─ Call scan_service.save_scan(user_id, result, input_type="csv")
  │     └─ INSERT into scans table
  └─ Return 200 JSON response
```

## Data Flow: OCR Audit

```
Client uploads image
  │
  ├─ POST /api/v1/audit/ocr
  │   multipart: image=<file>, program=BSCSE, audit_level=3
  │
FastAPI auth middleware → validate JWT
  │
audit.py router
  ├─ Read image bytes
  ├─ Call ocr_service.extract_transcript(image_bytes)
  │     ├─ OpenCV pre-process
  │     ├─ EasyOCR.readtext()
  │     ├─ Cluster rows by Y coordinate
  │     ├─ Map to {course_code, course_name, credits, grade, semester}
  │     ├─ Validate fields, compute per-row confidence
  │     └─ Return {rows, csv_text, warnings, confidence_avg}
  ├─ If confidence_avg < 0.60 → return 422
  ├─ Call audit_service.run_audit(csv_text, ...)
  ├─ Call scan_service.save_scan(...)
  └─ Return 200 JSON with OCR metadata + audit result
```

---

## Database Schema (Quick Reference)

```sql
-- profiles: one row per Google user
profiles (
  id UUID PK → auth.users.id,
  email TEXT UNIQUE,
  full_name TEXT,
  role TEXT DEFAULT 'student',   -- 'student' | 'admin'
  created_at TIMESTAMPTZ
)

-- scans: one row per audit run
scans (
  id UUID PK DEFAULT gen_random_uuid(),
  user_id UUID → profiles.id,
  student_id TEXT,               -- from transcript
  program TEXT,                  -- BSCSE | BSEEE | LLB
  input_type TEXT,               -- 'csv' | 'ocr_image'
  raw_input TEXT,                -- CSV text or OCR extracted text
  waivers TEXT[],                -- ['ENG102', 'MAT116']
  audit_level INTEGER,           -- 1 | 2 | 3
  result_json JSONB,             -- full structured result
  result_text TEXT,              -- formatted CLI-style output
  created_at TIMESTAMPTZ
)

-- RLS: students see only their own scans
-- RLS: admins see all scans
```

---

## Environment Variables

### Backend (Railway)
```
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_KEY=<service_key>
PORT=8000
```

### Frontend (Vercel)
```
VITE_SUPABASE_URL=https://<project>.supabase.co
VITE_SUPABASE_ANON_KEY=<anon_key>
VITE_API_URL=https://nsu-audit-api.railway.app
```

### Mobile (Flutter)
```
# In lib/config.dart constants
SUPABASE_URL
SUPABASE_ANON_KEY
API_BASE_URL
```

---

## API Quick Reference

| Method | Path | Auth | Who |
|--------|------|------|-----|
| GET | /health | ❌ | Anyone |
| POST | /api/v1/audit/csv | ✅ JWT | Student/Admin |
| POST | /api/v1/audit/ocr | ✅ JWT | Student/Admin |
| GET | /api/v1/audit/{id} | ✅ JWT | Owner or Admin |
| GET | /api/v1/history | ✅ JWT | Own history |
| GET | /api/v1/history/{id} | ✅ JWT | Owner or Admin |
| DELETE | /api/v1/history/{id} | ✅ JWT | Owner only |
| GET | /api/v1/history/user/{uid} | ✅ Admin | Admin only |
| GET | /api/v1/users | ✅ Admin | Admin only |
| PATCH | /api/v1/users/{id}/role | ✅ Admin | Admin only |

---

## NSU Grade Scale (Quick Reference)

| Grade | Points | Grade | Points |
|-------|--------|-------|--------|
| A | 4.0 | C | 2.0 |
| A- | 3.7 | C- | 1.7 |
| B+ | 3.3 | D+ | 1.3 |
| B | 3.0 | D | 1.0 |
| B- | 2.7 | F/I/W/X | excluded |

**Formula:** `CGPA = Σ(Grade Point × Credits) / Σ(Credits for valid grades)`
Best grade used for retaken courses. Waived courses excluded from CGPA.

---

## Academic Standing (Quick Reference)

| CGPA | Standing |
|------|---------|
| ≥ 3.80 | Summa Cum Laude |
| 3.65–3.79 | Magna Cum Laude |
| 3.50–3.64 | Cum Laude |
| 3.00–3.49 | First Class |
| 2.50–2.99 | Second Class |
| 2.00–2.49 | Third Class |
| < 2.00 | PROBATION |
