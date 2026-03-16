# NSU Audit Core — Phase 3 PRD
## Agentic MCP Layer: The NSU Admin AI Agent

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
