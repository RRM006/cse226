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
VALUES (
  NEW.id,
  NEW.email,
  COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
  'student'
)
ON CONFLICT (id) DO NOTHING;
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

# PART 4.0 — CLI Google Auth with NSU Email Restriction

> ⚠️ Do NOT begin until the user has confirmed Part 3 is complete.
> ⚠️ Do NOT begin Part 4 (OCR) until the user has confirmed Part 4.0 is complete.

## CONTEXT

This part wires Google OAuth into the CLI **before** the OCR service is built. From this point forward, all CLI audit commands (l1, l2, l3) require the user to be logged in with a verified `@northsouth.edu` Google account. The offline (Phase 1) logic is untouched — this auth layer wraps around it.

## TASK: Add NSU-restricted Google Auth to the CLI

---

### Step 4.0.1 — Credentials Manager

Create `cli/credentials.py`:

```python
import json
import os
from pathlib import Path

CREDENTIALS_DIR = Path.home() / ".nsu_audit"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"

def save_credentials(access_token: str, refresh_token: str, email: str) -> None:
    """Save JWT and user info to local credentials file."""
    CREDENTIALS_DIR.mkdir(exist_ok=True)
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(
            {"access_token": access_token, "refresh_token": refresh_token, "email": email},
            f,
        )

def load_credentials() -> dict | None:
    """Load saved credentials. Returns None if not found."""
    if not CREDENTIALS_FILE.exists():
        return None
    with open(CREDENTIALS_FILE, "r") as f:
        return json.load(f)

def delete_credentials() -> None:
    """Remove credentials file on logout."""
    if CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.unlink()

def is_logged_in() -> bool:
    return CREDENTIALS_FILE.exists()
```

---

### Step 4.0.2 — NSU Email Validator

Inside `cli/credentials.py`, add:

```python
NSU_EMAIL_DOMAIN = "northsouth.edu"

def validate_nsu_email(email: str) -> bool:
    """Return True only if email ends with @northsouth.edu."""
    return email.strip().lower().endswith(f"@{NSU_EMAIL_DOMAIN}")
```

This check must be enforced **after** Google login returns the user's email from the Supabase JWT — not before, because we rely on Google to verify ownership.

---

### Step 4.0.3 — Login Command

In `cli/audit_cli.py`, implement the `login` command:

**Flow:**
1. Generate a Supabase Google OAuth URL (redirect to `http://localhost:54321/callback`)
2. Open the URL in the user's default browser with `webbrowser.open()`
3. Start a temporary local HTTP server on `localhost:54321` to catch the OAuth callback
4. Extract the `access_token` and `refresh_token` from the callback URL fragment/query
5. Decode the JWT payload (without verifying — just read the `email` claim)
6. **Check:** if `email` does not end with `@northsouth.edu`, print an error and stop — do NOT save credentials
7. Save credentials via `credentials.save_credentials()`
8. Print: `✅ Logged in as <email>`

**Error cases to handle:**
- Non-NSU email → `❌ Login failed: only @northsouth.edu accounts are permitted.`
- Browser fails to open → print the URL and ask user to open manually
- Callback times out after 120 seconds → `❌ Login timed out. Please try again.`

**Suggested implementation sketch:**
```python
import webbrowser
import http.server
import threading
import urllib.parse

def cmd_login():
    oauth_url = build_supabase_oauth_url()  # construct from SUPABASE_URL + anon key
    print("Opening browser for NSU Google login...")
    webbrowser.open(oauth_url)

    token_result = {}

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            token_result["access_token"] = params.get("access_token", [None])[0]
            token_result["refresh_token"] = params.get("refresh_token", [None])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h2>Login complete. Return to your terminal.</h2>")

        def log_message(self, *args):
            pass  # silence server logs

    server = http.server.HTTPServer(("localhost", 54321), CallbackHandler)
    server.timeout = 120
    server.handle_request()

    access_token = token_result.get("access_token")
    if not access_token:
        print("❌ Login failed: no token received.")
        return

    email = decode_jwt_email(access_token)  # base64-decode the JWT payload
    if not validate_nsu_email(email):
        print("❌ Login failed: only @northsouth.edu accounts are permitted.")
        return

    save_credentials(access_token, token_result.get("refresh_token", ""), email)
    print(f"✅ Logged in as {email}")
```

---

### Step 4.0.4 — Logout Command

```python
def cmd_logout():
    delete_credentials()
    print("Logged out.")
```

---

### Step 4.0.5 — Auth Guard for Audit Commands

In `cli/audit_cli.py`, add an `require_login()` guard that is called at the **top** of every audit command handler (l1, l2, l3):

