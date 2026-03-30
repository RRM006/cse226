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
| Authentication | Supabase Auth (Google OAuth 2.0) + JWT for students |
| OCR Engine | EasyOCR |
| Frontend | React 19 + Vite + TailwindCSS 4 |
| Mobile | Flutter 3.x with Provider + Dio |
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
│       ├── config/           # API configuration
│       ├── models/           # Data models
│       ├── providers/        # State management (Provider)
│       ├── screens/          # All screens
│       │   ├── auth/         # Login gate, student login
│       │   ├── student/      # Student dashboard, results, requests
│       │   └── ...           # Upload, result, history screens
│       ├── services/         # API, Auth, Storage services
│       └── widgets/          # Reusable widgets
├── cli/                      # Python CLI tool
│   └── audit_cli.py
├── mcp/                      # MCP AI agent server
│   └── mcp_server.py
├── program_knowledge/        # Graduation rules (Markdown)
├── archive/                  # Legacy scripts
└── tests/                    # Test CSVs + unit tests
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTS                              │
├──────────────┬──────────────────┬───────────────────────────┤
│  Web App     │   Mobile App     │     MCP AI Agent          │
│  (React)     │   (Flutter)      │     (Python)              │
│              │                  │                           │
│  • Admin     │  • Student Login │  • Natural language audit │
│  • Student   │  • Dashboard     │  • Google Drive access    │
│  • Upload    │  • Audit Results │  • Batch processing       │
│  • History   │  • Requests      │  • Email notifications    │
│              │  • Upload        │                           │
└──────┬───────┴────────┬─────────┴───────────┬──────────────┘
       │                │                     │
       │                │                     │
┌──────▼────────────────▼─────────────────────▼──────────────┐
│                    BACKEND API (FastAPI)                    │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ Audit       │  │ Student      │  │ History         │   │
│  │ Endpoints   │  │ Endpoints    │  │ Endpoints       │   │
│  │             │  │              │  │                 │   │
│  │ POST /csv   │  │ POST /login  │  │ GET /history    │   │
│  │ POST /ocr   │  │ POST /change │  │ GET /history/:id│   │
│  │ POST /save  │  │   -password  │  │ DELETE /history │   │
│  │             │  │ GET /me      │  │   /:id          │   │
│  │             │  │ GET /results │  │                 │   │
│  │             │  │ POST/GET     │  │                 │   │
│  │             │  │   /requests  │  │                 │   │
│  └──────┬──────┘  └──────┬───────┘  └────────┬────────┘   │
│         │                │                    │            │
│  ┌──────▼────────────────▼────────────────────▼────────┐  │
│  │              AUDIT ENGINE (Core)                     │  │
│  │                                                      │  │
│  │  L1: Credit Tally    L2: CGPA Calc   L3: Full Audit │  │
│  │                                                      │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                 │
└──────────────────────────┼─────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│                    DATABASE (Supabase/PostgreSQL)           │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ profiles │  │ students │  │ scans    │  │ requests │  │
│  │          │  │          │  │          │  │          │  │
│  │ • id     │  │ • id     │  │ • id     │  │ • id     │  │
│  │ • email  │  │ • sid    │  │ • user_id│  │ • sid    │  │
│  │ • role   │  │ • name   │  │ • program│  │ • message│  │
│  │          │  │ • hash   │  │ • result │  │ • status │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Feature Comparison (Web vs Mobile vs Backend)

| Feature              | Backend | Web Frontend | Mobile  |
|----------------------|---------|-------------|---------|
| **Student Login**    | ✅      | ✅          | ✅ NEW  |
| **Admin Login (OAuth)** | ✅   | ✅          | ✅      |
| **Student Dashboard**| ✅      | ✅          | ✅ NEW  |
| **Student Audit Results** | ✅ | ✅          | ✅ NEW  |
| **Student Requests** | ✅      | ✅          | ✅ NEW  |
| **Change Password**  | ✅      | ✅          | ✅ NEW  |
| **Upload CSV**       | ✅      | ✅          | ✅      |
| **Upload OCR**       | ✅      | ✅          | ✅      |
| **View History**     | ✅      | ✅          | ✅      |
| **Delete Scans**     | ✅      | ✅          | ✅      |
| **Admin Manage Students** | ✅ | ✅          | 🔜      |
| **Admin Requests**   | ✅      | ✅          | 🔜      |
| **Admin Audit Results** | ✅   | ✅          | 🔜      |

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

### Mobile

```bash
cd mobile
flutter pub get
flutter run \
  --dart-define=API_BASE_URL=https://your-api.railway.app \
  --dart-define=SUPABASE_URL=https://your-project.supabase.co \
  --dart-define=SUPABASE_ANON_KEY=your_anon_key
```

### CLI (Offline Mode)

