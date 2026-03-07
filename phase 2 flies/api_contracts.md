# API Contracts — Phase 2
**NSU Audit Core | FastAPI Backend**
Full request/response spec for every endpoint.

Base URL: `https://nsu-audit-api.railway.app`
Local dev: `http://localhost:8000`
API Docs (auto-generated): `{base_url}/docs`

---

## Auth Header (all protected routes)

```
Authorization: Bearer <supabase_jwt>
```

---

## GET /health

**Auth:** Not required

**Response 200:**
```json
{
  "status": "ok",
  "version": "2.0"
}
```

---

## POST /api/v1/audit/csv

**Auth:** Required
**Content-Type:** `multipart/form-data`

**Request fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | File | ✅ | CSV transcript file |
| program | string | ✅ | `BSCSE` \| `BSEEE` \| `LLB` |
| audit_level | integer | ✅ | `1` \| `2` \| `3` |
| waivers | string | ❌ | Comma-separated, e.g. `ENG102,MAT116` |

**Response 200:**
```json
{
  "scan_id": "uuid-string",
  "student_id": "2012345678",
  "program": "BSCSE",
  "audit_level": 3,
  "input_type": "csv",
  "waivers_applied": ["ENG102"],
  "summary": {
    "total_credits": 127,
    "cgpa": 3.42,
    "standing": "First Class (Good Standing)",
    "eligible": false,
    "missing_courses_count": 2
  },
  "result_text": "=== NSU AUDIT CORE - LEVEL 3 ===\n...",
  "result_json": {
    "student_id": "2012345678",
    "program": "BSCSE",
    "audit_level": 3,
    "total_credits": 127,
    "required_credits": 130,
    "cgpa": 3.42,
    "standing": "First Class (Good Standing)",
    "eligible": false,
    "missing_courses": [
      {"code": "CSE499B", "name": "Senior Design Project II", "credits": 3, "category": "Capstone"}
    ],
    "excluded_courses": [
      {"code": "CSE305", "grade": "F", "credits": 3, "reason": "FAILED"}
    ],
    "waivers_applied": ["ENG102"]
  },
  "created_at": "2026-03-05T10:30:00Z"
}
```

**Response 422 (validation error):**
```json
{
  "detail": [
    {"loc": ["body", "program"], "msg": "value is not a valid enum member", "type": "type_error.enum"}
  ]
}
```

**Response 400 (bad CSV):**
```json
{
  "error": "invalid_csv",
  "message": "CSV missing required columns: grade, semester"
}
```

---

## POST /api/v1/audit/ocr

**Auth:** Required
**Content-Type:** `multipart/form-data`

**Request fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| image | File | ✅ | JPG, PNG, or PDF (first page) |
| program | string | ✅ | `BSCSE` \| `BSEEE` \| `LLB` |
| audit_level | integer | ✅ | `1` \| `2` \| `3` |
| waivers | string | ❌ | Comma-separated |

**Response 200:**
```json
{
  "scan_id": "uuid-string",
  "student_id": "2012345678",
  "program": "BSCSE",
  "audit_level": 3,
  "input_type": "ocr_image",
  "ocr_confidence": 0.89,
  "ocr_extracted_rows": 34,
  "ocr_warnings": [
    "Row 12: grade unclear (confidence 0.61) — assumed 'B'"
  ],
  "summary": {
    "total_credits": 127,
    "cgpa": 3.42,
    "standing": "First Class (Good Standing)",
    "eligible": false,
    "missing_courses_count": 2
  },
  "result_text": "=== NSU AUDIT CORE - LEVEL 3 ===\n...",
  "result_json": { "..." : "..." },
  "created_at": "2026-03-05T10:30:00Z"
}
```

**Response 422 (low confidence):**
```json
{
  "error": "ocr_low_confidence",
  "message": "OCR confidence too low (0.42). Please upload a clearer image.",
  "ocr_confidence": 0.42,
  "ocr_warnings": ["Row 3: unreadable", "Row 7: unreadable", "..."]
}
```

---

## GET /api/v1/audit/{scan_id}

**Auth:** Required (owner or admin)

**Response 200:**
```json
{
  "scan_id": "uuid",
  "user_id": "uuid",
  "student_id": "2012345678",
  "program": "BSCSE",
  "audit_level": 3,
  "input_type": "csv",
  "waivers_applied": [],
  "summary": { "..." : "..." },
  "result_text": "...",
  "result_json": { "..." : "..." },
  "created_at": "2026-03-05T10:30:00Z"
}
```

**Response 403:**
```json
{ "error": "forbidden", "message": "You do not have access to this scan." }
```

**Response 404:**
```json
{ "error": "not_found", "message": "Scan not found." }
```

---

## GET /api/v1/history

**Auth:** Required

**Query params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| limit | int | 20 | Max results to return |
| offset | int | 0 | Pagination offset |

**Response 200:**
```json
{
  "total": 12,
  "limit": 20,
  "offset": 0,
  "scans": [
    {
      "scan_id": "uuid",
      "input_type": "csv",
      "program": "BSCSE",
      "audit_level": 3,
      "summary": {
        "cgpa": 3.42,
        "eligible": false,
        "total_credits": 127,
        "standing": "First Class (Good Standing)"
      },
      "created_at": "2026-03-05T10:30:00Z"
    }
  ]
}
```

---

## DELETE /api/v1/history/{scan_id}

**Auth:** Required (owner only)

**Response 200:**
```json
{ "message": "Scan deleted successfully." }
```

**Response 403:**
```json
{ "error": "forbidden", "message": "You can only delete your own scans." }
```

---

## GET /api/v1/history/user/{user_id}

**Auth:** Admin only

**Response 200:** Same format as GET /api/v1/history

---

## GET /api/v1/users

**Auth:** Admin only

**Response 200:**
```json
{
  "total": 5,
  "users": [
    {
      "id": "uuid",
      "email": "student@northsouth.edu",
      "full_name": "Tanvir Ahmed",
      "role": "student",
      "scan_count": 3,
      "created_at": "2026-03-01T09:00:00Z"
    }
  ]
}
```

---

## PATCH /api/v1/users/{user_id}/role

**Auth:** Admin only
**Content-Type:** `application/json`

**Request body:**
```json
{ "role": "admin" }
```

**Response 200:**
```json
{
  "message": "Role updated.",
  "user_id": "uuid",
  "new_role": "admin"
}
```

**Response 400:**
```json
{ "error": "invalid_role", "message": "Role must be 'student' or 'admin'." }
```

---

## Error Response Format (all errors)

All errors return structured JSON — never raw Python tracebacks.

```json
{
  "error": "error_code_snake_case",
  "message": "Human-readable description of what went wrong."
}
```

Common error codes:
| Code | HTTP | Meaning |
|------|------|---------|
| `unauthorized` | 401 | Missing or invalid JWT |
| `forbidden` | 403 | Valid JWT but insufficient role |
| `not_found` | 404 | Resource doesn't exist |
| `invalid_csv` | 400 | CSV format/columns wrong |
| `invalid_program` | 422 | Program not BSCSE/BSEEE/LLB |
| `ocr_low_confidence` | 422 | OCR confidence below threshold |
| `internal_error` | 500 | Unexpected server error |