```python
def require_login():
    """Exit with a message if user is not logged in."""
    if not is_logged_in():
        print("❌ You must be logged in to run audits.")
        print("   Run: python cli/audit_cli.py login")
        raise SystemExit(1)
```

Call `require_login()` as the first line inside `cmd_l1()`, `cmd_l2()`, `cmd_l3()`.

The offline Phase 1 logic itself does not change — `require_login()` is purely a pre-flight check.

---

### Step 4.0.6 — CLI Entry Point

Make sure `cli/audit_cli.py` handles these top-level commands via `argparse` or `sys.argv`:

```
python cli/audit_cli.py login              # Google OAuth → NSU email check → save token
python cli/audit_cli.py logout             # Delete saved token
python cli/audit_cli.py l1 <csv> <prog>   # Requires login; runs Level 1 audit
python cli/audit_cli.py l2 <csv> <prog>   # Requires login; runs Level 2 audit
python cli/audit_cli.py l3 <csv> <prog>   # Requires login; runs Level 3 audit
```

Add a `--help` message that explains all commands and the NSU email requirement.

---

### Step 4.0.7 — Supabase OAuth URL Builder

In `cli/audit_cli.py` or a new `cli/auth_helpers.py`:

```python
import os

def build_supabase_oauth_url() -> str:
    supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    anon_key = os.environ.get("SUPABASE_ANON_KEY", "")
    redirect = "http://localhost:54321/callback"
    return (
        f"{supabase_url}/auth/v1/authorize"
        f"?provider=google"
        f"&redirect_to={redirect}"
    )
```

Load `.env` at CLI startup using `python-dotenv` (add `python-dotenv` to `requirements.txt` if not present).

---

### Step 4.0.8 — JWT Email Decoder

```python
import base64
import json

def decode_jwt_email(token: str) -> str:
    """Extract email from JWT payload without verifying signature."""
    payload_b64 = token.split(".")[1]
    # Pad base64 to a multiple of 4
    payload_b64 += "=" * (4 - len(payload_b64) % 4)
    payload = json.loads(base64.urlsafe_b64decode(payload_b64))
    return payload.get("email", "")
```

---

### Step 4.0.9 — Manual Test Checklist

Run these manually to verify before marking Part 4.0 complete:

1. `python cli/audit_cli.py login` — browser opens, login with NSU account → `✅ Logged in as <name>@northsouth.edu`
2. `python cli/audit_cli.py login` — login with a non-NSU Gmail → `❌ Login failed: only @northsouth.edu accounts are permitted.`
3. `python cli/audit_cli.py l1 data/test_L1_cse_standard.csv BSCSE` — without prior login → `❌ You must be logged in`
4. After login: `python cli/audit_cli.py l1 data/test_L1_cse_standard.csv BSCSE` — runs successfully
5. `python cli/audit_cli.py logout` → `Logged out.`
6. `python cli/audit_cli.py l3 data/test_L3_cse_eligible.csv BSCSE` — after logout → `❌ You must be logged in`

---

## COMPLETION GATE — Part 4.0

Before marking Part 4.0 done and moving to Part 4 (OCR):

- [ ] `cli/credentials.py` created with save / load / delete / is_logged_in / validate_nsu_email
- [ ] `login` command opens browser and handles OAuth callback
- [ ] Non-NSU Gmail login is rejected with clear error message
- [ ] NSU email login saves credentials to `~/.nsu_audit/credentials.json`
- [ ] `logout` command deletes credentials file
- [ ] `l1`, `l2`, `l3` commands all call `require_login()` and block if not logged in
- [ ] All 6 manual test cases above pass
- [ ] `tracking2.md` updated with Part 4.0 items marked ✅
- [ ] `testing_plan2.md` test cases AUTH-1 through AUTH-6 verified

**Present `tracking2.md` to the user. Wait for explicit "go ahead" before starting Part 4 (OCR).**

---

---

# PART 4 — OCR Service

> ⚠️ Do NOT begin until the user has confirmed Part 4.0 is complete.

## TASK: Build the EasyOCR pipeline to extract transcript data from images

### Step 4.1 — OCR Service
Create `backend/services/ocr_service.py`.

#### Step 4.1.0 — PDF Support (do this first, before any other OCR code)

Add `pdf2image` and `poppler-utils` support so users can upload a real NSU transcript PDF directly — not just images.

Add to `backend/requirements.txt`:
```
pdf2image
```

> Note: `pdf2image` requires `poppler` installed on the system.
> - Linux/Railway: `apt-get install poppler-utils`
> - Mac (local dev): `brew install poppler`
> - Add a `apt-packages.txt` or `nixpacks.toml` in the project root for Railway to install it automatically:
>   ```
>   # apt-packages.txt
>   poppler-utils
>   ```

