# NSU Audit Core — MCP Server

Agentic AI layer for NSU graduation audits. Gives any MCP-compatible LLM client powerful tools to manage graduation audits through natural language.

---

## 1. Prerequisites

- **Python 3.11+**
- **Google Cloud Project** with OAuth2 credentials:
  - Enable Google Drive API
  - Enable Gmail API
  - Create OAuth 2.0 credentials (Desktop application)
  - Download as `credentials.json`

---

## 2. Installation

```bash
# Navigate to MCP directory
cd mcp

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Place your credentials.json in the mcp folder
# (get from Google Cloud Console)
```

---

## 3. First-Run Authentication

```bash
python mcp_server.py
```

On first run:
1. Browser opens to Google OAuth consent screen
2. Login with your NSU Google account
3. Token saved to `~/.nsu_mcp/token.json`
4. All future runs load token silently

To force re-authentication:
```bash
python mcp_server.py --reauth
```

---

## 4. Configuration

### Command-Line Options

| Flag | Description | Default |
|------|-------------|---------|
| `--remote` | Use Railway backend instead of offline | `False` |
| `--reauth` | Force fresh Google OAuth login | `False` |
| `--api-url` | Override Railway API URL | `https://nsu-audit-api.railway.app` |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `RAILWAY_API_URL` | FastAPI backend URL (remote mode) |

### Files

| File | Location | Purpose |
|------|----------|---------|
| `token.json` | `~/.nsu_mcp/` | Google OAuth token |
| `credentials.json` | `mcp/` | GCP OAuth credentials |
| `history.json` | `~/.nsu_mcp/` | Local audit history |
| `api_token.txt` | `~/.nsu_mcp/` | FastAPI auth token (remote mode) |

---

## 5. Client Setup

### Claude Desktop

Add to `~/Library/Application Support/Claude/settings.json`:

```json
{
  "mcpServers": {
    "nsu-audit": {
      "command": "python",
      "args": ["/absolute/path/to/mcp/mcp_server.py"],
      "env": {}
    }
  }
}
```

### OpenCode

Add to `.opencode/config.json` (or create if not exists):

```json
{
  "mcpServers": [
    {
      "name": "nsu-audit",
      "command": "python /absolute/path/to/mcp/mcp_server.py"
    }
  ]
}
```

### Gemini CLI

Add to `~/.config/gemini-cli/mcp.json`:

```json
{
  "mcpServers": [
    {
      "name": "nsu-audit",
      "command": "python /absolute/path/to/mcp/mcp_server.py"
    }
  ]
}
```

---

## 6. Offline Mode vs Remote Mode

### Offline Mode (Default)

- Uses embedded Phase 1 audit engine
- No network required after initial OAuth
- Fast, private, works anywhere
- Limited to CSV transcripts (no OCR)

**Use when:**
- Working offline or on a plane
- Quick audits during meetings
- Privacy-sensitive operations

### Remote Mode

```bash
python mcp_server.py --remote
```

- Calls FastAPI backend on Railway
- OCR support for image/PDF transcripts
- History synced to Supabase database
- Requires API token setup

**Use when:**
- Processing image transcripts (photos of transcripts)
- Need centralized history across devices
- Using advanced audit features

---

## 7. Example Natural Language Prompts

Here are 10 prompts the admin can use:

1. **"Look at the folder 'NSU Spring 2026 BSCSE', run an L3 audit on every transcript, and email each result to the student's NSU email."**

2. **"Find the transcript for student ID 2212345642 and tell me if they can graduate under BSCSE."**

3. **"Show me all L3 audits done last week and list who failed."**

4. **"I'm on a plane. Audit all transcripts in my Downloads/NSU folder locally and give me a summary."**

5. **"Run a batch audit on the 'Fall 2025 LLB' folder, level 2, and send emails to all eligible students."**

6. **"Search my Drive for any files containing '2212345' and audit them."**

7. **"What's the average CGPA of all BSCSE students who passed the L3 audit this month?"**

8. **"List all files in my 'Pending Audit' folder and tell me which ones are missing the capstone course."**

9. **"Audit student 2212345678 with BSEEE program, level 3, and waive ENG102."**

10. **"Show me the full history of all audits done for the LLB program this semester."**

---

## 8. Saving the API Token (Remote Mode)

For remote mode, you need an API token from the FastAPI web app:

1. Go to the NSU Audit web application
2. Navigate to Settings / API Access
3. Generate a new API token
4. Save to `~/.nsu_mcp/api_token.txt`:

```bash
echo "your-api-token-here" > ~/.nsu_mcp/api_token.txt
chmod 600 ~/.nsu_mcp/api_token.txt
```

---

## 9. Troubleshooting

### Token Expired

```
Error: Token expired
```

**Fix:** Run with `--reauth` to get a fresh token:
```bash
python mcp_server.py --reauth
```

### Folder Not Found

```
Folder 'My Folder' not found in Drive
```

**Fix:** 
- Check the exact folder name in Google Drive
- Make sure the folder is in the admin's Drive (not shared drives)
- Case-sensitive search

### Gmail Quota Exceeded

```
Quota exceeded for Gmail API
```

**Fix:**
- Wait for quota reset (typically 24 hours)
- Use batch mode sparingly
- Check Google Cloud Console for your quota limits

### No CSV Files Found

```
No CSV files found in folder
```

**Fix:**
- Ensure transcripts are exported as CSV, not Excel
- Check file types: `list_drive_folder('folder', ['csv'])`

### Import Errors

```
ModuleNotFoundError: No module named 'google'
```

**Fix:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### MCP Client Not Connecting

**Fix:**
- Verify the path in client config is absolute (not relative)
- Check the MCP server starts successfully in terminal first
- Restart the LLM client after starting the server

---

## Quick Start

```bash
cd mcp
source venv/bin/activate

# First time: authenticate with Google
python mcp_server.py

# In another terminal or your LLM client:
# "List files in my 'NSU Transcripts' folder"
```

---

**NSU Audit Core Phase 3 — Agentic MCP Layer**
**CSE226.1 — Vibe Coding | North South University**
