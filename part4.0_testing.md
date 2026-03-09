# Part 4.0 — Testing Guide
**NSU Audit Core CLI - Google Auth with NSU Email Restriction**

---

## Prerequisites

Make sure you have the virtual environment activated:

```bash
cd /home/rafi/Workspace/Projects/cse226_project/project1_antigravity
source .venv/bin/activate
```

Or use the full path:
```bash
/home/rafi/Workspace/Projects/cse226_project/project1_antigravity/.venv/bin/python /home/rafi/Workspace/Projects/cse226_project/project1_antigravity/cli/audit_cli.py <command>
```

---

## Test Cases

### TEST 1: Help Command
**Purpose:** Verify CLI shows help

**Steps:**
```bash
python cli/audit_cli.py --help
```

**Expected Output:**
```
usage: audit_cli.py [-h] {login,logout,l1,l2,l3} ...

NSU Audit Core CLI

positional arguments:
  {login,logout,l1,l2,l3}
    login               Login with NSU Google account
    logout              Logout and clear credentials
    l1                  Run Level 1 audit (credit tally)
    ...
```

---

### TEST 2: Audit Without Login (Should Block)
**Purpose:** Verify l1/l2/l3 commands are blocked when not logged in

**Steps:**
```bash
# First, make sure you're logged out
python cli/audit_cli.py logout

# Try to run an audit
python cli/audit_cli.py l1 data/samples/test_L1.csv
```

**Expected Output:**
```
❌ You must be logged in to run audits.
   Run: python cli/audit_cli.py login
```

**Exit Code:** 1

---

### TEST 3: Logout When Not Logged In
**Purpose:** Verify logout works even when not logged in

**Steps:**
```bash
python cli/audit_cli.py logout
```

**Expected Output:**
```
Logged out.
```

---

### TEST 4: Login Command (Manual Browser OAuth)
**Purpose:** Test the login flow with real Google OAuth

**Steps:**
```bash
python cli/audit_cli.py login
```

**What happens:**
1. CLI prints "Opening browser for NSU Google login..."
2. Your default browser opens with Supabase Google OAuth page
3. Login with your **@northsouth.edu** Google account
4. After login, you should be redirected to a local page saying "Login complete. Return to your terminal."
5. CLI should print: `✅ Logged in as <your-email>@northsouth.edu`

**If using non-NSU email (@gmail.com, etc.):**
- Expected: `❌ Login failed: only @northsouth.edu accounts are permitted.`

**If browser doesn't open:**
- CLI will print the URL - copy/paste it manually in your browser

**Timeout:**
- If you don't complete login within 120 seconds, CLI prints: `❌ Login failed: no token received.`

---

### TEST 5: Verify Credentials Saved
**Purpose:** Check that login actually saved credentials

**Steps:**
```bash
cat ~/.nsu_audit/credentials.json
```

**Expected Output (formatted JSON):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "...",
  "email": "your.name@northsouth.edu"
}
```

---

### TEST 6: Audit After Login (Should Work)
**Purpose:** Verify audit runs when logged in

**Steps:**
```bash
# After successful login
python cli/audit_cli.py l1 data/samples/test_L1.csv
```

**Expected:** Full Level 1 audit output (credit tally table)

---

### TEST 7: Logout
**Purpose:** Test logout clears credentials

**Steps:**
```bash
python cli/audit_cli.py logout
```

**Expected Output:**
```
Logged out.
```

---

### TEST 8: Verify Credentials Deleted
**Steps:**
```bash
cat ~/.nsu_audit/credentials.json
```

**Expected Output:**
```
cat: /home/rafi/.nsu_audit/credentials.json: No such file or directory
```

---

### TEST 9: Audit After Logout (Should Block Again)
**Purpose:** Verify logout actually revokes access

**Steps:**
```bash
python cli/audit_cli.py l1 data/samples/test_L1.csv
```

**Expected Output:**
```
❌ You must be logged in to run audits.
   Run: python cli/audit_cli.py login
```

---

## Test l2 and l3 Commands Too

Don't just test l1 - also verify l2 and l3:

```bash
# Login first
python cli/audit_cli.py login

# Test Level 2
python cli/audit_cli.py l2 data/samples/test_L2.csv

# Test Level 3
python cli/audit_cli.py l3 data/samples/test_L3_retake.csv

# Logout
python cli/audit_cli.py logout
```

---

## Quick Test Summary

| # | Test | Command | Expected |
|---|------|---------|----------|
| 1 | Help | `python cli/audit_cli.py --help` | Shows usage |
| 2 | Blocked (no login) | `python cli/audit_cli.py l1 ...` | ❌ Must be logged in |
| 3 | Logout (not logged) | `python cli/audit_cli.py logout` | Logged out. |
| 4 | Login | `python cli/audit_cli.py login` | ✅ Logged in as ...@northsouth.edu |
| 5 | Credentials saved | `cat ~/.nsu_audit/credentials.json` | JSON with email |
| 6 | Audit works | `python cli/audit_cli.py l1 ...` | Full output |
| 7 | Logout | `python cli/audit_cli.py logout` | Logged out. |
| 8 | Credentials deleted | `cat ~/.nsu_audit/credentials.json` | File not found |
| 9 | Blocked again | `python cli/audit_cli.py l1 ...` | ❌ Must be logged in |

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'dotenv'"
Fix:
```bash
pip install python-dotenv
```

### "SUPABASE_URL not configured"
Fix: Make sure `backend/.env` exists and has `SUPABASE_URL` and `SUPABASE_ANON_KEY`

### Login times out immediately
The callback server might need more time. Just run `login` again.

### Credentials file location
- Path: `~/.nsu_audit/credentials.json`
- On Windows: `C:\Users\<username>\.nsu_audit\credentials.json`
