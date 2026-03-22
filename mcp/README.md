# NSU Audit Core — MCP Server

Agentic AI layer for NSU graduation audits. Gives any MCP-compatible LLM client powerful tools to manage graduation audits through natural language.

---

## Prerequisites

- **Python 3.11+**
- **Google Cloud Project** with OAuth2 credentials:
  - Enable Google Drive API and Gmail API
  - Create OAuth 2.0 credentials (Desktop application)
  - Download as `credentials.json`

---

## Installation

```bash
cd mcp
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
# Place credentials.json in the mcp folder
```

---

## Quick Start

```bash
cd mcp
source venv/bin/activate
python mcp_server.py  # First time: opens browser for Google OAuth
```

After first run, token is saved to `~/.nsu_mcp/token.json`.

To force re-authentication:
```bash
python mcp_server.py --reauth
```

---

## Configuration

### Command-Line Options

| Flag | Description |
|------|-------------|
| `--remote` | Use Railway backend instead of offline |
| `--reauth` | Force fresh Google OAuth login |
| `--api-url URL` | Override API URL |
| `--http` | Use HTTP/SSE transport instead of stdio |
| `--http-port PORT` | HTTP port (default: 8001) |

### Files

| File | Location | Purpose |
|------|----------|---------|
| `credentials.json` | `mcp/` | GCP OAuth credentials |
| `token.json` | `~/.nsu_mcp/` | Google OAuth token |
| `history.json` | `~/.nsu_mcp/` | Local audit history |
| `api_token.txt` | `~/.nsu_mcp/` | FastAPI auth token (remote mode) |

---

## MCP Clients

### Claude Desktop

Add to `~/Library/Application Support/Claude/settings.json`:

```json
{
  "mcpServers": {
    "nsu-audit": {
      "command": "python",
      "args": ["/absolute/path/to/mcp/mcp_server.py"]
    }
  }
}
```

### OpenCode

Add to `.opencode/config.json`:

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

## Modes

### Offline Mode (Default)

- Uses embedded audit engine
- No network required after initial OAuth
- Fast, private, works anywhere
- Limited to CSV transcripts (no OCR)

### Remote Mode

```bash
python mcp_server.py --remote
```

- Calls FastAPI backend on Railway
- OCR support for image/PDF transcripts
- History synced to Supabase database

---

## Available Tools

| Tool | Description |
|------|-------------|
| `list_drive_folder` | List files in a Google Drive folder |
| `get_transcript` | Download transcript from Drive |
| `search_drive` | Search Drive by student ID/name |
| `run_audit` | Execute L1/L2/L3 audit |
| `send_email` | Send results via Gmail |
| `get_audit_history` | Query past audits |
| `batch_audit_folder` | Batch process folder |

---

## Example Prompts

1. **"Look at the folder 'NSU Spring 2026 BSCSE', run an L3 audit on every transcript."**

2. **"Find the transcript for student ID 2212345642 and tell me if they can graduate."**

3. **"Show me all L3 audits done last week and list who failed."**

4. **"Audit all transcripts in my Downloads/NSU folder locally."**

5. **"Run a batch audit on the 'Fall 2025 LLB' folder and email results."**

---

## API Token (Remote Mode)

For remote mode, save your API token:

```bash
echo "your-api-token" > ~/.nsu_mcp/api_token.txt
chmod 600 ~/.nsu_mcp/api_token.txt
```

---

## Troubleshooting

### Token Expired
```bash
python mcp_server.py --reauth
```

### Module Not Found
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### MCP Client Not Connecting
- Verify the path in client config is absolute
- Check the MCP server starts successfully first
- Restart the LLM client after starting the server

---

**NSU Audit Core Phase 3 — Agentic MCP Layer**  
CSE226.1 — Vibe Coding | North South University
