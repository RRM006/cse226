# NSU Audit Core — Phase 2

**Course:** CSE226.1 — Vibe Coding | **Instructor:** Dr. Nabeel Mohammed

Phase 2 transforms the Phase 1 CLI graduation audit engine into a full-stack, multi-client service with OCR, authentication, and scan history.

---

## Overview

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL via Supabase
- **Auth:** Google OAuth 2.0 via Supabase
- **OCR:** EasyOCR (pure Python)
- **Frontend:** React + Vite
- **Mobile:** Flutter
- **CLI:** Python (Phase 1 updated with remote mode)
- **Hosting:** Railway (backend), Vercel (frontend)
- **CI/CD:** GitHub Actions + pre-commit

---

## Architecture

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
         │  ┌────────────▼────────────────────┐   │
         │  │         Route Handlers            │   │
         │  │  /audit  /ocr  /history  /users   │   │
         │  └────────────┬─────────────────────┘   │
         │               │                          │
         │  ┌────────────▼──────────┐ ┌────────┐ │
         │  │  Phase 1 Audit Engine  │ │ EasyOCR│ │
         │  │  (L1 + L2 + L3 logic)  │ │ Engine │ │
         │  └────────────────────────┘ └────────┘ │
         └─────────────────┬───────────────────────┘
                           │
         ┌─────────────────▼───────────────────────┐
         │           Supabase (PostgreSQL)          │
         │   users | profiles | scans               │
         └───────────────────────────────────────────┘
```

---

## API Endpoints

Base URL: `https://nsu-audit-api.railway.app`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Health check |
| POST | `/api/v1/audit/csv` | JWT | Upload CSV, run audit |
| POST | `/api/v1/audit/ocr` | JWT | Upload image, OCR + audit |
| GET | `/api/v1/history` | JWT | Get user's scan history |
| DELETE | `/api/v1/history/{scan_id}` | JWT | Delete own scan |
| GET | `/api/v1/users` | Admin | List all users |
| PATCH | `/api/v1/users/{id}/role` | Admin | Change user role |

---

## Setup Instructions

### 1. Supabase Setup

1. Create a Supabase project at https://supabase.com
2. Go to **SQL Editor** and run `backend/supabase_schema.sql`
3. Configure **Authentication > Providers > Google**: Enable Google OAuth
4. Add redirect URL: `http://localhost:54321` (for CLI dev)
5. Get credentials:
   - Project URL: `https://<project>.supabase.co`
   - Anon Key: Settings > API > `anon public`
   - Service Key: Settings > API > `service_role`

### 2. Backend Setup

```bash
cd backend
cp .env.example .env
# Edit .env with your Supabase credentials

pip install -r requirements.txt
uvicorn main:app --reload
```

**Environment Variables:**
```
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_KEY=<service_key>
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env:
# VITE_SUPABASE_URL=<project_url>
# VITE_SUPABASE_ANON_KEY=<anon_key>
# VITE_API_URL=http://localhost:8000

npm run dev
```

### 4. Mobile Setup (Flutter)

```bash
cd mobile
flutter pub get
# Edit lib/services/auth_service.dart with your Supabase credentials

flutter build apk --release
```

### 5. CLI Setup

```bash
cd cli
pip install -r requirements.txt
cp ../backend/.env.example .env
# Edit .env with Supabase credentials

python audit_cli.py --help
```

---

## Running the CLI

### Offline Mode (Phase 1 behavior)
```bash
python audit_cli.py l1 tests/BSCSE/L1/L1_BSCSE_001_basic_passing.csv BSCSE
python audit_cli.py l2 tests/BSCSE/L2/L2_BSCSE_001_cgpa_calc.csv BSCSE
python audit_cli.py l3 tests/BSCSE/L3/L3_BSCSE_001_complete.csv BSCSE
```

### Remote Mode (with auth & history)
```bash
# Login first
python audit_cli.py login

# Run audit and save to cloud
python audit_cli.py l3 tests/BSCSE/L3/L3_BSCSE_001_complete.csv BSCSE --remote

# View history
python audit_cli.py history

# Logout
python audit_cli.py logout
```

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

---

## Deployment

### Backend (Railway)

1. Push code to GitHub
2. Connect repo to Railway
3. Set environment variables in Railway dashboard
4. Deploy: `railway up`

### Frontend (Vercel)

1. Push code to GitHub
2. Import project in Vercel
3. Set environment variables:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
   - `VITE_API_URL` (Railway backend URL)
4. Deploy automatically on push to main

---

## Development

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

Hooks run: black, flake8, isort, trailing-whitespace, large-file check

### GitHub Actions CI

On push to `main` and PRs:
1. black --check
2. flake8 check
3. isort check
4. pytest tests/
5. Auto-deploy to Railway (main only)
6. Auto-deploy to Vercel (main only)

---

## User Roles

- **Student:** Can run audits, view own history, delete own scans
- **Admin:** All student permissions + view all users, view all scans, change user roles

Admin role must be manually set in Supabase dashboard (profiles table).

---

## OCR

EasyOCR extracts transcript data from images. Confidence rules:
- ≥ 0.85: accepted as-is
- 0.70–0.84: accepted with warning
- < 0.70: row excluded

---

## FastAPI Documentation

Interactive API docs available at: `https://nsu-audit-api.railway.app/docs`

---

## License

NSU Audit Core — CSE226.1 — Dr. Nabeel Mohammed
