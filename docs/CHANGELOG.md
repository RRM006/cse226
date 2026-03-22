# Changelog

## [Unreleased] — Cleanup & Quality Improvement Pass

### Deleted Files

| File/Folder | Reason |
|-------------|--------|
| `archive/src/` | Legacy Phase 1 duplicate code — identical to `backend/core/` |
| `archive/test_outputs/` | Test output files — not needed |
| `archive/scripts/` | Obsolete test runner scripts |
| `frontend/src/App.css` | Unused CSS file with no imports |
| `frontend/src/assets/` | Unused folder — contained only `react.svg` |
| `tests/testclirun.txt` | Temporary debug output file |
| `tests/test_mcp/` | Empty directory |
| `mobile/nsu_audit_mobile.iml` | IntelliJ IDE artifact |
| `.opencode/` | Local OpenCode cache directory |
| `web` (old bash script) | Redundant — replaced with cleaner version |
| `mcp/mcp_script` | Redundant bash launcher |
| `mcp/phase3_prd.md` | Obsolete Phase 3 requirements doc |
| `mcp/TESTING.md` | Duplicated `mcp/README.md` content |

### Created Files

| File | Purpose |
|------|---------|
| `backend/core/shared.py` | Extracted common functions: `parse_transcript`, `detect_program`, `resolve_retakes`, `calculate_cgpa`, `get_standing`, `format_credits` |
| `backend/core/__init__.py` | Package exports: `run_level1`, `run_level2`, `run_level3`, shared utilities |
| `tests/test_audit.py` | 22 pytest unit tests covering core engine |
| `tests/__init__.py` | Python package marker |
| `README.md` | Professional root README (consolidated from docs) |
| `web` | Bash wrapper for `web_launcher.py` |
| `docs/CHANGELOG.md` | This file |

### Modified Files

#### Frontend

| File | Change |
|------|--------|
| `frontend/src/App.jsx` | Fixed `window.location.href` → `useNavigate()` (SPA navigation fix) |
| `frontend/src/lib/api.js` | Fixed module-load crash → `console.warn()` (graceful env var handling) |
| `frontend/src/lib/supabase.js` | Fixed module-load crash → null check + graceful fallback |
| `frontend/eslint.config.js` | Fixed `varsIgnorePattern: '^[A-Z_]'` → `'^_'` (dangerous pattern) |

#### Mobile

| File | Change |
|------|--------|
| `mobile/lib/services/auth_service.dart` | Fixed `signInWithGoogle()` OAuth callback URL |
| `mobile/lib/services/api_service.dart` | Fixed status code check → `200-299` range |

#### Backend

| File | Change |
|------|--------|
| `backend/core/level1_credit_tally.py` | Imports from `shared.py`, removed duplicate functions, added type hints |
| `backend/core/level2_cgpa_calculator.py` | Imports from `shared.py`, removed duplicate functions, added type hints |
| `backend/core/shared.py` | Added CSV column validation (`parse_transcript`) |

#### Configuration

| File | Change |
|------|--------|
| `.gitignore` | Cleaned up, added missing entries |

#### MCP

| File | Change |
|------|--------|
| `mcp/README.md` | Condensed from 290 → ~140 lines, removed duplicate testing content |

### Critical Bug Fixes

1. **Frontend App.jsx** — `window.location.href` redirect broke SPA navigation. Fixed to use `useNavigate()`.

2. **Frontend api.js / supabase.js** — `throw new Error()` at module load crashed entire app if env vars missing. Fixed to `console.warn()` with graceful fallback.

3. **Frontend eslint.config.js** — `varsIgnorePattern: '^[A-Z_]'` silenced virtually ALL variable warnings. Fixed to `'^_'` (only underscore-prefixed).

4. **Mobile api_service.dart** — Only `statusCode == 200` treated as success. API returns 201/202 for some endpoints. Fixed to `200-299` range.

5. **Mobile auth_service.dart** — `signInWithGoogle()` didn't await OAuth completion. Fixed with proper async handling.

### Code Quality Improvements

1. **Shared module** — Extracted 6 duplicate functions into `backend/core/shared.py`:
   - `parse_transcript()` — now includes CSV column validation
   - `detect_program()`
   - `resolve_retakes()`
   - `calculate_cgpa()` — now supports waivers parameter
   - `get_standing()`
   - `format_credits()`

2. **Type hints added** — All function signatures now include proper type hints (`Optional[List[str]]`).

3. **Tests added** — 22 pytest unit tests covering:
   - Shared utilities
   - Level 1 credit tally
   - Level 2 CGPA calculator
   - Edge cases (empty CSV, case-insensitive grades, etc.)

### .gitignore Updates

Added entries for:
- `frontend/package-lock.json`
- `mobile/linux/flutter/*.so`
- `mobile/linux/flutter/ephemeral/`
- `pickup_guide.md`
- `opencode.json`
- `.opencode/`
