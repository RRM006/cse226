# NSU Audit Core — Phase 2 Build Prompts
**For use with OpenCode / Claude / Cursor**
Each part must be completed and confirmed before moving to the next.

---

## HOW TO USE THESE PROMPTS

1. Open your AI coding assistant (OpenCode, Cursor, or Claude).
2. Paste **Part 1** first. Read all files it asks you to read.
3. Wait for the assistant to confirm completion.
4. Check the output yourself.
5. Only then paste **Part 2**, and so on.
6. Never skip parts. Never skip confirmation gates.

---

---

# PART 1 — Project Bootstrap & Supabase Setup

## READ BEFORE DOING ANYTHING

1. Read `phase2_prd.md` in full. Understand every requirement, every layer, every deliverable.
2. Read `README.md` (Phase 1) — understand the existing audit engine, CSV format, grading rules.
3. Read all three program knowledge files:
   - `data/programs/program_knowledge_BSCSE.md`
   - `data/programs/program_knowledge_BSEEE.md`
   - `data/programs/program_knowledge_LLB.md`
4. If anything is unclear, stop and ask before writing any code.

## TASK: Bootstrap the Phase 2 project

### Step 1.1 — Folder Structure
Create the complete Phase 2 folder structure as defined in the PRD Section 12. Create all directories and empty placeholder files now. Do not write any logic yet.

### Step 1.2 — tracking.md
Create `tracking.md` immediately. It must contain:
- A full checklist of every feature across all 8 parts, marked ⬜ Not Started
- What is planned next (Part 1 tasks)
- A Bugs/Issues table (empty for now)

Format:
```
## Phase 2 Progress Tracker

### Part 1: Bootstrap & Supabase
- ⬜ Folder structure created
- ⬜ tracking.md created
- ⬜ assumptions.md created
- ⬜ Supabase schema SQL written
- ⬜ .env.example created
- ⬜ requirements.txt created

[...continue for all parts]

## Bugs/Issues
| # | Layer | Description | Status | Fix Applied |
|---|-------|-------------|--------|-------------|
```

### Step 1.3 — assumptions.md
Create `assumptions.md` immediately. Log any assumption you make using this format:
```
## Assumption #N — [Part / Step]
**Context:** What triggered this
**Assumption:** What you assumed
**Reason:** Why
**Impact:** What changes if wrong
**Source:** [OpenCode assumption / User clarification]
```

### Step 1.4 — Supabase Schema
Write the SQL file `backend/supabase_schema.sql` with:
- `profiles` table (extends `auth.users`)
- `scans` table (all columns from PRD Section 5)
- Row Level Security policies for student and admin (from PRD Section 5)
- Enable RLS on both tables
- Comment every block clearly

### Step 1.5 — Environment Setup
Create `backend/.env.example` with these variables (no real values):
```
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=
RAILWAY_PORT=8000
```

Create `backend/requirements.txt` with:
```
fastapi
uvicorn[standard]
supabase
python-multipart
easyocr
opencv-python-headless
pillow
asyncpg
python-jose[cryptography]
httpx
locust
pytest
pytest-asyncio
black
flake8
isort
pre-commit
```

