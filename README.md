# NSU Audit Core

**A Full-Stack Graduation Audit System for North South University**

Developed by Rafiur Rahman Mashrafi  
Course: CSE226.1 — Vibe Coding | Instructor: Dr. Nabeel Mohammed

---

## Overview

NSU Audit Core automates graduation eligibility checking for North South University (NSU) students across three academic programs:

- **BSCSE** — BSc in Computer Science & Engineering
- **BSEEE** — BSc in Electrical & Electronic Engineering
- **LL.B Honors** — Bachelor of Law

### Three-Tier Audit Engine

| Level | What It Does |
|-------|-------------|
| **L1** | Credit Tally — counts valid earned credits |
| **L2** | CGPA Calculator — weighted CGPA with waivers and retakes |
| **L3** | Full Graduation Audit — prerequisites, electives, capstone check |

### Platform Support

| Platform | Stack |
|----------|-------|
| Web App | React 19 + Vite + TailwindCSS 4 |
| Mobile App | Flutter (Android & iOS) |
| CLI | Python — offline and remote modes |
| AI Agent | MCP Server for natural language auditing |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend API | FastAPI (Python 3.11) |
| Database | PostgreSQL via Supabase |
| Authentication | Supabase Auth (Google OAuth 2.0) |
| OCR Engine | EasyOCR |
| Frontend | React 19 + Vite + TailwindCSS 4 |
| Mobile | Flutter 3.x |
| CI/CD | GitHub Actions + pre-commit |
| Hosting | Railway (Backend), Vercel (Frontend) |

---

## Project Structure

```
nsu-audit-core/
├── backend/                  # FastAPI REST API
│   ├── core/                 # Audit engine (L1, L2, L3) + shared utilities
│   │   ├── shared.py         # Common functions (parse_transcript, etc.)
│   │   ├── level1_credit_tally.py
│   │   ├── level2_cgpa_calculator.py
│   │   ├── level3_audit_engine.py
│   │   ├── external_transfer.py
│   │   └── transfer_handler.py
│   ├── routers/              # API route definitions
│   ├── services/             # Business logic layer
│   ├── main.py               # Application entry point
│   └── requirements.txt
├── frontend/                 # React web application
│   ├── src/
│   │   ├── pages/            # Login, Upload, Result, History
│   │   ├── components/       # Reusable UI components
│   │   └── lib/              # API client, Supabase client
│   └── vite.config.js
├── mobile/                   # Flutter mobile application
│   └── lib/
│       ├── screens/
│       └── services/
├── cli/                      # Python CLI tool
│   └── audit_cli.py
├── mcp/                      # MCP AI agent server
│   └── mcp_server.py
├── program_knowledge/        # Graduation rules (Markdown)
│   ├── program_knowledge_BSCSE.md
│   ├── program_knowledge_BSEEE.md
│   └── program_knowledge_LLB.md
├── archive/                  # Legacy scripts (testbat/ only)
│   └── testbat/
└── tests/                    # Test CSVs + unit tests
    ├── BSCSE/
    ├── BSEEE/
    ├── LLB/
    ├── test_audit.py         # Unit tests for audit engine
    ├── test_ocr.py
    └── locustfile.py
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Flutter SDK 3.x
- Supabase account

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your Supabase credentials to .env
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Add your Supabase credentials to .env
npm run dev
```

### CLI (Offline Mode)

```bash
cd cli
pip install -r requirements.txt
python audit_cli.py l1 ../tests/BSCSE/L1/L1_BSCSE_001_basic_passing.csv BSCSE
```

### Mobile

```bash
cd mobile
flutter pub get
flutter run
```

### Interactive Launcher

```bash
python web_launcher.py
```

---

## Environment Variables

### Backend — `backend/.env`

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
RAILWAY_PORT=8000
```

### Frontend — `frontend/.env`

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_API_URL=http://localhost:8000
```

### Mobile — Build Arguments

```bash
flutter build apk \
  --dart-define=SUPABASE_URL=https://your-project.supabase.co \
  --dart-define=SUPABASE_ANON_KEY=your_anon_key \
  --dart-define=API_BASE_URL=https://nsu-audit-api.railway.app
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/me` | Current user info |
| POST | `/api/v1/audit/csv` | Run CSV-based audit |
| POST | `/api/v1/audit/ocr` | Run OCR + audit |
| GET | `/api/v1/history` | User scan history |
| DELETE | `/api/v1/history/{scan_id}` | Delete a scan record |
| GET | `/api/v1/users` | List all users (Admin only) |
| PATCH | `/api/v1/users/{id}/role` | Update user role (Admin only) |

---

## Testing

```bash
# Unit tests
pytest tests/ -v

# Load testing
locust -f tests/locustfile.py --headless -u 20 -r 4 \
  --run-time 60s --host https://nsu-audit-api.railway.app
```

---

## Deployment

### Backend — Railway

1. Connect repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically via GitHub Actions

### Frontend — Vercel

1. Import repository to Vercel
2. Set environment variables
3. Deploy automatically via GitHub Actions

---

## License

Developed for CSE226.1 — Vibe Coding at North South University.

## Author

Rafiur Rahman Mashrafi  
North South University | CSE226.1 — Vibe Coding  
Instructor: Dr. Nabeel Mohammed
