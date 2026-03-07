# NSU Audit Core — Phase 2 PRD
**Course:** CSE226.1 — Vibe Coding | **Instructor:** Dr. Nabeel Mohammed
**Version:** 2.0 | **Due:** Sunday, March 8, 2026

---

## 1. Overview

Phase 1 delivered a robust CLI-based graduation audit engine for NSU's three programs (BSCSE, BSEEE, LL.B Honors). Phase 2 evolves that engine into a **full-stack, multi-client service** — accessible via Web App, Mobile App (Flutter), and CLI — backed by a shared cloud database, Google Authentication, OCR-powered transcript ingestion, and a scan history system.

The Phase 1 audit logic is **reused as-is** as the core engine. Phase 2 wraps it inside a FastAPI backend, exposes it as a REST API, and connects it to multiple clients.

---

## 2. Goals

| Goal | Description |
|------|-------------|
| **OCR Ingestion** | Allow users to upload a photo/scan of an NSU transcript; extract data using EasyOCR without any AI model |
| **Multi-client Access** | Same backend service accessible via Web App, Flutter Mobile App, and updated CLI |
| **Auth** | Google OAuth 2.0 login across all three clients via Supabase Auth |
| **Scan History** | Every audit run (CSV or OCR) is saved to the DB and retrievable per user account |
| **Role System** | Admin sees all users' scans; Students see only their own |
| **Concurrency** | Support minimum 20 concurrent users with automated load testing |
| **Code Quality** | GitHub Actions CI pipeline with pre-commit hooks and linting |

---

## 3. Tech Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| **Backend API** | FastAPI (Python) | Async support, auto-docs, same language as Phase 1 |
| **OCR** | EasyOCR (Python) | Pure Python, no cloud dependency, easy setup |
| **Database** | PostgreSQL via Supabase | Free tier, built-in Auth, Row Level Security |
| **Auth** | Supabase Auth (Google OAuth) | Works across web, mobile, CLI |
| **Web Frontend** | React + Vite (hosted on Vercel) | Fast, free deployment |
| **Mobile App** | Flutter (Android + iOS) | Single codebase |
| **CLI** | Python (updated Phase 1 CLI) | Backward compatible, adds auth + remote mode |
| **Backend Hosting** | Railway | Free tier, supports Python/FastAPI |
| **CI/CD** | GitHub Actions + pre-commit | Linting, formatting, automated tests |
| **Load Testing** | Locust (Python) | Easy concurrent user simulation |

---

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTS                              │
│   ┌──────────┐    ┌──────────────┐    ┌──────────────────┐  │
│   │ Web App  │    │ Flutter App  │    │   CLI (Python)   │  │
│   │ (React)  │    │ (Mobile)     │    │   (Updated)      │  │
│   └────┬─────┘    └──────┬───────┘    └────────┬─────────┘  │
└────────┼─────────────────┼────────────────────┼────────────┘
         │                 │                    │
         └─────────────────┴────────────────────┘
                           │  HTTPS REST API
         ┌─────────────────▼───────────────────────┐
         │           FastAPI Backend               │
         │  ┌────────────────────────────────────┐ │
         │  │         Auth Middleware             │ │
         │  │     (Supabase JWT validation)       │ │
         │  └────────────┬───────────────────────┘ │
         │               │                         │
         │  ┌────────────▼───────────────────────┐ │
         │  │         Route Handlers              │ │
         │  │  /audit  /ocr  /history  /users     │ │
         │  └────────────┬───────────────────────┘ │
         │               │                         │
         │  ┌────────────▼──────────┐ ┌──────────┐ │
         │  │  Phase 1 Audit Engine │ │ EasyOCR  │ │
         │  │  (L1 + L2 + L3 logic) │ │ Engine   │ │
         │  └───────────────────────┘ └──────────┘ │
         └─────────────────┬───────────────────────┘
                           │
         ┌─────────────────▼───────────────────────┐
         │           Supabase (PostgreSQL)         │
         │   users | scans | audit_results         │
         └─────────────────────────────────────────┘