```bash
cd cli
pip install -r requirements.txt
python audit_cli.py l1 ../tests/BSCSE/L1/L1_BSCSE_001_basic_passing.csv BSCSE
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
STUDENT_JWT_SECRET=your-student-jwt-secret
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
  --dart-define=API_BASE_URL=https://nsu-audit-api.railway.app \
  --dart-define=SUPABASE_URL=https://your-project.supabase.co \
  --dart-define=SUPABASE_ANON_KEY=your_anon_key
```

---

## API Endpoints

### Audit Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/audit/csv` | Run CSV-based audit |
| POST | `/api/v1/audit/ocr` | Run OCR + audit |
| POST | `/api/v1/audit/save` | Save scan result |

### Student Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/student/login` | Student login (ID/password) |
| POST | `/api/v1/student/change-password` | Change password |
| GET | `/api/v1/student/me` | Get student profile |
| GET | `/api/v1/student/audit-results` | List audit results |
| GET | `/api/v1/student/audit-results/{id}` | Get audit result detail |
| POST | `/api/v1/student/requests` | Submit review request |
| GET | `/api/v1/student/requests` | List student requests |

### History Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/history` | User scan history |
| GET | `/api/v1/history/{scan_id}` | Get scan detail |
| DELETE | `/api/v1/history/{scan_id}` | Delete a scan record |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/me` | Current user info |
| GET | `/api/v1/users` | List all users |
| PATCH | `/api/v1/users/{id}/role` | Update user role |
| GET | `/api/v1/students` | List all students |
| POST | `/api/v1/students` | Create student account |
| PATCH | `/api/v1/students/{id}` | Update student |
| DELETE | `/api/v1/students/{id}` | Delete student |
| PATCH | `/api/v1/students/{id}/reset-password` | Reset student password |
| GET | `/api/v1/audit-results` | List all audit results |
| POST | `/api/v1/audit-results` | Create audit result |
| GET | `/api/v1/requests` | List all requests |
| PATCH | `/api/v1/requests/{id}` | Update request status |

---

## Authentication Flow

### Student Authentication (Mobile)

```
1. Student enters Student ID + Password
2. POST /api/v1/student/login
3. Backend validates credentials, returns JWT token
4. Token stored in flutter_secure_storage
5. Subsequent requests include: Authorization: Bearer <token>
6. Token valid for 8 hours
7. First login forces password change
```

### Admin Authentication (Web/Mobile)

```
1. User clicks "Sign in with Google"
2. Supabase OAuth flow (Google)
3. Only @northsouth.edu emails allowed
4. Supabase session token used
5. Subsequent requests include: Authorization: Bearer <supabase_token>
```

---

## Android Usage Guide

### A. Install Using APK

1. Build the APK: `cd mobile && flutter build apk --release`
2. Find the APK at: `mobile/build/app/outputs/flutter-apk/app-release.apk`
3. Transfer to your Android phone
4. Go to Settings → Security → "Unknown Sources" → Enable
5. Tap the APK file to install
6. Grant any requested permissions

### B. Run Using Flutter (Developer Mode)

```bash
# 1. Enable Developer Options on your phone
#    Settings → About Phone → Tap "Build Number" 7 times

# 2. Enable USB Debugging
#    Settings → Developer Options → USB Debugging → Enable

# 3. Connect phone via USB cable

# 4. Verify device is detected
flutter doctor
flutter devices

# 5. Run the app
cd mobile
flutter pub get
flutter run \
  --dart-define=API_BASE_URL=https://your-api.railway.app \
  --dart-define=SUPABASE_URL=https://your-project.supabase.co \
  --dart-define=SUPABASE_ANON_KEY=your_key
```

### C. Build APK

```bash
cd mobile
flutter build apk --release \
  --dart-define=API_BASE_URL=https://your-api.railway.app \
  --dart-define=SUPABASE_URL=https://your-project.supabase.co \
  --dart-define=SUPABASE_ANON_KEY=your_key

# Output location: build/app/outputs/flutter-apk/app-release.apk
```

### D. Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Device not detected | Run `flutter doctor --android-licenses`, accept all |
| Gradle build fails | Run `cd mobile/android && ./gradlew clean`, then `flutter clean && flutter pub get` |
| USB permission denied | Run `sudo usermod -aG plugdev $LOGNAME`, restart terminal |
| App crashes on launch | Check `--dart-define` values are correct, run `flutter logs` |
| API connection refused | Ensure backend is running and API_BASE_URL is correct |

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

### Mobile — Google Play Store

1. Build release APK: `flutter build apk --release`
2. Sign the APK with your keystore
3. Upload to Google Play Console

---

## License

Developed for CSE226.1 — Vibe Coding at North South University.

## Author

Rafiur Rahman Mashrafi  
North South University | CSE226.1 — Vibe Coding  
Instructor: Dr. Nabeel Mohammed
