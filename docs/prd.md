# NSU Audit Core — Product Requirements Document

*Combined PRD from Phase 1 and Phase 2*  
*Course: CSE226.1 — Vibe Coding | Instructor: Dr. Nabeel Mohammed*

---

# PART I: Phase 1 — CLI Graduation Audit Engine

**Spring 2026 CSE226.1 - Vibe Coding**  
**Project 1: The Dept. Admin "Audit Core"**  
*Dr. Nabeel Mohammed*  
*Demonstration due: 24th February 2026*

---

## 1. Overview: Building for the Future

In the near future, Department Administration at NSU will be assisted by **Agentic AI**, autonomous assistants capable of handling student queries and graduation checks. However, the agentic systems still need tools to execute tasks.

Your goal in this project is to build the **Audit Engine** that powers this transition. While this version of the project **does not involve AI Integration**, you are developing the "Skill" or "Service" that a future AI Admin Agent would call to verify a student's graduation eligibility. Your product must be precise, handle messy data, and provide clear reports that a future agent could relay to a student or faculty member.

At this stage, your solution should be a tool with a Command Line Interface (CLI) that can be invoked from the terminal.

**Deadline:** February 24th, 2026

---

## 2. Resources & Flexibility

You are provided with two baseline files to build your solution:

- **transcript.csv**: A raw data export of a student's history.
- **program_knowledge.md**: The "Knowledge Base" markdown file structure containing rules and mandatory courses.

**Note about content structure:** You have full flexibility to modify the structure of these files to incorporate the correct information and any semantic meaning you may wish to convey.

---

## 3. Implementation Levels & Marks Breakdown

### Level 1: The Credit Tally Engine (10 Marks)

> **The Task:** Read the student transcript and calculate total valid credits.
> 
> **The Challenge:** A department admin only cares about *earned* credits. You need to decide which grades count and which do not. For example, how should your product treat an "F" versus a "W" or a "0-credit" lab?
> 
> **Required:** Provide a test_L1.csv that proves your solution correctly identifies which credits are valid for graduation.

### Level 2: The Logic Gate & Waiver Handler (10 Marks)

> **The Task:** Calculate weighted CGPA and handle program-specific waivers.
> 
> **The Challenge:** Map letter grades to the NSU scale and handle "state" changes. The interface must ask the Admin: *"Waivers granted for ENG102 or BUS112?"* and adjust the requirements accordingly.
> 
> **Required:** Provide a test_L2.csv that tests your math. You must ensure that non-grade entries (like waivers or withdrawals) do not break your CGPA calculation logic.

### Level 3: The Audit & Deficiency Reporter (10 Marks)

> **The Task:** Compare the student's history against the program.md rules to find missing requirements.
> 
> **The Challenge:** An Admin Agent must be able to tell a student *exactly* why they can't graduate. Your service should identify missing mandatory courses and flag "Probation" status (CGPA < 2.0).
> 
> **Required:** Provide a **"Retake Scenario"** data file. If a student attempts a course multiple times, how does your product ensure the admin gets an accurate picture of their progress?

---

## 4. Deliverables

1. **The tool:** Functional CLI scripts, one per implementation level, that an Admin could run to process a student.
2. **Your Knowledge Files:** Your optimized versions of the .csv and your program knowledge file.
3. **Your Custom Test Cases:** The specific data files (test_L1.csv, test_L2.csv, etc.) that you designed to prove the product is robust enough for a future Agentic AI.

---

## 5. Supported Programs

The system supports three NSU programs:

1. **BSCSE** — Bachelor of Science in Computer Science & Engineering
2. **BSEEE** — Bachelor of Science in Electrical & Electronic Engineering
3. **LL.B Honors** — Bachelor of Law

---

# PART II: Phase 2 — Full-Stack Multi-Client Service

**Version 2.0 | Due: March 8, 2026**

---

## 1. Overview