At the very top of `extract_transcript(file_bytes: bytes) -> dict` in `ocr_service.py`, before any OpenCV or EasyOCR code, add this input normalisation block:

```python
import numpy as np
import cv2
from pdf2image import convert_from_bytes
from PIL import Image

def _bytes_to_cv2_image(file_bytes: bytes) -> np.ndarray:
    """
    Accept PDF, JPG, or PNG bytes and always return a cv2 numpy image.
    For PDFs, only the first page is used.
    """
    # Detect PDF by magic bytes
    if file_bytes[:4] == b"%PDF":
        # Convert first page of PDF to PIL Image at 300 DPI for good OCR resolution
        pages = convert_from_bytes(file_bytes, dpi=300, first_page=1, last_page=1)
        pil_image = pages[0]
        # Convert PIL Image → numpy array → BGR for OpenCV
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    else:
        # JPG or PNG — decode directly with OpenCV
        nparr = np.frombuffer(file_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
```

Call `_bytes_to_cv2_image(file_bytes)` as the **first line** of `extract_transcript()`. The returned numpy array is then used for all downstream OpenCV and EasyOCR processing. Nothing else in the pipeline needs to know whether the original input was a PDF or an image.

#### Step 4.1.1 — Two-Column Layout Handling

NSU transcripts use a **two-column layout** (left half and right half of the page, each with its own semester block). The row clustering must account for this:

- After EasyOCR returns all text boxes, split them into **left group** (x-center < page_width / 2) and **right group** (x-center ≥ page_width / 2)
- Cluster rows within each group independently by Y-coordinate (within 10px = same row)
- Process left group rows first (top to bottom), then right group rows (top to bottom)
- Semester header rows (e.g. "Summer 2009", "Fall 2010") reset the current semester label for all rows that follow within that group

#### Step 4.1.2 — Full Pipeline

The complete pipeline for `extract_transcript(file_bytes: bytes) -> dict` must:

1. **Normalise input** — call `_bytes_to_cv2_image(file_bytes)` (handles PDF and images)
2. **Pre-process with OpenCV:**
   - Convert to grayscale
   - Apply adaptive thresholding for contrast
   - Deskew if rotation detected (compute skew angle from Hough lines, rotate to correct)
3. **Run EasyOCR** with English language on the processed image
4. **Split into left/right column groups** based on X-coordinate midpoint (Step 4.1.1)
5. **Cluster by Y-coordinate** within each group — boxes within 10px Y of each other are the same row
6. **Detect semester headers** — if a row contains only a semester string (e.g. `"Spring 2012"`, `"Fall 2009"`), store it as the current semester label; do not treat it as a course row
7. **Map each course row to columns:** `course_code`, `course_name`, `credits`, `grade`, `semester`
   - Use X-position ranges calibrated to the transcript column layout to assign each text box to the correct field
8. **Validate each field:**
   - `course_code`: must match regex `[A-Z]{2,4}\d{3}[A-Z]?`
   - `grade`: must be one of `A, A-, B+, B, B-, C+, C, C-, D+, D, F, I, W, WV, X`
   - `credits`: must be `0`, `1`, `2`, or `3`
9. **Score confidence per row** — average the EasyOCR confidence values of all boxes in the row
10. **Flag low-confidence rows** — if row confidence < 0.70, add to `warnings` list; still include the row in output (do not drop it silently)
11. **Return:**

```python
{
  "rows": [
    {
      "course_code": "EEE141",
      "course_name": "Electrical Circuits",
      "credits": 3,
      "grade": "C",
      "semester": "Summer 2009",
      "confidence": 0.91
    }
  ],
  "csv_text": "course_code,course_name,credits,grade,semester\nEEE141,Electrical Circuits,3,C,Summer 2009\n...",
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
- [ ] `pdf2image` added to `requirements.txt` and `poppler-utils` install documented
- [ ] PDF upload correctly converts first page to image before OCR
- [ ] JPG and PNG uploads still work unchanged
- [ ] Two-column layout correctly parsed — left and right semester blocks both extracted
- [ ] Semester headers correctly detected and attached to following course rows
- [ ] EasyOCR successfully reads a real NSU transcript image/PDF
- [ ] Row parser correctly extracts course_code, course_name, credits, grade, semester
- [ ] Low-confidence rows are flagged in warnings, not silently dropped
- [ ] OCR endpoint works end-to-end for both image and PDF input
- [ ] OCR result feeds into audit engine and produces correct output
- [ ] Tests in `test_ocr.py` pass
- [ ] Update `tracking2.md`

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