```

---

## 5. Database Schema

All tables are in Supabase (PostgreSQL). Row Level Security (RLS) enforces role-based access.

### `profiles` table
Extends Supabase Auth's `auth.users`.

```sql
CREATE TABLE profiles (
  id          UUID PRIMARY KEY REFERENCES auth.users(id),
  email       TEXT UNIQUE NOT NULL,
  full_name   TEXT,
  role        TEXT NOT NULL DEFAULT 'student',  -- 'student' | 'admin'
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### `scans` table
One record per audit run (whether CSV upload or OCR scan).

```sql
CREATE TABLE scans (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES profiles(id),
  student_id      TEXT,                   -- extracted from transcript
  program         TEXT,                   -- BSCSE | BSEEE | LLB
  input_type      TEXT NOT NULL,          -- 'csv' | 'ocr_image'
  raw_input       TEXT,                   -- CSV text or OCR extracted text
  waivers         TEXT[],                 -- e.g. ['ENG102', 'MAT116']
  audit_level     INTEGER NOT NULL,       -- 1 | 2 | 3
  result_json     JSONB NOT NULL,         -- full structured audit result
  result_text     TEXT NOT NULL,          -- formatted CLI-style output
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### Row Level Security Policies

```sql
-- Students can only see their own scans
CREATE POLICY "student_own_scans" ON scans
  FOR SELECT USING (auth.uid() = user_id);

-- Admins can see all scans
CREATE POLICY "admin_all_scans" ON scans
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin')
  );

-- Any authenticated user can insert their own scan
CREATE POLICY "insert_own_scan" ON scans
  FOR INSERT WITH CHECK (auth.uid() = user_id);
```

---

## 6. API Endpoints

Base URL: `https://nsu-audit-api.railway.app`

### Auth (handled by Supabase, not FastAPI)
| Method | Path | Description |
|--------|------|-------------|
| — | Supabase Google OAuth | Login via Google, returns JWT |

### Audit
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/audit/csv` | Required | Upload CSV, run audit (L1/L2/L3) |
| `POST` | `/api/v1/audit/ocr` | Required | Upload image, run OCR then audit |
| `GET`  | `/api/v1/audit/{scan_id}` | Required | Get a specific scan result |

### History
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET`  | `/api/v1/history` | Required | Get current user's scan history |
| `GET`  | `/api/v1/history/{user_id}` | Admin only | Get any user's scan history |
| `DELETE` | `/api/v1/history/{scan_id}` | Required | Delete a scan (own only) |

### Users (Admin only)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET`  | `/api/v1/users` | Admin | List all users |
| `PATCH` | `/api/v1/users/{id}/role` | Admin | Change user role |

### Health
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET`  | `/health` | None | API health check |

---

## 7. Request/Response Contracts

### POST `/api/v1/audit/csv`
**Request** (multipart/form-data):
```
file: <CSV file>
program: "BSCSE" | "BSEEE" | "LLB"
audit_level: 1 | 2 | 3
waivers: "ENG102,MAT116"   (optional)
knowledge_file: "BSCSE"    (which program knowledge to use)
```

**Response:**
```json
{
  "scan_id": "uuid",
  "student_id": "2012345678",
  "program": "BSCSE",
  "audit_level": 3,
  "summary": {
    "total_credits": 127,
    "cgpa": 3.42,
    "standing": "First Class (Good Standing)",
    "eligible": false,
    "missing_courses": 3
  },
  "result_text": "=== NSU AUDIT CORE - LEVEL 3 ===\n...",
  "result_json": { ... },
  "created_at": "2026-03-05T10:30:00Z"
}
```

### POST `/api/v1/audit/ocr`
**Request** (multipart/form-data):
```
image: <JPG/PNG file>
program: "BSCSE" | "BSEEE" | "LLB"
audit_level: 1 | 2 | 3
waivers: "ENG102"  (optional)
```

**Response:** Same as CSV audit response, with additional:
```json
{
  "ocr_confidence": 0.87,
  "ocr_extracted_rows": 35,
  "ocr_warnings": ["Low confidence on row 12: 'CSE3?5'"]
}
```

### GET `/api/v1/history`
**Response:**
```json
{
  "total": 12,
  "scans": [
    {
      "scan_id": "uuid",
      "input_type": "csv",
      "program": "BSCSE",
      "audit_level": 3,
      "summary": { "cgpa": 3.42, "eligible": false },
      "created_at": "2026-03-05T10:30:00Z"
    }
  ]
}
```

---

## 8. OCR Engine Design

EasyOCR is used to extract transcript data from uploaded images — **no AI model, no cloud API**.

### OCR Pipeline

```
Image Upload
     │
     ▼
Pre-processing (OpenCV)
  - Grayscale conversion
  - Contrast enhancement
  - Deskew if needed
     │
     ▼
EasyOCR Text Extraction
  - English language model
  - Returns list of (bbox, text, confidence)
     │
     ▼
Row Parser
  - Detect table rows via Y-coordinate clustering
  - Map columns: course_code | course_name | credits | grade | semester
  - Handle merged cells, split rows
     │
     ▼
Validation & Confidence Check
  - Flag rows with confidence < 0.7
  - Validate course_code format (e.g. CSE115, ENG102)
  - Validate grade values against known scale
     │
     ▼
CSV-equivalent data structure
  (feeds into same Phase 1 audit engine)
