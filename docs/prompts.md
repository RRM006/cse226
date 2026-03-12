# NSU Audit Core — Development Prompts

*Combined prompts from Phase 1 and Phase 2*  
*Course: CSE226.1 — Vibe Coding | Instructor: Dr. Nabeel Mohammed*

---

# PART I: Phase 1 Development Prompts

## SETUP — Read Before Doing Anything Else

1. Read `CSE226_Proj_1.md` fully. Understand every requirement, every level, and every deliverable.
2. Read `README.md` fully. Understand the architecture, output formats, grading scale, policies, and edge cases.
3. Read all three knowledge files:
   - `program_knowledge_BSCSE.md`
   - `program_knowledge_BSEEE.md`
   - `program_knowledge_LLB.md`
   Understand each program's mandatory courses, credit requirements per category, elective trails, capstone requirements, waiver rules, and prerequisite chains.
4. If anything is ambiguous or unclear after reading all five files, **stop and ask the user for clarification before writing any code**.

---

## FILES TO CREATE AND MAINTAIN THROUGHOUT THE PROJECT

### `tracking.md`
Create this file immediately after reading the source files. Update it after **every significant action**.

It must always contain:
- A checklist of every feature/task across all three levels, marked ✅ Done, 🔄 In Progress, or ⬜ Not Started
- What was completed in the last session
- What is planned next
- Any blockers or open questions
- A **Bugs/Issues** section

### `assumptions.md`
Every time you make an assumption — not just at the start, but **throughout the entire project** — log it immediately.

### `testing_plan.md`
Create this file **before writing any code**. It must contain:
- A definition of what "testing" means for this project
- Test cases for each level
- Integration tests for multi-program support
- Policy enforcement tests
- Expected inputs and expected outputs for each test case

---

## NSU GRADING SCALE

| Grade | Points | Grade | Points |
|-------|--------|-------|--------|
| A     | 4.0    | C     | 2.0    |
| A-    | 3.7    | C-    | 1.7    |
| B+    | 3.3    | D+    | 1.3    |
| B     | 3.0    | D     | 1.0    |
| B-    | 2.7    | F/I/W/X | 0.0 (excluded from CGPA) |

**CGPA Formula:**
```
CGPA = Σ(Grade Point × Credits) / Σ(Credits for valid grades)
```

---

## Phase 1 Implementation Levels

### Level 1: The Credit Tally Engine
- Read student transcript and calculate total valid credits
- Determine which grades count and which do not (F, W, I, X, 0-credit labs)
- Output: Total credits earned, credits attempted, breakdown by category

### Level 2: The Logic Gate & Waiver Handler
- Calculate weighted CGPA
- Handle program-specific waivers
- Interactive prompt: "Waivers granted for ENG102 or BUS112?"
- Ensure non-grade entries don't break CGPA calculation

### Level 3: The Audit & Deficiency Reporter
- Compare student's history against program.md rules
- Identify missing mandatory courses
- Flag "Probation" status (CGPA < 2.0)
- Handle retake scenarios (only best grade counts)

---

## Phase 1 Deliverables

1. **The tool:** Functional CLI scripts (one per level)
2. **Knowledge Files:** Optimized CSV and program knowledge files
3. **Test Cases:** test_L1.csv, test_L2.csv, test_L3.csv, retake scenario

---

# PART II: Phase 2 Development Prompts

## HOW TO USE THESE PROMPTS

1. Open your AI coding assistant (OpenCode, Cursor, or Claude).
2. Paste **Part 1** first. Read all files it asks you to read.
3. Wait for the assistant to confirm completion.
4. Check the output yourself.
5. Only then paste **Part 2**, and so on.
6. Never skip parts. Never skip confirmation gates.

---

## PART 1 — Project Bootstrap & Supabase Setup

### READ BEFORE DOING ANYTHING

1. Read `prd.md` in full. Understand every requirement, every layer, every deliverable.
2. Read all three program knowledge files:
   - `program_knowledge_BSCSE.md`
   - `program_knowledge_BSEEE.md`
   - `program_knowledge_LLB.md`
3. If anything is unclear, stop and ask before writing any code.

### TASK: Bootstrap the Phase 2 project

**Step 1.1 — Folder Structure**
Create the complete Phase 2 folder structure as defined in the PRD. Create all directories and empty placeholder files now.

**Step 1.2 — tracking2.md**
Create `tracking2.md` immediately with full checklist of all features.

**Step 1.3 — assumptions2.md**
Create `assumptions2.md` immediately. Log any assumption using the standard format.

**Step 1.4 — Supabase Schema**
Write `backend/supabase_schema.sql` with:
- `profiles` table (extends `auth.users`)
- `scans` table
- Row Level Security policies
- Enable RLS on both tables

**Step 1.5 — Environment Setup**
Create `backend/.env.example` and `backend/requirements.txt`

---

## PART 2 — Supabase Auth Middleware & Database Layer