### Step 1.6 — FastAPI Skeleton
Create `backend/main.py` — a minimal FastAPI app:
- App title: "NSU Audit Core API v2"
- Include `/health` endpoint returning `{"status": "ok", "version": "2.0"}`
- Include `cors` middleware (allow all origins for now)
- Import (but don't implement yet) routers for audit, history, users
- Print startup message with API docs URL

### Step 1.7 — Config
Create `backend/config.py` using `pydantic BaseSettings`:
- Load `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`, `PORT` from env
- Export a single `settings` singleton

## COMPLETION GATE — Part 1
Before marking Part 1 done:
- [ ] All folders and placeholder files exist
- [ ] `tracking.md` has full feature checklist
- [ ] `assumptions.md` exists and is being updated
- [ ] `supabase_schema.sql` is complete and correct
- [ ] `.env.example` has all required variables
- [ ] `requirements.txt` has all dependencies
- [ ] FastAPI starts with `uvicorn backend.main:app` with no errors
- [ ] `/health` returns `{"status": "ok"}`
- [ ] Update `tracking.md` to mark Part 1 tasks ✅

**Present `tracking.md` to the user. Wait for explicit "go ahead" before starting Part 2.**

---

---

# PART 2 — Supabase Auth Middleware & Database Layer

> ⚠️ Do NOT begin until the user has confirmed Part 1 is complete.

## TASK: Wire up Supabase Auth and the database client

### Step 2.1 — Supabase Client
Create `backend/database.py`:
- Initialize `supabase` client using `settings.SUPABASE_URL` and `settings.SUPABASE_SERVICE_KEY`
- Provide async helper functions:
  - `get_profile(user_id: str) -> dict`
  - `create_scan(scan_data: dict) -> dict`
  - `get_scans_by_user(user_id: str) -> list`
  - `get_all_scans() -> list` (admin only)
  - `delete_scan(scan_id: str, user_id: str) -> bool`

### Step 2.2 — Auth Middleware
Create `backend/auth.py`:
- Dependency function `get_current_user(token: str = Depends(oauth2_scheme))`
- Validate the Supabase JWT using Supabase's public JWKS endpoint
- Extract user `id`, `email`, `role` from the token payload
- Return a `CurrentUser` dataclass/model with `id`, `email`, `role`
- If token is invalid or expired, raise `HTTPException(401)`

Create `require_admin` dependency:
- Uses `get_current_user`
- Raises `HTTPException(403)` if `current_user.role != "admin"`

### Step 2.3 — Profiles Auto-Create
Create a Supabase Edge Function or trigger in `supabase_schema.sql` that auto-inserts a row in `profiles` whenever a new user signs up via Google OAuth:
```sql
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO profiles (id, email, full_name, role)
  VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name', 'student');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();
```

### Step 2.4 — Test Auth Locally
Add a test endpoint to `main.py` (remove after testing):
```python
@app.get("/api/v1/me")
async def get_me(current_user = Depends(get_current_user)):
    return {"user_id": current_user.id, "email": current_user.email, "role": current_user.role}
```
Test it with a valid Supabase JWT from Postman or `curl`.

## COMPLETION GATE — Part 2
- [ ] `database.py` helper functions all work
- [ ] Auth middleware validates real Supabase JWT correctly
- [ ] Invalid token correctly returns 401
- [ ] `/api/v1/me` returns correct user info
- [ ] `require_admin` correctly returns 403 for non-admin user
- [ ] Profile auto-created on Google login (test with a real Google account)
- [ ] Update `tracking.md`

**Present `tracking.md` to the user. Wait for "go ahead" before Part 3.**

---

---

# PART 3 — Audit Service (Wraps Phase 1 Engine)

> ⚠️ Do NOT begin until the user has confirmed Part 2 is complete.

## TASK: Wrap the Phase 1 Python scripts into a callable service layer

### Step 3.1 — Copy Phase 1 Core
Copy these files from `src/` into `backend/core/`:
- `level1_credit_tally.py`
- `level2_cgpa_calculator.py`
- `level3_audit_engine.py`

Do NOT modify the logic. Only refactor the interface:
- Extract all `print()` output into a returned string (capture stdout using `io.StringIO`)
- Extract all `input()` prompts (for waivers) into a parameter: `waivers: list[str]`
- Each script should now have a callable main function: `run_level1(csv_text: str, program: str) -> dict`
- Return both `result_text` (formatted output string) and `result_json` (structured data dict)

The structured `result_json` must include at minimum:
```json
{
  "student_id": "...",
  "program": "...",
  "audit_level": 1,
  "total_credits": 120,
  "cgpa": 3.42,
  "standing": "First Class (Good Standing)",
  "eligible": false,
  "missing_courses": [],
  "excluded_courses": [],
  "waivers_applied": []
}
```

### Step 3.2 — Audit Service
Create `backend/services/audit_service.py`:
```python
async def run_audit(
    csv_text: str,
    program: str,        # BSCSE | BSEEE | LLB
    audit_level: int,    # 1 | 2 | 3
    waivers: list[str],  # ['ENG102', 'MAT116']
    knowledge_file: str  # path to program_knowledge_*.md
) -> dict:
    # calls the appropriate core level function
    # returns {result_text, result_json}
```

### Step 3.3 — Audit Router (CSV only for now)
Create `backend/routers/audit.py`:
- `POST /api/v1/audit/csv`
  - Accept multipart form with: `file`, `program`, `audit_level`, `waivers` (optional)
  - Read CSV file content as string
  - Call `audit_service.run_audit()`
  - Save result to DB via `scan_service.create_scan()`
  - Return full response per PRD contract

### Step 3.4 — Scan Service
Create `backend/services/scan_service.py`:
- `async def save_scan(user_id, result, input_type, csv_text) -> dict`
- `async def get_user_history(user_id) -> list`
- `async def get_scan_by_id(scan_id) -> dict`
- `async def delete_scan(scan_id, user_id) -> bool`

### Step 3.5 — Test CSV Audit End-to-End
Use the existing Phase 1 test CSV files to test the API:
```bash
curl -X POST https://localhost:8000/api/v1/audit/csv \
  -H "Authorization: Bearer <jwt>" \
  -F "file=@data/test_L3_cse_standard.csv" \
  -F "program=BSCSE" \
  -F "audit_level=3"
```
Verify the response matches the PRD contract.

## COMPLETION GATE — Part 3
- [ ] Phase 1 core functions are callable without `print()` or `input()`
- [ ] `run_audit()` returns both `result_text` and `result_json`
- [ ] CSV audit endpoint works end-to-end with authentication
- [ ] Scan is saved to Supabase DB after each audit
- [ ] All 3 audit levels work (L1, L2, L3)
- [ ] All 3 programs work (BSCSE, BSEEE, LLB)
- [ ] Update `tracking.md`

**Present `tracking.md` to the user. Wait for "go ahead" before Part 4.**

---

---

# PART 4 — OCR Service

> ⚠️ Do NOT begin until the user has confirmed Part 3 is complete.

## TASK: Build the EasyOCR pipeline to extract transcript data from images

### Step 4.1 — OCR Service
Create `backend/services/ocr_service.py`.

The pipeline must:
1. Accept an uploaded image (JPG, PNG) or PDF first page
2. Pre-process with OpenCV:
   - Convert to grayscale
   - Apply adaptive thresholding for contrast
   - Deskew if rotation detected
3. Run EasyOCR with English language
4. Cluster text boxes by Y-coordinate to identify rows
5. For each row, map detected text to: `course_code`, `course_name`, `credits`, `grade`, `semester`
6. Validate each field:
   - `course_code`: must match regex `[A-Z]{2,4}\d{3}[A-Z]?`
   - `grade`: must be one of the valid NSU grades
   - `credits`: must be 0, 1, 2, or 3
7. Return:
```python
{
  "rows": [
    {"course_code": "CSE115", "course_name": "...", "credits": 3, "grade": "A", "semester": "Spring 2023", "confidence": 0.94}
  ],
  "csv_text": "course_code,course_name,...\nCSE115,...",
  "warnings": ["Low confidence on row 5: grade unclear"],
  "confidence_avg": 0.89
}
```

### Step 4.2 — OCR Audit Endpoint
Add `POST /api/v1/audit/ocr` to `backend/routers/audit.py`:
- Accept image upload
- Call `ocr_service.extract_transcript(image_bytes)`
- If `confidence_avg < 0.60`, return `422` with error and OCR warnings
- Otherwise, feed `csv_text` to `audit_service.run_audit()`
- Include OCR metadata in response (`ocr_confidence`, `ocr_warnings`, `ocr_extracted_rows`)

### Step 4.3 — Test OCR
Create test images for OCR testing:
- `tests/ocr_samples/clean_transcript.png` — a screenshot of a clean, well-formatted transcript
- `tests/ocr_samples/low_quality.jpg` — blurry or skewed transcript (to test confidence filtering)

Write `tests/test_ocr.py`:
- Test that clean image extracts all rows correctly
- Test that low-quality image returns appropriate warnings
- Test that extracted CSV feeds correctly into Level 3 audit

## COMPLETION GATE — Part 4
- [ ] EasyOCR successfully reads a sample NSU transcript image
- [ ] Row parser correctly extracts course_code, grade, credits
- [ ] Low-confidence rows are flagged, not silently dropped
- [ ] OCR endpoint works end-to-end
- [ ] OCR result feeds into audit engine and produces correct output
- [ ] Tests in `test_ocr.py` pass
- [ ] Update `tracking.md`

**Present `tracking.md` to the user. Wait for "go ahead" before Part 5.**

---

---

# PART 5 — History Routes & Updated CLI

> ⚠️ Do NOT begin until the user has confirmed Part 4 is complete.

## TASK: History API routes + update the CLI

### Step 5.1 — History Router
Create `backend/routers/history.py`:

- `GET /api/v1/history`
  - Returns current user's scans (paginated, newest first)
  - Query params: `limit=20`, `offset=0`
  - Uses `get_current_user` dependency

- `GET /api/v1/history/{scan_id}`
  - Returns full scan including `result_text` and `result_json`
  - Only accessible by the scan's owner or an admin

- `DELETE /api/v1/history/{scan_id}`
  - Deletes scan only if `user_id` matches current user (or admin)

- `GET /api/v1/history/user/{user_id}` (Admin only)
  - Uses `require_admin` dependency
  - Returns full history for any user

### Step 5.2 — Users Router
Create `backend/routers/users.py`:

- `GET /api/v1/users` (Admin only)
  - Returns list of all users with scan counts

- `PATCH /api/v1/users/{user_id}/role` (Admin only)
  - Body: `{"role": "admin" | "student"}`
  - Updates `profiles.role`

### Step 5.3 — Updated CLI
Update `cli/audit_cli.py` to add:

**New commands** (in addition to all existing Phase 1 commands):

`audit-cli login`
- Opens browser to Supabase Google OAuth URL
- Listens on localhost callback port for the token
- Saves JWT to `~/.nsu_audit/credentials.json`
- Prints "✅ Logged in as <email>"

`audit-cli logout`
- Deletes `~/.nsu_audit/credentials.json`
- Prints "Logged out."

`audit-cli history`
- Reads saved JWT, calls `GET /api/v1/history`
- Prints a formatted table of past scans

`--remote` flag on existing audit commands:
```bash
python cli/audit_cli.py transcript.csv BSCSE program_knowledge_BSCSE.md --remote
```
- If `--remote` is passed: run audit locally AND send result to the API (saves to history)
- If not passed: run fully offline (Phase 1 behavior unchanged)

### Step 5.4 — Test History
- Run 3 audits as a student user
- Verify all 3 appear in `GET /api/v1/history`
- Delete one, verify 2 remain
- Test admin can see all scans

## COMPLETION GATE — Part 5
- [ ] History GET/DELETE routes work with correct auth
- [ ] Admin can view all users' scans
- [ ] `audit-cli login` completes Google OAuth flow successfully
- [ ] `audit-cli history` shows correct results from API
- [ ] `--remote` flag saves local audit result to DB
- [ ] Offline mode still works without any auth (Phase 1 behavior)
- [ ] Update `tracking.md`

**Present `tracking.md` to the user. Wait for "go ahead" before Part 6.**

---

---

# PART 6 — React Web App

> ⚠️ Do NOT begin until the user has confirmed Part 5 is complete.

## TASK: Build the full React web frontend

### Tech
- React + Vite
- Supabase JS client for auth
- Tailwind CSS (or plain CSS if preferred — keep it clean)
- Deploy to Vercel

### Step 6.1 — Supabase Auth
In `frontend/src/lib/supabase.js`:
- Initialize Supabase client
- Export `supabase` singleton

In `frontend/src/lib/api.js`:
- All API call functions (wrapping `fetch`)
- Auto-attach `Authorization: Bearer <jwt>` header using current Supabase session

### Step 6.2 — Pages to Build

**`Login.jsx`**
- "Login with Google" button → calls `supabase.auth.signInWithOAuth({ provider: 'google' })`
- Redirect to Upload page after success
- If already logged in, redirect away from login

**`Upload.jsx`**
- File input: accepts CSV or image (JPG/PNG)
- Dropdown: select Program (BSCSE / BSEEE / LLB)
- Dropdown: select Audit Level (1 / 2 / 3)
- Text input: Waivers (comma-separated, optional)
- "Run Audit" button → POST to correct endpoint based on file type
- Loading state during audit

**`Result.jsx`**
- Displays audit result
- Show summary card: Student ID, Program, CGPA, Eligibility, Credits
- Show full formatted text in a `<pre>` block (the `result_text` from API)
- "Save to History" button (already saved automatically, just confirms)
- "New Audit" button to go back to Upload

**`History.jsx`**
- Table of past scans: Date | Program | Level | CGPA | Status
- Click a row → shows full Result view for that scan
- Delete button per row (with confirmation)

**`AdminPanel.jsx`** (visible only if `role === 'admin'`)
- List of all users with scan counts
- Button to view a user's full history
- Role change button (Student ↔ Admin)

### Step 6.3 — Routing & Auth Guard
Use React Router v6:
- `/` → redirect to `/upload` if logged in, else `/login`
- `/login` — public
- `/upload` — protected
- `/result/:scan_id` — protected
- `/history` — protected
- `/admin` — protected, admin only

Add an `AuthGuard` component that checks Supabase session and redirects to login if unauthenticated.

### Step 6.4 — Deploy to Vercel
- `vercel.json` with `rewrites` for SPA routing
- Set environment variables in Vercel: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_API_URL`

## COMPLETION GATE — Part 6
- [ ] Login with real Google account works
- [ ] CSV upload → audit result displayed correctly
- [ ] Image upload → OCR audit result displayed with confidence info
- [ ] History page shows all past scans
- [ ] History delete works
- [ ] Admin panel visible only to admin users
- [ ] App deployed and accessible on Vercel
- [ ] Update `tracking.md`

**Present `tracking.md` to the user. Wait for "go ahead" before Part 7.**

---

---

# PART 7 — Flutter Mobile App

> ⚠️ Do NOT begin until the user has confirmed Part 6 is complete.

## TASK: Build the Flutter mobile app (Android + iOS)

### Step 7.1 — Dependencies (`pubspec.yaml`)
Add:
```yaml
dependencies:
  supabase_flutter: ^2.0.0
  image_picker: ^1.0.0
  http: ^1.0.0
  file_picker: ^6.0.0
  flutter_secure_storage: ^9.0.0
```

### Step 7.2 — Screens to Build

**`login_screen.dart`**
- "Sign in with Google" button using `supabase.auth.signInWithOAuth(OAuthProvider.google)`
- On success, navigate to Upload screen

**`upload_screen.dart`**
- Two buttons: "Upload CSV" (FilePicker) and "Take Photo / Gallery" (ImagePicker)
- Dropdowns for Program and Audit Level
- Optional waiver text field
- "Run Audit" button → calls `api_service.runAudit()`
- CircularProgressIndicator during processing

**`result_screen.dart`**
- Summary card: CGPA, Eligibility badge (green/red), Credits
- Scrollable pre-formatted text (the `result_text`)
- "Back" and "View History" buttons

**`history_screen.dart`**
- ListView of past scans: date, program, CGPA, eligibility
- Tap to view full result
- Swipe to delete

### Step 7.3 — Services

**`auth_service.dart`**
- `signInWithGoogle()`
- `signOut()`
- `getCurrentSession()` → returns JWT
- `isAdmin()` → checks user role

**`api_service.dart`**
- `runCsvAudit(file, program, level, waivers)` → POST `/api/v1/audit/csv`
- `runOcrAudit(imageFile, program, level)` → POST `/api/v1/audit/ocr`
- `getHistory()` → GET `/api/v1/history`
- `deleteScan(scanId)` → DELETE `/api/v1/history/{scanId}`
- Attach `Authorization: Bearer <jwt>` header to every request

### Step 7.4 — Build APK for Demo
```bash
flutter build apk --release
```

## COMPLETION GATE — Part 7
- [ ] Google login works on Android device/emulator
- [ ] CSV upload and audit works end-to-end
- [ ] Camera/gallery photo → OCR audit works
- [ ] History screen shows correct data
- [ ] APK builds successfully
- [ ] Update `tracking.md`

**Present `tracking.md` to the user. Wait for "go ahead" before Part 8.**

---

---

# PART 8 — CI/CD Pipeline, Load Testing & Deployment

> ⚠️ Do NOT begin until the user has confirmed Part 7 is complete.

## TASK: Finalize code quality pipeline, load test, and deploy everything

### Step 8.1 — Pre-commit Hooks
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-large-files
        args: [--maxkb=500]
```

Install: `pre-commit install`

### Step 8.2 — GitHub Actions CI
Create `.github/workflows/ci.yml`:
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: black --check backend/
      - run: flake8 backend/ --max-line-length=100
      - run: isort --check-only backend/
      - run: pytest tests/ -v

  deploy-backend:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Railway
        run: railway up --detach
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Vercel
        run: vercel --prod --token ${{ secrets.VERCEL_TOKEN }}
```

### Step 8.3 — Load Test (Locust)
Create `tests/locustfile.py`:

```python
from locust import HttpUser, task, between
import json

TEST_JWT = "paste_a_valid_test_jwt_here"
TEST_CSV_PATH = "data/test_L3_cse_standard.csv"

class AuditUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def run_csv_audit(self):
        with open(TEST_CSV_PATH, "rb") as f:
            self.client.post(
                "/api/v1/audit/csv",
                headers={"Authorization": f"Bearer {TEST_JWT}"},
                files={"file": f},
                data={"program": "BSCSE", "audit_level": "3"}
            )
    
    @task(1)
    def get_history(self):
        self.client.get(
            "/api/v1/history",
            headers={"Authorization": f"Bearer {TEST_JWT}"}
        )
```

Run load test:
```bash
locust -f tests/locustfile.py --headless -u 20 -r 4 --run-time 60s \
  --host https://nsu-audit-api.railway.app \
  --html tests/load_test_report.html
```

Pass criteria:
- 0% failure rate
- P95 response time for CSV audit < 5000ms
- P95 response time for history < 500ms

### Step 8.4 — Railway Deployment
Create `backend/Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

Set Railway environment variables:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_KEY`

Deploy: `railway up`

### Step 8.5 — README_PHASE2.md
Write a complete `README_PHASE2.md` with:
- Project overview
- Architecture diagram (text-based)
- Setup instructions (Supabase, Railway, Vercel, Flutter)
- How to run locally
- How to run the CLI in both offline and remote mode
- How to run tests
- How to run the load test
- Environment variables reference
- API documentation link (FastAPI auto-docs URL)

## FINAL COMPLETION GATE
Before declaring Phase 2 complete:
- [ ] All pre-commit hooks pass on latest code
- [ ] GitHub Actions CI passes on `main`
- [ ] Backend deployed and live on Railway
- [ ] Web app deployed and live on Vercel
- [ ] Flutter APK builds successfully
- [ ] Locust load test: 20 concurrent users, 0% errors
- [ ] Load test HTML report saved to `tests/load_test_report.html`
- [ ] `README_PHASE2.md` is complete and accurate
- [ ] All tasks in `tracking.md` marked ✅
- [ ] All `assumptions.md` entries are logged

**Present the final `tracking.md` to the user for sign-off.**

---

---

## RULES TO FOLLOW AT ALL TIMES

1. Never start a part while the previous one is incomplete or unconfirmed.
2. Never make an assumption silently — log it in `assumptions.md` immediately.
3. Always update `tracking.md` after completing any task.
4. If something breaks, log it in the Bugs/Issues table in `tracking.md` before continuing.
5. Present `tracking.md` to the user at every completion gate and wait for explicit "go ahead".
6. Never commit secrets or `.env` files to git.
7. All API errors must return structured JSON — never expose raw Python tracebacks.
8. The Phase 1 offline CLI must continue to work exactly as before (backward compatible).
9. OCR uses EasyOCR only — no external AI API calls.
10. All Python code must pass `black` and `flake8` before being committed.