Phase 1 delivered a robust CLI-based graduation audit engine for NSU's three programs. Phase 2 evolves that engine into a **full-stack, multi-client service** — accessible via Web App, Mobile App (Flutter), and CLI — backed by a shared cloud database, Google Authentication, OCR-powered transcript ingestion, and a scan history system.

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
          │   users | profiles | scans              │
          └─────────────────────────────────────────┘
```

---

## 5. Database Schema

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

---

## 6. API Endpoints

Base URL: `https://nsu-audit-api.railway.app`

### Health
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | None | API health check |

### Audit
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/audit/csv` | Required | Upload CSV, run audit (L1/L2/L3) |
| POST | `/api/v1/audit/ocr` | Required | Upload image, run OCR then audit |
| GET | `/api/v1/audit/{scan_id}` | Required | Get a specific scan result |

### History
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/history` | Required | Get current user's scan history |
| GET | `/api/v1/history/{user_id}` | Admin only | Get any user's scan history |
| DELETE | `/api/v1/history/{scan_id}` | Required | Delete a scan (own only) |

### Users (Admin only)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/users` | Admin | List all users |
| PATCH | `/api/v1/users/{id}/role` | Admin | Change user role |

---

## 7. Feature Requirements

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

## 8. Non-Functional Requirements

### NFR-1: Concurrency
- Minimum 20 concurrent users supported without degradation
- Load test must verify this with Locust
- Target: P95 response time < 5s for CSV audit, < 15s for OCR audit

### NFR-2: Code Quality
- All Python code passes `flake8` and `black` formatting check
- Pre-commit hooks block commits that fail linting
- GitHub Actions runs tests + lint on every push to `master`

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

## 9. Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | FastAPI backend | Deployed on Railway, full audit + OCR + history API |
| 2 | React Web App | Deployed on Vercel, all 5 pages functional |
| 3 | Flutter Mobile App | APK + iOS build, Google auth + OCR + history |
| 4 | Updated CLI | `audit-cli` with `--remote`, `login`, `history` |
| 5 | Supabase setup | DB schema, RLS policies, Google OAuth configured |
| 6 | GitHub Actions CI | Lint + test pipeline passing on main |
| 7 | Locust load test | Report showing 20 concurrent users passed |
| 8 | README | Full setup and run instructions |

---

## 10. Timeline (6 days to March 8)

| Day | Focus |
|-----|-------|
| Day 1 (Mar 3) | Supabase setup, DB schema, Google OAuth, FastAPI skeleton |
| Day 2 (Mar 4) | Audit service (wraps Phase 1), OCR service, core API routes |
| Day 3 (Mar 5) | Scan history routes, auth middleware, CLI updates |
| Day 4 (Mar 6) | React Web App (all pages, Supabase auth) |
| Day 5 (Mar 7) | Flutter Mobile App (login, upload, history) |
| Day 6 (Mar 8) | CI/CD pipeline, load testing, bugfixes, deployment |

---

## 11. Out of Scope (Phase 2)

- AI model integration (planned for Phase 3)
- Prerequisite graph visualization
- Email notifications
- Offline mobile mode
- Student self-service portal (admin-only for now)

---

# PART III: Phase 3 — Agentic MCP Layer
**The NSU Admin AI Agent**

**Version 3.0**
**Course: CSE226.1 — Vibe Coding | Instructor: Dr. Nabeel Mohammed**
**Author: Rafiur Rahman Mashrafi**

---

## 1. Vision

> *"In the near future, Department Administration at NSU will be assisted by Agentic AI."*
> — Phase 1 PRD

Phase 3 makes that sentence real.

Phase 1 built the audit engine. Phase 2 wrapped it in a REST API with auth, OCR, and a web/mobile/CLI frontend. Phase 3 adds the **AI Agent layer** — a local MCP (Model Context Protocol) server that gives any LLM client a set of powerful tools so an NSU admin can manage graduation audits entirely through natural language.

**The admin types once. The agent does everything.**

---

## 2. Goals