### TASK: Create auth middleware and DB helpers

**Step 2.1 — Database Helpers**
Create `backend/database.py` with functions:
- `get_profile(user_id)`
- `create_scan(scan_data)`
- `get_scans_by_user(user_id)`
- `get_all_scans()` (admin)
- `delete_scan(scan_id, user_id)`

**Step 2.2 — Auth Middleware**
Create `backend/auth.py` with:
- `get_current_user()` dependency to validate Supabase JWT
- `require_admin` dependency to check admin role
- `CurrentUser` model

**Step 2.3 — Test Endpoint**
Create `/api/v1/me` endpoint to return current user info.

---

## PART 3 — Audit Service (Phase 1 Engine Wrapper)

### TASK: Wrap Phase 1 engine in FastAPI service

**Step 3.1 — Copy Phase 1 Engine**
Copy `archive/src/level1_credit_tally.py`, `level2_cgpa_calculator.py`, `level3_audit_engine.py` to `backend/core/`

**Step 3.2 — Refactor for API**
- Replace `print()` calls with StringIO capture
- Replace `input()` prompts with function parameters
- Return both `result_text` and `result_json`

**Step 3.3 — Audit Service**
Create `backend/services/audit_service.py` with `run_audit()` function

**Step 3.4 — Router**
Create `backend/routers/audit.py` with `POST /api/v1/audit/csv` endpoint

---

## PART 4 — OCR Service

### TASK: Implement EasyOCR transcript scanning

**Step 4.1 — OCR Service**
Create `backend/services/ocr_service.py` with:
- Image pre-processing (grayscale, contrast)
- EasyOCR text extraction
- Row parsing via Y-coordinate clustering
- Column mapping (course_code, course_name, credits, grade, semester)
- Confidence scoring

**Step 4.2 — OCR Endpoint**
Create `POST /api/v1/audit/ocr` endpoint

---

## PART 5 — History Routes & Updated CLI

### TASK: Create history API and update CLI

**Step 5.1 — History Router**
Create `backend/routers/history.py` with:
- `GET /api/v1/history`
- `GET /api/v1/history/{scan_id}`
- `DELETE /api/v1/history/{scan_id}`

**Step 5.2 — Users Router**
Create `backend/routers/users.py` with:
- `GET /api/v1/users`
- `PATCH /api/v1/users/{user_id}/role`

**Step 5.3 — CLI Updates**
Update `cli/audit_cli.py` with:
- `login` command
- `logout` command
- `history` command
- `--remote` flag

---

## PART 6 — React Web App

### TASK: Build React frontend

**Step 6.1 — Setup**
Create React + Vite project in `frontend/`

**Step 6.2 — Supabase Client**
Create `frontend/src/lib/supabase.js`

**Step 6.3 — API Client**
Create `frontend/src/lib/api.js`

**Step 6.4 — Pages**
Create all pages:
- Login.jsx
- Upload.jsx
- Result.jsx
- History.jsx
- AdminPanel.jsx

---

## PART 7 — Flutter Mobile App

### TASK: Build Flutter mobile app

**Step 7.1 — Setup**
Create Flutter project in `mobile/`

**Step 7.2 — Screens**
Create all screens:
- login_screen.dart
- upload_screen.dart
- result_screen.dart
- history_screen.dart

**Step 7.3 — Services**
Create:
- auth_service.dart
- api_service.dart

---

## PART 8 — CI/CD, Load Testing & Deployment

### TASK: Finalize pipeline and deploy

**Step 8.1 — Pre-commit Hooks**
Create `.pre-commit-config.yaml`

**Step 8.2 — GitHub Actions**
Create `.github/workflows/ci.yml`

**Step 8.3 — Load Test**
Create `tests/locustfile.py` for 20 concurrent users

**Step 8.4 — Railway Deployment**
Create `backend/Procfile`

**Step 8.5 — README**
Write comprehensive `README.md`

---

## Development Rules (Apply to All Parts)

1. **Never skip confirmation gates** — Present tracking.md after each part
2. **Never make assumptions silently** — Log in assumptions.md immediately
3. **Never commit secrets** — Use .env files, not hardcoded credentials
4. **Always update tracking** — After completing any task
5. **All API errors return JSON** — Never expose raw Python tracebacks
6. **Phase 1 CLI must work** — Backward compatibility required
7. **OCR uses EasyOCR only** — No external AI API calls
8. **All Python code passes black and flake8** — Before committing

---

## Project Structure

```
nsu-audit-core/
├── backend/              # FastAPI backend
├── frontend/             # React web app
├── mobile/               # Flutter app
├── cli/                  # CLI tool
├── tests/                # Test files
├── docs/                 # Documentation
├── .github/              # CI/CD workflows
├── program_knowledge/    # Program requirements
├── archive/              # Phase 1 preserved
├── .pre-commit-config.yaml
└── .gitignore
```
