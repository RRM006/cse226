# Assumptions Log — Phase 2
**NSU Audit Core | CSE226.1**
All assumptions made during Phase 2 must be logged here immediately.

---

## Format

```
## Assumption #N — [Part / Step]
**Context:** What situation triggered this assumption
**Assumption:** What was assumed
**Reason:** Why assumed instead of asking
**Impact:** What changes if this assumption is wrong
**Source:** [OpenCode assumption / User clarification]
```

---

## Pre-logged Assumptions (from PRD and user notes)

---

## Assumption #1 — Architecture / Tech Stack

**Context:** User specified the full tech stack in their notes.
**Assumption:** FastAPI (backend), EasyOCR (OCR), Supabase PostgreSQL (DB + Auth), React + Vite (web), Flutter (mobile), Railway (backend hosting), Vercel (frontend hosting), GitHub Actions + pre-commit (CI/CD), Locust (load testing).
**Reason:** Explicitly stated by user.
**Impact:** None — user confirmed this stack.
**Source:** User clarification

---

## Assumption #2 — Phase 1 Engine Reuse

**Context:** User said "Reuse the audit logic from Phase 1 scripts as core engine."
**Assumption:** The three Python scripts (`level1_credit_tally.py`, `level2_cgpa_calculator.py`, `level3_audit_engine.py`) will be copied into `backend/core/` and refactored to remove `print()` and `input()` calls, replacing them with return values and parameters — but the core audit logic will not be changed.
**Reason:** User explicitly required reuse, not a rewrite.
**Impact:** If Phase 1 logic has bugs, they carry into Phase 2. Any logic bug fix should be done in `backend/core/` and backported.
**Source:** User clarification

---

## Assumption #3 — OCR: No AI API

**Context:** User explicitly said "OCR use korte hbe, ai lagbeh nah" (OCR must be used, no AI needed) and "OCR libraries."
**Assumption:** EasyOCR (pure Python library) is used for all transcript image reading. No calls to OpenAI Vision, Google Vision API, or any other AI service.
**Reason:** User explicitly required this.
**Impact:** OCR accuracy may be lower on very poor quality images. This is acceptable per requirements.
**Source:** User clarification

---

## Assumption #4 — Concurrent Users

**Context:** User said "work with a minimum of 20 concurrent users (max)."
**Assumption:** "20 concurrent users" means 20 simultaneous active HTTP connections hitting the API. Locust load test will simulate exactly 20 users. The system does not need to handle more than 20 at this stage.
**Reason:** User specified 20 as both min and max for this phase.
**Impact:** Scaling beyond 20 is out of scope for Phase 2.
**Source:** User clarification

---

## Assumption #5 — User Roles

**Context:** User said "User Roles: Admin + Student."
**Assumption:** Two roles only: `admin` and `student`. All new Google sign-ups default to `student`. Admin role is assigned manually (via Supabase dashboard or API). There is no self-registration as admin.
**Reason:** User explicitly defined both roles and their access.
**Impact:** If a third role is needed later, schema change required.
**Source:** User clarification

---

## Assumption #6 — Scan History Scope

**Context:** User said "history of all past transcript scans/calls that happened for a specific account."
**Assumption:** History is per-user account (Google OAuth identity). A student sees only their own history. An admin sees all users' history. History is never deleted automatically — only manually by the user or admin.
**Reason:** Standard audit trail behavior.
**Impact:** Storage grows unboundedly; not a concern at this scale.
**Source:** User clarification + OpenCode assumption

---

## Assumption #7 — CLI Backward Compatibility

**Context:** Phase 1 CLI must continue to work. Phase 2 adds new flags.
**Assumption:** The Phase 1 CLI commands work exactly as before without any auth or network requirement (pure offline mode). New flags `--remote`, `login`, `logout`, `history` are additive. If `--remote` is not passed, no API calls are made.
**Reason:** Must not break existing Phase 1 demo.
**Impact:** None — purely additive.
**Source:** OpenCode assumption

---

## Assumption #8 — Database: Supabase Free Tier Limits

**Context:** User specified Supabase free tier.
**Assumption:** Free tier limits (500MB DB, 50MB file storage, 50,000 monthly active users) are sufficient for a class project with max 20 users. No file storage is used — CSV and OCR text are stored as text in the DB, not as files.
**Reason:** Free tier is sufficient for this project scope.
**Impact:** If image blobs need to be stored, Supabase Storage would be needed (also free tier available).
**Source:** OpenCode assumption

---

## Assumption #9 — OCR Input Formats

**Context:** User said "scan official nsu transcript or image should be uploaded scanned and work."
**Assumption:** Accepted image formats: JPG, PNG. PDF accepted (first page only extracted). No multi-page PDF processing. Maximum file size: 10MB.
**Reason:** EasyOCR works natively with image formats. PDF → image conversion uses pdf2image/poppler.
**Impact:** Multi-page transcripts in PDF would only have first page processed. If this is an issue, user must upload as image.
**Source:** OpenCode assumption

---

## Assumption #10 — Waivers in API

**Context:** Phase 1 CLI prompts admin interactively for waivers. Phase 2 is an API.
**Assumption:** In the API, waivers are passed as an optional comma-separated string field in the form data (e.g., `waivers=ENG102,MAT116`). If not provided, no waivers are applied. There is no interactive prompt in the API.
**Reason:** REST APIs cannot have interactive prompts. Waivers must be a request parameter.
**Impact:** The web/mobile/CLI clients are responsible for asking the user about waivers before submitting.
**Source:** OpenCode assumption

---

## Assumption #11 — JWT Validation Strategy