| Goal | Description |
|------|-------------|
| **MCP Server** | Local Python MCP server (stdio transport) with 7 tools |
| **Google Drive Integration** | Browse and download transcripts from admin's personal Drive |
| **Audit Engine Bridge** | Call the existing FastAPI backend (remote) OR run Phase 1 logic locally (offline) |
| **Gmail Integration** | Send formatted audit result emails via Gmail API |
| **Universal Compatibility** | Works with Claude Desktop, OpenCode, Gemini CLI, or any MCP-compatible host |
| **OAuth2 Auth** | One-time browser login for Google; token saved locally for all future use |
| **Dual Mode** | `--remote` flag to sync with Railway backend; default is offline using embedded Phase 1 engine |

---

## 3. Audience

**Primary user:** NSU Department Admin (not students).

The admin runs this MCP server locally on their machine and connects it to their preferred LLM client. They interact only through natural language — no coding, no manual file handling.

---

## 4. How It Works (The Agentic Loop)

```
Admin (natural language prompt)
         │
         ▼
┌──────────────────────────────────┐
│      LLM Client (MCP Host)       │  ← Claude Desktop / OpenCode /
│                                  │    Gemini CLI / any MCP host
└──────────────┬───────────────────┘
               │  MCP stdio transport
               ▼
┌──────────────────────────────────────────────────────────┐
│             NSU MCP Server  (local Python)               │
│                                                          │
│  list_drive_folder   get_transcript    run_audit         │
│  send_email          search_drive      get_audit_history │
│  batch_audit_folder                                      │
└────────┬──────────────────────┬───────────────┬──────────┘
         │                      │               │
         ▼                      ▼               ▼
  Google Drive API      FastAPI Backend    Gmail API
  (Admin's Drive)    (Railway — optional)  (Admin's Gmail)
         │                      │
         │              Phase 1 Engine
         │              (embedded — offline mode)
```

### Example Agentic Conversations

**Scenario 1 — Batch Audit & Email**
> *"Look at the folder 'NSU Spring 2026 BSCSE', run an L3 audit on every transcript, and email each result to the student's NSU email."*

Agent flow: `list_drive_folder` → loop: `get_transcript` → `run_audit` → `send_email`

**Scenario 2 — Single Student Check**
> *"Find the transcript for student ID 2212345642 and tell me if they can graduate under BSCSE."*

Agent flow: `search_drive` → `get_transcript` → `run_audit`

**Scenario 3 — History Inquiry**
> *"Show me all L3 audits done last week and list who failed."*

Agent flow: `get_audit_history` (with date filter)

**Scenario 4 — Offline Batch**
> *"I'm on a plane. Audit all transcripts in my Downloads/NSU folder locally and give me a summary."*

Agent uses offline mode (embedded Phase 1 engine, no network needed).

---

## 5. MCP Tools Specification

### Tool 1: `list_drive_folder`

**Description:** Lists all transcript files (CSV, image, PDF) inside a specified Google Drive folder.

**Input parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder_name` | string | Yes | Name of the Drive folder to search |
| `file_types` | list[string] | No | Filter by type, e.g. `["csv", "png", "pdf"]`. Default: all |

**Returns:** List of objects with `file_id`, `file_name`, `mime_type`, `modified_date`, `size`.

**Error cases:** Folder not found, Drive auth expired, no files matching filter.

---

### Tool 2: `get_transcript`

**Description:** Downloads a transcript file from Google Drive and returns its content ready for auditing. Handles CSV (returns raw text) and images/PDFs (returns base64 for OCR pipeline).

**Input parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_id` | string | Yes | Drive file ID from `list_drive_folder` |
| `file_name` | string | No | Human-readable name for logging |

**Returns:** Object with `file_id`, `file_name`, `content_type` (`csv` or `image`), `content` (raw CSV text or base64 string), `size_bytes`.

---

### Tool 3: `run_audit`

**Description:** Runs an L1, L2, or L3 graduation audit on a transcript. Operates in two modes controlled by the `--remote` server flag:
- **Offline (default):** Uses the embedded Phase 1 Python engine directly.
- **Remote:** POSTs to the FastAPI backend on Railway.

