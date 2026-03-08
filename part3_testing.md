# Part 3 Testing Guide — CSV Audit Endpoint

Follow these step-by-step instructions to verify that Part 3 (the Phase 1 Engine wrapper and the `/api/v1/audit/csv` endpoint) is working correctly on your machine.

## Prerequisites

1. Your virtual environment is activated (`source .venv/bin/activate` or `source venv/bin/activate`).
2. Your Supabase `.env` variables are correctly loaded.
3. Your FastAPI server is running (`uvicorn backend.main:app --reload`).

## 1. Getting a Valid JWT Token

You need an authentication token to test the API. Since we set up a Supabase auto-profile trigger, the easiest way to get a token is to log in through the Supabase dashboard or use a small script. 

If you already have a token from testing Part 2, you can use that. Otherwise, you can use the interactive Swagger UI built into FastAPI:

1. Open http://localhost:8000/docs in your browser.
2. Click the green **Authorize** button.
3. Enter a valid JWT token. (You can generate one for a user in your Supabase project using the API or by logging into your frontend temporarily if it's set up).

*Alternatively, you can test via `curl` bypassing auth if you temporarily modify `get_current_user` in `backend/auth.py` for local testing.*

## 2. Testing via Swagger UI (Recommended)

1. Open your browser to the FastAPI Swagger UI: http://localhost:8000/docs
2. Scroll down to the `POST /api/v1/audit/csv` endpoint under the **audit** section.
3. Click **Try it out**.
4. Fill out the form fields:
   * **file**: Click "Choose File" and select `data/samples/transcript.csv` (or any other CSV from the data/samples folder).
   * **program**: Enter `BSCSE`
   * **audit_level**: Enter `3`
   * **waivers**: Leave empty or enter a valid waiver like `ENG102`
5. Click **Execute**.

### Expected Result in Swagger:
* **Response Code:** `200`
* **Response Body:** A JSON object containing:
  * `scan_id`: A UUID string.
  * `student_id`: "1234567" (or whatever is in the CSV)
  * `program`: "BSCSE"
  * `summary`: A JSON object matching the PRD containing `total_credits`, `cgpa`, `standing`, `eligible`, and `missing_courses` count.
  * `result_json`: The detailed JSON data array.
  * `result_text`: A large string block containing the classic Phase 1 box-drawing output.

## 3. Testing via cURL (Terminal)

If you prefer the terminal, run the following command (replace `YOUR_JWT_TOKEN` with your actual token):

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/audit/csv' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@data/samples/transcript.csv;type=text/csv' \
  -F 'program=BSCSE' \
  -F 'audit_level=3' \
  -F 'waivers=ENG102'
```

### Expected Output
You should see a large JSON response ending with the visual string representation of the audit.

## 4. Verifying Database Saving

After running a successful audit API request via Swagger or cURL:

1. Go to your **Supabase Dashboard**.
2. Click on the **Table Editor**.
3. Select the `scans` table.
4. You should see a brand new row created for your audit test.
5. Check the columns: 
   * `input_type` should be `"csv"`.
   * `result_text` and `result_json` should contain the generated report data.
   * `student_id`, `program`, and `audit_level` should be populated correctly.

## 5. Specific Test Cases to Verify

To be completely thorough and match `testing_plan2.md`, perform the same `POST` request test but change the inputs according to these specific cases:

### Test Case AS-1: Level 1 — Valid CSV, BSCSE
* **Input:** `data/samples/test_L1_cse_standard.csv` (or equivalent), `program=BSCSE`, `audit_level=1`, `waivers=`
* **Expected:** `result_json.total_credits` matches Phase 1 Level 1 output.

### Test Case AS-2: Level 2 — CGPA with Waivers, BSCSE
* **Input:** `data/samples/test_L2_cse_waivers.csv` (or equivalent), `program=BSCSE`, `audit_level=2`, `waivers=ENG102,MAT116`
* **Expected:** CGPA calculation excludes the waived courses.

### Test Case AS-3: Level 3 — Full Audit, Graduation Eligible, BSCSE
* **Input:** `data/samples/test_L3_cse_eligible.csv` (or equivalent), `program=BSCSE`, `audit_level=3`, `waivers=`
* **Expected:** `summary.eligible` is `true`, `missing_courses` count is 0.

### Test Case AS-4: Level 3 — Full Audit, Not Eligible, Missing Capstone
* **Input:** `data/samples/test_L3_cse_missing_capstone.csv` (or equivalent), `program=BSCSE`, `audit_level=3`, `waivers=`
* **Expected:** `summary.eligible` is `false`, CSE499B in `missing_courses`.

### Test Case AS-5: Level 3 — LLB Program, Missing Core Year 4
* **Input:** `data/samples/test_L3_law_missing_core.csv` (or equivalent), `program=LLB`, `audit_level=3`, `waivers=ENG102`
* **Expected:** `summary.eligible` is `false`, year 4 courses in `missing_courses`.

### Test Case AS-6: Level 3 — Retake Scenario, Passed After Fail
* **Input:** `data/samples/test_L3_retake.csv` (or equivalent), `program=BSCSE`, `audit_level=3`, `waivers=`
* **Expected:** The failed-then-passed course clears the requirement properly.

### Test Case AS-7: Level 1 — Invalid Grades Excluded
* **Input:** Any CSV with F, W, I, X grades, `audit_level=1`
* **Expected:** Invalid grade rows excluded from credit total.

### Test Case AS-8: Level 2 — Probation Flag
* **Input:** Any CSV with CGPA < 2.0, `audit_level=2`
* **Expected:** `summary.standing` is `"PROBATION"`, `summary.eligible` is `false`.

### Test Case API-5: Missing Program Field
* **Input:** Any CSV, `audit_level=3`, but DO NOT send the `program` field.
* **Expected:** 422 Unprocessable Entity with validation error.