```

### OCR Confidence Rules
- Row confidence ≥ 0.85 → accepted as-is
- Row confidence 0.70–0.84 → accepted with warning flagged in response
- Row confidence < 0.70 → row excluded, error flagged, user asked to verify manually

---

## 9. Authentication Flow

### Web App & Mobile
1. User clicks "Login with Google"
2. Supabase Auth handles the OAuth redirect
3. On success, Supabase returns a JWT
4. All API calls include `Authorization: Bearer <jwt>` header
5. FastAPI middleware validates JWT against Supabase's public key

### CLI
1. First run: `audit-cli login` → opens browser to Supabase Google OAuth
2. Token saved to `~/.nsu_audit/credentials.json`
3. Subsequent calls include the token automatically
4. `audit-cli logout` clears saved token

### Role Assignment
- All new users default to `student` role
- Admin manually sets `role = 'admin'` in Supabase dashboard or via API

---

## 10. Feature Requirements

### FR-1: OCR Transcript Scan
- FR-1.1: Accept JPG, PNG, PDF (first page) image uploads
- FR-1.2: Extract course rows using EasyOCR (no AI API)
- FR-1.3: Map extracted rows to `course_code, course_name, credits, grade, semester`
- FR-1.4: Flag low-confidence rows in the response
- FR-1.5: Feed extracted data to the same Phase 1 audit engine

### FR-2: CSV Upload
- FR-2.1: Accept CSV matching Phase 1 schema
- FR-2.2: Run audit at requested level (1, 2, or 3)
- FR-2.3: Accept optional waivers parameter
- FR-2.4: Return structured JSON + formatted text result

### FR-3: Scan History
- FR-3.1: Every audit run (CSV or OCR) automatically saved to DB
- FR-3.2: User can view their full scan history
- FR-3.3: Each history entry shows: date, program, audit level, CGPA, eligibility
- FR-3.4: User can click a history entry to view the full audit report
- FR-3.5: User can delete their own scan entries

### FR-4: Google Auth
- FR-4.1: Google OAuth login on Web App
- FR-4.2: Google OAuth login on Flutter Mobile App
- FR-4.3: Browser-based Google OAuth flow for CLI (`audit-cli login`)
- FR-4.4: All API endpoints require valid Supabase JWT (except `/health`)

### FR-5: Role-Based Access
- FR-5.1: Students see and manage only their own scans
- FR-5.2: Admin can view all users' scans
- FR-5.3: Admin can change any user's role
- FR-5.4: Admin dashboard shows user list and total scan counts

### FR-6: CLI (Updated)
- FR-6.1: Retain full offline mode (Phase 1 behavior, no auth required)
- FR-6.2: Add `--remote` flag to send results to the API and save to history
- FR-6.3: `audit-cli login` / `audit-cli logout` for Google auth
- FR-6.4: `audit-cli history` to view past scans from terminal

### FR-7: Web App
- FR-7.1: Login page with Google OAuth button
- FR-7.2: Upload transcript (CSV or image)
- FR-7.3: Select program, audit level, waivers
- FR-7.4: View formatted audit result
- FR-7.5: Scan history list with ability to view past results
- FR-7.6: Admin panel: view all users, all scans

### FR-8: Flutter Mobile App
- FR-8.1: Google login screen
- FR-8.2: Camera capture or gallery select for transcript image
- FR-8.3: OCR processing with progress indicator
- FR-8.4: Display audit result in clean card-based UI
- FR-8.5: Scan history screen

---

## 11. Non-Functional Requirements

### NFR-1: Concurrency
- Minimum 20 concurrent users supported without degradation
- Load test must verify this with Locust
- Target: P95 response time < 5s for CSV audit, < 15s for OCR audit

### NFR-2: Code Quality
- All Python code passes `flake8` and `black` formatting check
- Pre-commit hooks block commits that fail linting
- GitHub Actions runs tests + lint on every push to `main`

### NFR-3: Security
- All API endpoints require valid Supabase JWT
- Row Level Security enforced at DB level (not just API level)
- No credentials committed to git (`.env` files, Supabase keys)
- Environment variables only via Railway/Vercel secret stores

### NFR-4: Reliability
- FastAPI error handlers return structured JSON errors (never raw 500s)
- OCR failures return partial results with warnings, not hard errors
- DB connection pooling via asyncpg

---

## 12. Project Structure

```
nsu-audit-core/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings from env vars
│   ├── auth.py                  # Supabase JWT validation middleware
│   ├── database.py              # Supabase client + DB helpers
│   ├── routers/
│   │   ├── audit.py             # /api/v1/audit/* routes
│   │   ├── history.py           # /api/v1/history/* routes
│   │   └── users.py             # /api/v1/users/* routes
│   ├── services/
│   │   ├── ocr_service.py       # EasyOCR pipeline
│   │   ├── audit_service.py     # Wraps Phase 1 engine
│   │   └── scan_service.py      # Save/retrieve scans from DB
│   ├── core/                    # Phase 1 audit engine (copied from src/)
│   │   ├── level1_credit_tally.py
│   │   ├── level2_cgpa_calculator.py
│   │   └── level3_audit_engine.py
│   ├── requirements.txt
│   ├── Procfile                 # Railway deployment
│   └── .env.example
│
├── frontend/                    # React + Vite web app
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Upload.jsx
│   │   │   ├── Result.jsx
│   │   │   ├── History.jsx
│   │   │   └── AdminPanel.jsx
│   │   ├── components/
│   │   ├── lib/
│   │   │   ├── supabase.js      # Supabase client
│   │   │   └── api.js           # API call helpers
│   │   └── App.jsx
│   ├── package.json
│   └── vercel.json
│
├── mobile/                      # Flutter app
│   ├── lib/
│   │   ├── main.dart
│   │   ├── screens/
│   │   │   ├── login_screen.dart
│   │   │   ├── upload_screen.dart
│   │   │   ├── result_screen.dart
│   │   │   └── history_screen.dart
│   │   ├── services/
│   │   │   ├── auth_service.dart
│   │   │   └── api_service.dart
│   │   └── models/
│   └── pubspec.yaml
│
├── cli/                         # Updated CLI
│   ├── audit_cli.py             # Updated with --remote, login, history
│   └── credentials.py           # Token management
│
├── tests/
│   ├── test_ocr.py
│   ├── test_api.py
│   ├── test_audit_service.py
│   └── locustfile.py            # Load testing (20 concurrent users)
│
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI pipeline
│
├── .pre-commit-config.yaml      # Pre-commit hooks
├── data/                        # Phase 1 data files (transcripts, program_knowledge)
└── README_PHASE2.md
```

---

## 13. CI/CD Pipeline

### GitHub Actions (`ci.yml`)
Triggers on every push to `main` and every pull request.

Steps:
1. Install dependencies
2. Run `black --check` (formatting)
3. Run `flake8` (linting)
4. Run `pytest tests/` (unit + integration tests)
5. On `main` only: auto-deploy backend to Railway, frontend to Vercel

### Pre-commit hooks (`.pre-commit-config.yaml`)
Blocks local commits that fail:
- `black` auto-format
- `flake8` lint check
- `isort` import sorting
- Trailing whitespace removal
- Large file check (block accidental model file commits)

---

## 14. Load Testing (Locust)

### Target: 20 concurrent users

Test scenarios in `locustfile.py`:
1. **Login + CSV audit** — simulate full flow end-to-end
2. **History fetch** — authenticated GET to /history
3. **OCR audit** — upload a test image, run L3 audit

Pass criteria:
- 0% error rate at 20 users
- P95 latency < 5s for CSV
- P95 latency < 15s for OCR

Run command:
```bash
locust -f tests/locustfile.py --headless -u 20 -r 4 --run-time 60s --host https://nsu-audit-api.railway.app
```

---

## 15. Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | FastAPI backend | Deployed on Railway, full audit + OCR + history API |
| 2 | React Web App | Deployed on Vercel, all 5 pages functional |
| 3 | Flutter Mobile App | APK + iOS build, Google auth + OCR + history |
| 4 | Updated CLI | `audit-cli` with `--remote`, `login`, `history` |
| 5 | Supabase setup | DB schema, RLS policies, Google OAuth configured |
| 6 | GitHub Actions CI | Lint + test pipeline passing on main |
| 7 | Locust load test | Report showing 20 concurrent users passed |
| 8 | README_PHASE2.md | Full setup and run instructions |

---

## 16. Timeline (6 days to March 8)

| Day | Focus |
|-----|-------|
| Day 1 (Mar 3) | Supabase setup, DB schema, Google OAuth, FastAPI skeleton |
| Day 2 (Mar 4) | Audit service (wraps Phase 1), OCR service, core API routes |
| Day 3 (Mar 5) | Scan history routes, auth middleware, CLI updates |
| Day 4 (Mar 6) | React Web App (all pages, Supabase auth) |
| Day 5 (Mar 7) | Flutter Mobile App (login, upload, history) |
| Day 6 (Mar 8) | CI/CD pipeline, load testing, bugfixes, deployment |

---

## 17. Out of Scope (Phase 2)

- AI model integration (planned for Phase 3)
- Prerequisite graph visualization
- Email notifications
- Offline mobile mode
- Student self-service portal (admin-only for now)