**Input parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `transcript_content` | string | Yes | Raw CSV text (from `get_transcript`) |
| `program` | string | Yes | `BSCSE`, `BSEEE`, or `LLB` |
| `audit_level` | integer | Yes | `1`, `2`, or `3` |
| `waivers` | list[string] | No | e.g. `["ENG102", "BUS112"]` |
| `student_email` | string | No | Stored in result for use by `send_email` |

**Returns:** Full audit result object with `student_id`, `program`, `audit_level`, `cgpa`, `total_credits`, `eligible` (bool), `deficiencies` (list), `result_text` (formatted plain-text report), `result_json` (structured data).

---

### Tool 4: `send_email`

**Description:** Sends a formatted audit result email via Gmail API. Automatically formats the email body from an audit result object.

**Input parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `to` | string | Yes | Recipient email address |
| `subject` | string | No | Default: `"NSU Graduation Audit Result — {student_id}"` |
| `audit_result` | object | Yes | The result object returned by `run_audit` |
| `cc` | string | No | Optional CC address (e.g. dept chair) |
| `include_full_report` | boolean | No | Attach formatted text report. Default: `true` |

**Returns:** Object with `message_id`, `status`, `sent_at`, `recipient`.

---

### Tool 5: `search_drive`

**Description:** Finds a specific student's transcript file in Drive by student ID, name, or keyword. Useful when the admin doesn't know the exact folder structure.

**Input parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Student ID, name, or filename keyword |
| `folder_name` | string | No | Limit search to a specific folder |

**Returns:** List of matching files (same schema as `list_drive_folder`). Empty list if none found.

---

### Tool 6: `get_audit_history`

**Description:** Retrieves past audit records. In remote mode, fetches from the Supabase DB via the FastAPI backend. In offline mode, reads from a local JSON log file (`~/.nsu_mcp/history.json`) maintained by the MCP server itself.

**Input parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Max records to return. Default: `20` |
| `program` | string | No | Filter by program |
| `audit_level` | integer | No | Filter by level |
| `eligible_only` | boolean | No | If `true`, return only eligible students |
| `since` | string | No | ISO date string, e.g. `"2026-03-01"` |

**Returns:** List of audit summary objects with `scan_id`, `student_id`, `program`, `audit_level`, `cgpa`, `eligible`, `created_at`.

---

### Tool 7: `batch_audit_folder`

**Description:** High-level compound tool — lists a folder, downloads all transcripts, audits each one, and optionally emails results. This is the "do everything" tool for bulk workflows. Internally chains tools 1 → 2 → 3 → (optionally) 4.

**Input parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder_name` | string | Yes | Drive folder containing transcripts |
| `program` | string | Yes | `BSCSE`, `BSEEE`, or `LLB` |
| `audit_level` | integer | Yes | `1`, `2`, or `3` |
| `send_emails` | boolean | No | If `true`, email each result. Default: `false` |
| `email_domain` | string | No | Domain to construct student emails, e.g. `"northsouth.edu"` |
| `waivers` | list[string] | No | Applied to all audits in the batch |

**Returns:** Batch summary with `total_processed`, `eligible_count`, `ineligible_count`, `errors`, and a `results` list (one entry per student). Streams progress updates to the LLM as each file is processed.

---

## 6. Authentication Design

### Google OAuth2 (Drive + Gmail)

The MCP server uses a single OAuth2 credential for both Google Drive and Gmail access. Scopes required:
- `https://www.googleapis.com/auth/drive.readonly`
- `https://www.googleapis.com/auth/gmail.send`

**First-run flow:**
1. Admin runs `python mcp_server.py` for the first time.
2. Server detects no saved token at `~/.nsu_mcp/token.json`.
3. Browser opens automatically to Google's OAuth consent screen.
4. Admin logs in with their NSU Google account.
5. Token saved to `~/.nsu_mcp/token.json` (encrypted with system keyring or plain JSON with a warning).
6. All future runs load the token silently. Refresh tokens are handled automatically.

