# Pickup Guide - NSU Audit Core Phase 2

## Current State

### Completed Parts
- **PART 1**: Project Bootstrap & Supabase Setup — COMPLETE
- **PART 2**: Supabase Auth Middleware & Database Layer — COMPLETE  
- **PART 3**: Audit Service (Phase 1 Engine Wrapper) — COMPLETE
- **PART 4.0**: CLI Google Auth with NSU Email Restriction — COMPLETE
- **PART 4**: OCR Service — COMPLETE (Including deep OCR bug fixes)

### In Progress
- **PART 5**: History Routes & Updated CLI — NOT STARTED (Ready to begin)

### Not Started Yet
- None (Only Part 5 remains)

---

## What Was Just Done (This Session)

### Files Created/Modified

1. **`backend/services/ocr_service.py`** (Heavily updated to fix OCR accuracy on transcripts)
   - **Multi-column Layout Fix:** Replaced hardcoded pixel delta checking with dynamic page midpoint detection for left/right columns to prevent horizontal merging of separate courses.
   - **Lenient Course Code Regex:** Updated `COURSE_CODE_PATTERN` to catch typical OCR digit misreads (like 'MATI6' becoming 'MAT116', 'L'/'I' to '1', 'O' to '0', 'S' to '5').
   - **DPI Increase:** Increased `pdf2image` conversion to `dpi=300`. This allowed EasyOCR to successfully read single-character grades (like 'B', 'D') that were previously being hidden by the 'NORTH SOUTH UNIVERSITY' watermark.
   - **Grade/Credit Token Splitting:** EasyOCR was merging grades and noise together (e.g., `[13.0TTI D`). Implemented string splitting by space so that 'D' is cleanly isolated as a `VALID_GRADE`.
   - **Confidence Threshold Adjustments:** Lowered the confidence exclusion threshold from `< 0.70` to `< 0.30`. The 300 DPI conversion caused baseline confidence to drop to ~0.50 on otherwise perfect reads (like 'ENG102'), so lowering the threshold prevents valid courses from disappearing.

### Decisions Made

1. **Resolution vs Confidence Trade-off**: Decided to use 300 DPI for PDF extraction. While this slightly lowered the confidence scores for some EasyOCR bounding boxes, it was absolutely mandatory to recover single-letter grades (A, B, C, D) which were being destroyed by the transcript gray watermark at 200 DPI.
2. **Lower Rejection Threshold**: Because we have a very strict regex validation pattern for course codes (`^[A-Z]{2,4}\s*[\dIOlSZ]{2,4}$`), it is safe to lower the EasyOCR confidence rejection threshold to `< 0.30`. The regex ensures we aren't picking up garbage rows.
3. **Midpoint Column Separation**: Decided that checking if `x < page_midpoint` is infinitely more robust for preventing left/right column crosstalk than checking if items are `< 500px` apart.

### Logged Assumptions
- Assumed OCR digit misreads are deterministic enough to normalize programmatically (I->1, O->0, S->5, Z->2).
- Assumed any isolated token falling in `VALID_GRADES` across a horizontally clustered row is the student's grade, even if merged near a noisy block.

---

## Exact Next Step

**Start PART 5 — History Routes & Updated CLI**

**What to do first:**
1. Open `tracking2.md` and review the checklist for `PART 5`.
2. Create/Open `backend/routers/history.py` to start implementing the API endpoints (`GET /api/v1/history`, `GET /api/v1/history/{scan_id}`, etc.).
3. Ensure the current user token validation (`Depends(get_current_user)`) is hooked up to these routes.

**Immediate instruction:**
Begin writing the `history.py` router and bind it to `main.py`. Do not revisit OCR unless explicitly asked—it is fully verified and stable.

---

## Open Items

### Bugs/Issues
- None. The missing MAT116 and hidden grades bugs are fully verified as fixed.

### Questions Not Fully Answered
- None.

### Deferred Items
- None.

---

## Key Files Reference

### Backend Core
| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI application entry point |
| `backend/config.py` | Pydantic settings configuration |
| `backend/database.py` | Supabase database helper functions |
| `backend/auth.py` | JWT validation and CurrentUser dependency |

### Services
| File | Purpose |
|------|---------|
| `backend/services/audit_service.py` | Wrapper for Phase 1 audit engine (L1/L2/L3) |
| `backend/services/ocr_service.py` | OCR pipeline for transcript images/PDFs (Handles layout, regex, extraction) |
| `backend/services/scan_service.py` | Save/retrieve audit scans from database |

### Routers
| File | Purpose |
|------|---------|
| `backend/routers/audit.py` | `/api/v1/audit/csv` and `/api/v1/audit/ocr` endpoints |

### Phase 1 Engine (Backend Core)
| File | Purpose |
|------|---------|
| `backend/core/level1_credit_tally.py` | Level 1: Credit tally |
| `backend/core/level2_cgpa_calculator.py` | Level 2: CGPA calculation |
| `backend/core/level3_audit_engine.py` | Level 3: Full graduation audit |

### CLI
| File | Purpose |
|------|---------|
| `cli/audit_cli.py` | Main CLI holding logic for all commands |
| `cli/credentials.py` | Credentials management (`~/.nsu_audit/credentials.json`) |

### Executable CLI Scripts (Project Root)
| File | Purpose |
|------|---------|
| `login`, `logout` | Auth management commands |
| `l1`, `l2`, `l3`, `ocr` | Direct invocation scripts for audit levels and OCR |

### Documentation
| File | Purpose |
|------|---------|
| `tracking2.md` | Progress tracker with part-by-part checklist |
| `assumptions2.md` | All assumptions made during development |
| `testing_plan2.md` | Test cases and results |
| `phase2_prd2.md` | Full requirements document |

### Program Knowledge (Knowledge Base)
| File | Purpose |
|------|---------|
| `program_knowledge/program_knowledge_BSCSE.md` | BSCSE graduation requirements |
| `program_knowledge/program_knowledge_BSEEE.md` | BSEEE graduation requirements |
| `program_knowledge/program_knowledge_LLB.md` | LLB graduation requirements |