**Context:** FastAPI needs to validate Supabase JWTs.
**Assumption:** JWT validation is done by verifying the token's signature against Supabase's JWKS endpoint (`https://<project>.supabase.co/auth/v1/.well-known/jwks.json`). The `python-jose` library is used for this. The user's role is read from the `profiles` table on each request (not stored in JWT).
**Reason:** Standard Supabase JWT validation approach.
**Impact:** Each authenticated request makes one DB call to fetch the user's role. Acceptable at this scale.
**Source:** OpenCode assumption

---

## Assumption #12 — Program Knowledge Files Location

**Context:** Phase 1 uses program knowledge `.md` files. Phase 2 API needs them.
**Assumption:** The three program knowledge files are bundled inside the backend (`backend/data/programs/`). The API uses the `program` parameter to select the correct file. Users do not upload their own knowledge files via the API.
**Reason:** Program requirements are institutional — they should not be user-modifiable.
**Impact:** Updating program requirements requires a backend code deployment.
**Source:** OpenCode assumption

---

## Assumption #13 — Flutter Target Platforms

**Context:** User said "mobile app."
**Assumption:** Flutter app targets Android primarily (APK for demo). iOS build attempted if time permits. No web build of the Flutter app (separate React app handles web).
**Reason:** Android APK is faster to demo. iOS requires a Mac + developer account.
**Impact:** iOS users must use the web app until iOS build is done.
**Source:** OpenCode assumption

---

## Assumption #14 — Load Test JWT

**Context:** Locust load test requires authenticated API calls.
**Assumption:** A dedicated test user account is created in Supabase. Its JWT is hardcoded in `locustfile.py` (not committed to git — loaded from env). This JWT is refreshed before each test run.
**Reason:** Load testing 20 users with 20 different real Google OAuth flows is impractical.
**Impact:** Load test uses a single account's JWT for all virtual users. This tests concurrency at the API/DB level, not at the auth level.
**Source:** OpenCode assumption

---

## Assumption #15 — CI/CD Deployment Triggers

**Context:** GitHub Actions CI pipeline.
**Assumption:** Tests run on every push and PR. Auto-deploy to Railway and Vercel only triggers on pushes to `main`. PRs do not trigger deployment.
**Reason:** Standard CI/CD practice to avoid deploying unreviewed code.
**Impact:** None.
**Source:** OpenCode assumption

---

*Add new assumptions below as they arise during development.*

---

## New Assumptions (add here during build)

## Assumption #16 — API Return Structure for Phase 1 Engine
**Context:** Refactoring Phase 1 scripts to be callable by FastAPI.
**Assumption:** The core Phase 1 scripts use `io.StringIO` to capture `print()` output rather than rewriting the core visualization logic. They return a `result_text` property for the textual report and a simplified `result_json` object matching the API requirements.
**Reason:** Rewriting the entire `print_audit_output` function to return purely structured JSON was too intrusive to the Phase 1 engine, and the visual output format still needs to be preserved for the frontend/mobile apps to display.
**Impact:** Apps display the raw `result_text` log alongside the parsed `summary` details.
**Source:** OpenCode assumption.

## Assumption #17 — Knowledge File Loading in API
**Context:** The Level 3 engine needs program knowledge files.
**Assumption:** The `knowledge_file_content` is passed as a string from the router to the core engine, instead of having the engine read directly from a file path. The API router determines the file path and reads it.
**Reason:** Easier dependency injection, cleaner testing, and better separation of concerns between API logic and core engine logic.
**Impact:** Minimal impact, just centralizes file IO in the router layer.
**Source:** OpenCode assumption.

## Assumption #18 — OCR Row Parsing Strategy
**Context:** EasyOCR returns raw text with bounding boxes, need to map to transcript table rows.
**Assumption:** Rows are detected by clustering text elements with similar Y-coordinates (within 15px tolerance). Columns are mapped by X-coordinate position: course_code (left), course_name (middle), credits (right-middle), grade (right), semester (far right).
**Reason:** Standard table extraction approach for OCR output.
**Impact:** May need tuning if transcript layout differs significantly from expected format.
**Source:** OpenCode assumption.

## Assumption #19 — OCR Course Code Pattern
**Context:** Need to validate extracted course codes.
**Assumption:** Course codes follow pattern: 2-4 uppercase letters followed by 3 digits (e.g., CSE115, ENG102, MAT116). Regex: `^[A-Z]{2,4}\d{3}$`.
**Reason:** Based on Phase 1 code showing courses like ENG102, MAT116, CSE115.
**Impact:** Non-standard course codes will be flagged as warnings.
**Source:** OpenCode assumption.

## Assumption #20 — OCR Row Detection Strategy
**Context:** EasyOCR returns individual word bounding boxes, not full rows.
**Assumption:** Rows are detected by finding text that matches course code pattern, then grouping nearby text elements on the same Y-coordinate (within 20px tolerance). Course code is used as anchor, other fields extracted from adjacent text.
**Reason:** More robust than clustering all text - focuses on identifiable course codes.
**Impact:** May miss rows with unreadable course codes but reduces false positives.
**Source:** OpenCode assumption.

## Assumption #21 — OCR Confidence Rules
**Context:** PRD specifies confidence thresholds for OCR output.
**Assumption:**
- Row confidence ≥ 0.85 → accepted as-is
- Row confidence 0.70–0.84 → accepted with warning flagged
- Row confidence < 0.70 → row excluded from output
- Overall average confidence < 0.60 → API returns 422 error
**Reason:** Per PRD Section 8 requirements.
**Impact:** Users with poor quality images must re-upload clearer versions.
**Source:** PRD requirement.