**Re-auth:** Admin can run `python mcp_server.py --reauth` to force a fresh login.

### FastAPI Backend Auth (Remote Mode)

In `--remote` mode, the MCP server authenticates against the existing FastAPI backend using a long-lived API token (admin generates once from the web app settings page). Stored at `~/.nsu_mcp/api_token.txt`.

---

## 7. Project Structure

```
nsu-audit-core/
├── mcp/                          # Phase 3 — NEW
│   ├── mcp_server.py             # Entry point, server registration
│   ├── config.py                 # Config: remote/offline mode, paths
│   ├── auth/
│   │   ├── google_oauth.py       # OAuth2 flow, token management
│   │   └── api_auth.py           # FastAPI token auth (remote mode)
│   ├── tools/
│   │   ├── drive_tools.py        # list_drive_folder, get_transcript, search_drive
│   │   ├── audit_tools.py        # run_audit (offline + remote)
│   │   ├── email_tools.py        # send_email via Gmail API
│   │   ├── history_tools.py      # get_audit_history
│   │   └── batch_tools.py        # batch_audit_folder
│   ├── offline/
│   │   └── engine_bridge.py      # Imports Phase 1 core audit engine
│   ├── history/
│   │   └── local_log.py          # Local JSON history for offline mode
│   ├── requirements.txt
│   └── README.md                 # MCP setup instructions per LLM client
├── backend/                      # Phase 2 (unchanged)
├── frontend/                     # Phase 2 (unchanged)
├── mobile/                       # Phase 2 (unchanged)
├── cli/                          # Phase 2 (unchanged)
└── core/                         # Phase 1 engine (reused by mcp/offline/)
```

---

