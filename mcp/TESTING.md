# NSU Audit MCP - Testing Guide

This guide explains how to set up, run, and test the MCP server.

---

## 1. Setup Prerequisites

### Step 1: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable APIs:
   - Google Drive API
   - Gmail API
4. Go to **APIs & Services > Credentials**
5. Click **Create Credentials > OAuth client ID**
6. Select **Desktop app** as application type
7. Download the JSON file
8. Rename it to `credentials.json` and place in `mcp/` folder

```bash
cd mcp
cp credentials.json.example credentials.json  # If you already have credentials
# Or place your downloaded credentials.json here
```

### Step 2: Install Dependencies

```bash
cd mcp
source ../venv/bin/activate  # Or your venv
pip install -r requirements.txt
```

---

## 2. Test Offline Mode (No Google Auth Required Initially)

### Test 1: Verify MCP Server Starts

```bash
cd mcp
python mcp_server.py
```

**Expected Output:**
```
NSU Audit MCP Server starting...
  Mode: Offline
  API URL: https://nsu-audit-api.railway.app
  Token path: /home/rafi/.nsu_mcp/token.json

Initializing Google OAuth (opening browser for login)...
```

**What happens:**
- Server detects no token exists
- Opens browser for OAuth login
- After login, token saved to `~/.nsu_mcp/token.json`
- Server starts in stdio mode (waiting for MCP client)

### Test 2: Run Audit Tool Directly (Python)

You can test the audit engine without MCP:

```bash
cd mcp
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').parent / 'backend'))

from tools.audit_tools import run_audit

# Read a test CSV
csv_path = '../tests/BSCSE/L3/L3_BSCSE_001_complete.csv'
with open(csv_path, 'r') as f:
    csv_content = f.read()

result = run_audit(csv_content, 'BSCSE', 3)
print('Student ID:', result.get('student_id'))
print('CGPA:', result.get('cgpa'))
print('Total Credits:', result.get('total_credits'))
print('Eligible:', result.get('eligible'))
print('Deficiencies:', result.get('deficiencies'))
"
```

**Expected Output:**
```
Student ID: 2212345678
CGPA: 3.57
Total Credits: 141
Eligible: True
Deficiencies: []
```

---

## 3. Test with MCP Client (OpenCode)

### Step 1: Configure OpenCode

Add to `.opencode/config.json`:

```json
{
  "mcpServers": [
    {
      "name": "nsu-audit",
      "command": "python /home/rafi/Workspace/Projects/cse226_project/project1_antigravity/mcp/mcp_server.py"
    }
  ]
}
```

### Step 2: Test Each Tool

Start OpenCode and try these prompts:

#### Test Tool: `run_audit`

**Prompt:**
```
Run an L3 audit on this CSV:
student_id,course_code,course_name,credits,grade,semester
2212345678,CSE303,Data Structures,3,A,Fall 2023
2212345678,CSE304,Algorithms,3,A-,Spring 2024
2212345678,CSE305,Database Systems,3,B+,Fall 2024
2212345678,MAT116,Calculus I,3,A,Fall 2023
2212345678,MAT217,Calculus II,3,B,Spring 2024
2212345678,ENG101,English I,3,Pass,Fall 2023
2212345678,ENG102,English II,3,Pass,Spring 2024
```

**Expected Output:**
```json
{
  "student_id": "2212345678",
  "program": "BSCSE",
  "audit_level": 3,
  "cgpa": 3.57,
  "total_credits": 21,
  "eligible": true,
  "deficiencies": []
}
```

#### Test Tool: `list_drive_folder`

**Prompt:**
```
List files in my Google Drive folder called "NSU Transcripts"
```

**Expected Output:**
```json
[
  {
    "file_id": "1abc123...",
    "file_name": "student_2212345678.csv",
    "mime_type": "text/csv",
    "modified_date": "2026-03-15T10:30:00.000Z",
    "size_bytes": 2048
  }
]
```

#### Test Tool: `get_audit_history`

**Prompt:**
```
Show me my audit history, last 5 records
```

**Expected Output:**
```json
[
  {
    "scan_id": "2212345678_2026-03-15T10:30:00Z",
    "student_id": "2212345678",
    "program": "BSCSE",
    "audit_level": 3,
    "cgpa": 3.57,
    "eligible": true,
    "created_at": "2026-03-15T10:30:00Z"
  }
]
```

---

## 4. Test Remote Mode

### Step 1: Set Up API Token

1. Go to the NSU Audit Web App
2. Login with Google
3. Go to Settings > API Access
4. Generate API token
5. Save to file:

```bash
echo "your-api-token-here" > ~/.nsu_mcp/api_token.txt
chmod 600 ~/.nsu_mcp/api_token.txt
```

### Step 2: Start Server in Remote Mode

```bash
cd mcp
python mcp_server.py --remote
```

### Step 3: Test OCR Feature

In remote mode, you can test image transcript scanning:

**Prompt:**
```
Run an L3 audit on the image file with ID 1xyz789 in Google Drive
```

**Expected Output:**
```json
{
  "student_id": "2212345678",
  "program": "BSCSE",
  "audit_level": 3,
  "cgpa": 3.45,
  "total_credits": 138,
  "eligible": true,
  "deficiencies": [],
  "_warning": "OCR used - confidence: 0.92"
}
```

---

## 5. Troubleshooting

### Error: "credentials.json not found"

**Solution:**
```bash
# Make sure credentials.json exists
ls -la mcp/credentials.json

# If using example file
cp mcp/credentials.json.example mcp/credentials.json
# Then replace with your real credentials from Google Cloud Console
```

### Error: "Token expired"

**Solution:**
```bash
python mcp_server.py --reauth
```

### Error: "Module not found"

**Solution:**
```bash
source ../venv/bin/activate
pip install -r requirements.txt
```

### Error: "API token not found" (Remote Mode)

**Solution:**
```bash
echo "your-token" > ~/.nsu_mcp/api_token.txt
chmod 600 ~/.nsu_mcp/api_token.txt
```

---

## 6. Expected Behavior Summary

| Mode | Features | Requirements |
|------|----------|--------------|
| **Offline** | CSV audit only, local history | Google OAuth (one-time) |
| **Remote** | CSV + Image OCR, cloud history | Google OAuth + API token |

| Tool | Works Offline | Works Remote |
|------|---------------|--------------|
| `run_audit` | ✅ CSV | ✅ CSV + OCR |
| `list_drive_folder` | ✅ | ✅ |
| `get_transcript` | ✅ | ✅ |
| `search_drive` | ✅ | ✅ |
| `send_email` | ✅ | ✅ |
| `get_audit_history` | ✅ Local | ✅ Cloud |
| `batch_audit_folder` | ✅ CSV only | ✅ CSV + OCR |
