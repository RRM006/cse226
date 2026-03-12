# NSU Audit Core

**A Full-Stack Graduation Audit System for North South University**

*Developed by Rafiur Rahman Mashrafi*  
*Course: CSE226.1 — Vibe Coding | Instructor: Dr. Nabeel Mohammed*

---

## Overview

NSU Audit Core is a comprehensive graduation audit system designed for North South University (NSU). It provides multi-platform access to verify student graduation eligibility across three academic programs: **BSCSE** (Computer Science), **BSEEE** (Electrical Engineering), and **LL.B Honors** (Law).

The system evolved from a CLI tool (Phase 1) into a full-stack multi-client service (Phase 2), supporting Web, Mobile, and CLI interfaces with OCR-powered transcript scanning and cloud-based history management.

---

## Features

### Core Functionality
- **Three-Tier Audit System**
  - Level 1: Credit Tally
  - Level 2: CGPA Calculation
  - Level 3: Full Graduation Eligibility Audit

- **Multi-Program Support**
  - BSCSE (Bachelor of Science in Computer Science & Engineering)
  - BSEEE (Bachelor of Science in Electrical & Electronic Engineering)
  - LL.B Honors (Bachelor of Law)

- **OCR Transcript Scanning**
  - Upload transcript images (JPG, PNG, PDF)
  - Automatic data extraction using EasyOCR
  - Confidence-based validation

### Authentication & Authorization
- Google OAuth 2.0 Authentication via Supabase
- Role-based access control (Student / Admin)
- NSU email domain restriction (@northsouth.edu)

### Multi-Platform Access
- **Web App**: React + Vite frontend
- **Mobile App**: Flutter (Android & iOS)
- **CLI**: Python-based command-line tool with offline and remote modes

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend API | FastAPI (Python) |
| Database | PostgreSQL via Supabase |
| Authentication | Supabase Auth (Google OAuth) |
| OCR Engine | EasyOCR |
| Frontend | React + Vite |
| Mobile | Flutter |
| Hosting | Railway (Backend), Vercel (Frontend) |
| CI/CD | GitHub Actions + Pre-commit |
| Load Testing | Locust |

---

## Project Structure

```
nsu-audit-core/
├── backend/              # FastAPI backend
│   ├── main.py          # Application entry point
│   ├── config.py        # Configuration settings
│   ├── auth.py          # Authentication middleware
│   ├── database.py      # Database utilities
│   ├── routers/         # API route handlers
│   │   ├── audit.py     # Audit endpoints
│   │   ├── history.py   # History endpoints
│   │   └── users.py     # User management
│   ├── services/        # Business logic
│   │   ├── audit_service.py
│   │   ├── ocr_service.py
│   │   └── scan_service.py
│   ├── core/            # Phase 1 audit engine
│   └── requirements.txt
├── frontend/            # React web application
│   ├── src/
│   │   ├── pages/       # Login, Upload, Result, History, Admin
│   │   ├── components/  # Reusable components
│   │   └── lib/         # API and Supabase clients
│   └── package.json
├── mobile/              # Flutter mobile application
│   ├── lib/
│   │   ├── screens/    # App screens
│   │   └── services/   # API and auth services
│   └── pubspec.yaml
├── cli/                # Python CLI tool
│   ├── audit_cli.py    # Main CLI application
│   └── credentials.py   # Token management
├── tests/              # Test files
│   ├── BSCSE/          # Test data
│   ├── BSEEE/
│   ├── LLB/
│   ├── nsu_transcript_ocr/  # OCR test samples
│   └── locustfile.py   # Load testing
├── docs/               # Documentation
└── .github/            # CI/CD workflows
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/audit/csv` | Run audit with CSV upload |
| POST | `/api/v1/audit/ocr` | Run audit with image OCR |
| GET | `/api/v1/history` | Get user's scan history |
| DELETE | `/api/v1/history/{scan_id}` | Delete a scan |
| GET | `/api/v1/users` | List all users (Admin) |
| PATCH | `/api/v1/users/{id}/role` | Change user role (Admin) |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Flutter SDK 3.x
- Supabase account

### Backend Setup

```bash
cd backend
cp .env.example .env
# Edit .env with your Supabase credentials

pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your Supabase credentials

npm run dev
```

### Mobile Setup

```bash
cd mobile
flutter pub get
flutter build apk --release
```

### CLI Setup

```bash
cd cli
pip install -r requirements.txt
python audit_cli.py --help
```

---

## Usage

### CLI Modes

**Offline Mode (Phase 1 behavior):**
```bash
python audit_cli.py l1 tests/BSCSE/L1/L1_BSCSE_001_basic_passing.csv BSCSE
python audit_cli.py l2 tests/BSCSE/L2/L2_BSCSE_001_cgpa_calc.csv BSCSE
python audit_cli.py l3 tests/BSCSE/L3/L3_BSCSE_001_complete.csv BSCSE
```

**Remote Mode (with cloud sync):**
```bash
python audit_cli.py login
python audit_cli.py l3 tests/BSCSE/L3/L3_BSCSE_001_complete.csv BSCSE --remote
python audit_cli.py history
python audit_cli.py logout
```

---

## Running Tests

```bash
# Unit and integration tests
pytest tests/ -v

# Load testing (requires deployed backend)
locust -f tests/locustfile.py --headless -u 20 -r 4 --run-time 60s \
  --host https://nsu-audit-api.railway.app \
  --html tests/load_test_report.html
```

---

## Deployment

### Backend (Railway)
1. Connect repository to Railway
2. Set environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_KEY`
3. Deploy automatically via GitHub Actions

### Frontend (Vercel)
1. Import repository in Vercel
2. Set environment variables:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
   - `VITE_API_URL`
3. Deploy automatically via GitHub Actions

---

## Documentation

Additional documentation available in the `docs/` folder:

- `docs/phase2_prd2.md` - Product Requirements Document
- `docs/phase2_prompts.md` - Development Prompts
- `docs/tracking2.md` - Project Progress Tracker
- `docs/testing_plan2.md` - Test Cases
- `docs/assumptions2.md` - Technical Assumptions

---

## License

This project is developed for educational purposes as part of CSE226.1 — Vibe Coding course at North South University.

---

## Author

**Rafiur Rahman Mashrafi**  
North South University  
CSE226.1 — Vibe Coding  
Instructor: Dr. Nabeel Mohammed
