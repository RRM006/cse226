# Part 4 — Manual Testing Guide
**NSU Audit Core | Phase 2**

---

## Overview

This guide helps you manually test the OCR functionality in Part 4. The OCR service extracts transcript data from images and PDFs, then feeds it into the audit engine.

---

## Test Files

All test files are located in `tests/nsu_transcript_ocr/`:

| File | Description |
|------|-------------|
| `Screenshot_20260309_214956.png` | PNG screenshot transcript |
| `681844277-Transcript.pdf` | First PDF transcript |
| `585057865-Riyadh.pdf` | Second PDF transcript |

---

## Step-by-Step Manual Tests

### Prerequisites

1. Start the backend server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. Ensure you have a valid JWT token (login via CLI or web app)

---

### Test 1: OCR Service Unit Test

**Purpose:** Test OCR extraction directly without API

```bash
cd /home/rafi/Workspace/Projects/cse226_project/project1_antigravity
python -c "
import asyncio
from backend.services.ocr_service import process_ocr, process_pdf_first_page

# Test PNG
png_path = 'tests/nsu_transcript_ocr/Screenshot_20260309_214956.png'
with open(png_path, 'rb') as f:
    img = f.read()

async def test():
    result = await process_ocr(img)
    print(f'PNG: {result.extracted_row_count} rows, confidence: {result.confidence_avg:.2f}')
    print(f'Warnings: {len(result.warnings)}')
    print(f'CSV:\\n{result.csv_text[:500]}')

asyncio.run(test())
"
```

**Expected:**
- PNG: 16+ rows extracted, confidence > 0.90
- Warnings should appear for low-confidence rows

---

### Test 2: PDF Conversion Test

**Purpose:** Test PDF to image conversion

```bash
python -c "
import asyncio
from backend.services.ocr_service import process_pdf_first_page

pdf_path = 'tests/nsu_transcript_ocr/681844277-Transcript.pdf'
with open(pdf_path, 'rb') as f:
    pdf = f.read()

async def test():
    img = await process_pdf_first_page(pdf)
    print(f'Converted to {len(img)} bytes of PNG')

asyncio.run(test())
"
```

**Expected:** Should convert PDF to PNG without errors

---

### Test 3: Full OCR + Audit Pipeline

**Purpose:** Test end-to-end OCR to audit flow

```bash
python -c "
import asyncio
from backend.services.ocr_service import process_ocr, process_pdf_first_page
from backend.services.audit_service import run_audit

pdf_path = 'tests/nsu_transcript_ocr/681844277-Transcript.pdf'
with open(pdf_path, 'rb') as f:
    pdf = f.read()

async def test():
    img = await process_pdf_first_page(pdf)
    ocr = await process_ocr(img)
    print(f'OCR: {ocr.extracted_row_count} rows, conf: {ocr.confidence_avg:.2f}')
    
    audit = await run_audit(
        csv_text=ocr.csv_text,
        program='BSEEE',
        audit_level=1,
        waivers=[],
        knowledge_file=''
    )
    print(f'Audit credits: {audit.get(\"total_credits\")}')

asyncio.run(test())
"
```

**Expected:**
- OCR extracts 20+ rows
- Audit runs successfully and returns total credits

---

### Test 4: API Endpoint Test (Requires Auth)

**Purpose:** Test the `/api/v1/audit/ocr` endpoint

**Using curl:**
```bash
# Replace TOKEN with your JWT
curl -X POST "http://localhost:8000/api/v1/audit/ocr" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@tests/nsu_transcript_ocr/681844277-Transcript.pdf" \
  -F "program=BSEEE" \
  -F "audit_level=1"
```

**Expected Response:**
```json
{
  "scan_id": "uuid",
  "student_id": "...",
  "program": "BSEEE",
  "audit_level": 1,
  "summary": {
    "total_credits": 42,
    "cgpa": 3.2,
    "standing": "...",
    "eligible": false,
    "missing_courses": 3
  },
  "result_text": "=== NSU AUDIT CORE ===\n...",
  "result_json": {...},
  "created_at": "2026-03-09T...",
  "ocr_confidence": 0.95,
  "ocr_extracted_rows": 22,
  "ocr_warnings": ["Row 4: Low confidence (0.69) for ENG103 - excluded"]
}
```

---

### Test 5: Low Confidence Rejection

**Purpose:** Verify 422 returned when confidence < 0.60

The API should return HTTP 422 if OCR confidence is below 0.60. This is handled automatically - low quality images will be rejected.

---

### Test 6: File Type Validation

**Purpose:** Verify only JPG, PNG, PDF accepted

```bash
# Should fail with 400
curl -X POST "http://localhost:8000/api/v1/audit/ocr" \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@test.txt" \
  -F "program=BSEEE" \
  -F "audit_level=1"
```

**Expected:** 400 Bad Request

---

### Test 7: File Size Limit

**Purpose:** Verify 10MB limit enforced

The API should reject files larger than 10MB with 400 error.

---

## Test Results Summary

| Test | File | Expected Rows | Min Confidence |
|------|------|---------------|----------------|
| OCR Unit | PNG | 16+ | 0.90 |
| OCR Unit | PDF 1 | 20+ | 0.90 |
| OCR Unit | PDF 2 | 8+ | 0.85 |
| API | PDF 1 | 20+ | 0.90 |

---

## Troubleshooting

### Issue: "No module named 'easyocr'"
```bash
pip install easyocr opencv-python-headless pdf2image pillow torch torchvision --break-system-packages
```

### Issue: "Could not convert PDF to image"
```bash
# Install poppler
sudo pacman -S poppler  # Arch
sudo apt-get install poppler-utils  # Debian/Ubuntu
```

### Issue: Low extraction count
- Check image quality
- Verify course codes are in format: `XXX000` (e.g., CSE115, ENG102)
- Check that transcript has clear table structure