## 8. MCP Client Configuration

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "nsu-audit": {
      "command": "python",
      "args": ["/path/to/nsu-audit-core/mcp/mcp_server.py"],
      "env": {}
    }
  }
}
```

For remote mode:
```json
{
  "mcpServers": {
    "nsu-audit": {
      "command": "python",
      "args": [
        "/path/to/nsu-audit-core/mcp/mcp_server.py",
        "--remote",
        "--api-url", "https://nsu-audit-api.railway.app"
      ]
    }
  }
}
```

### OpenCode / Gemini CLI

Same `stdio` transport. Add to the respective config file (`.opencode/config.json` or `~/.config/gemini-cli/mcp.json`):

```json
{
  "mcpServers": [
    {
      "name": "nsu-audit",
      "command": "python /path/to/mcp/mcp_server.py"
    }
  ]
}
```

---

## 9. Feature Requirements

### FR-3.1: MCP Server Foundation
- FR-3.1.1: Implement using the `mcp` Python SDK with `stdio` transport
- FR-3.1.2: Server must start cleanly with `python mcp_server.py`
- FR-3.1.3: All 7 tools must be registered and discoverable by any MCP host
- FR-3.1.4: `--remote` flag switches audit and history tools to use the Railway backend
- FR-3.1.5: Graceful error messages for all tool failures (no raw stack traces to LLM)

### FR-3.2: Google Drive Tools
- FR-3.2.1: OAuth2 browser login on first run, token persisted locally
- FR-3.2.2: `list_drive_folder` returns files with metadata
- FR-3.2.3: `get_transcript` downloads CSV and image files
- FR-3.2.4: `search_drive` supports fuzzy filename search
- FR-3.2.5: Handle Drive API rate limits with exponential backoff

### FR-3.3: Audit Tool
- FR-3.3.1: Offline mode must use the Phase 1 `core/` engine directly (no HTTP)
- FR-3.3.2: Remote mode must call `POST /api/v1/audit/csv` on the Railway backend
- FR-3.3.3: Result must include both `result_text` (human-readable) and `result_json` (structured)
- FR-3.3.4: Image transcripts must be sent to `POST /api/v1/audit/ocr` in remote mode; in offline mode, warn that OCR requires remote mode

### FR-3.4: Email Tool
- FR-3.4.1: Use Gmail API with OAuth2 (same token as Drive)
- FR-3.4.2: Email body must be formatted clearly: student ID, program, CGPA, eligibility status, deficiencies list
- FR-3.4.3: Plain-text email body (no HTML required for v1)
- FR-3.4.4: Log all sent emails to local history

### FR-3.5: Batch Tool
- FR-3.5.1: Stream progress updates per file (LLM sees "Processing file 3/12...")
- FR-3.5.2: Continue batch even if individual files fail (log errors, don't abort)
- FR-3.5.3: Return summary counts at the end

### FR-3.6: History Tool
- FR-3.6.1: Offline mode reads/writes `~/.nsu_mcp/history.json`
- FR-3.6.2: Remote mode calls `GET /api/v1/history` on the FastAPI backend
- FR-3.6.3: Support filtering by date, program, level, and eligibility

---

## 10. Non-Functional Requirements

| # | Requirement | Target |
|---|-------------|--------|
| NFR-3.1 | MCP server startup time | < 3 seconds |
| NFR-3.2 | Single audit latency (offline) | < 2 seconds |
| NFR-3.3 | Single audit latency (remote) | < 5 seconds |
| NFR-3.4 | Batch audit throughput | ≥ 5 students/minute (remote) |
| NFR-3.5 | Token refresh | Automatic, no admin intervention |
| NFR-3.6 | Error handling | All tool errors return structured MCP error objects, never crash the server |
| NFR-3.7 | Credentials security | OAuth token at `~/.nsu_mcp/` with `600` file permissions; never logged or printed |

---

## 11. Tech Stack

| Component | Technology |
|-----------|-----------|
| MCP Framework | `mcp` Python SDK (official Anthropic SDK) |
| Google Drive | `google-api-python-client` + `google-auth-oauthlib` |
| Gmail | `google-api-python-client` (Gmail API v1) |
| Transport | `stdio` (universal MCP transport) |
| Offline Engine | Phase 1 `core/` module (direct Python import) |
| Remote Client | `httpx` (async HTTP to FastAPI backend) |
| Local History | Plain JSON at `~/.nsu_mcp/history.json` |
| Dev-time Docs | context7 MCP (for `mcp` SDK + Google API docs lookup) |

---

## 12. Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | `mcp/mcp_server.py` | Working MCP server with all 7 tools registered |
| 2 | `mcp/requirements.txt` | All Python dependencies |
| 3 | `mcp/README.md` | Setup guide for Claude Desktop, OpenCode, Gemini CLI |
| 4 | Google OAuth credentials | Setup instructions (admin creates their own GCP project) |
| 5 | Sample prompts doc | 10 example natural language prompts the admin can use |
| 6 | Integration test | Script that exercises all 7 tools against mock data |

---

## 13. Out of Scope (Phase 3)

- Web UI for the MCP server
- Student-facing MCP access (admin only)
- WhatsApp / Telegram bot interface
- Multi-admin shared MCP deployment
- Prerequisite graph visualization
- HTML email formatting (plain-text only for v1)

---

## 14. Suggested Development Order

| Step | Task |
|------|------|
| 1 | Set up MCP server skeleton (`mcp_server.py`) with one dummy tool |
| 2 | Wire up Google OAuth2 flow, test Drive listing |
| 3 | Implement `list_drive_folder` + `get_transcript` |
| 4 | Implement `run_audit` (offline mode first, then remote) |
| 5 | Implement `send_email` via Gmail API |
| 6 | Implement `search_drive` + `get_audit_history` |
| 7 | Implement `batch_audit_folder` |
| 8 | Test full chain in Claude Desktop |
| 9 | Test in OpenCode CLI |
| 10 | Write README + sample prompts doc |

---

*NSU Audit Core Phase 3 — Agentic MCP Layer*
*CSE226.1 — Vibe Coding | North South University*
