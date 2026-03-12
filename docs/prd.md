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
