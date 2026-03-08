# Testing Guide: Part 2 (Supabase Auth Middleware & Database Layer)

This guide provides exactly what you need to do, step-by-step without skipping anything, to verify that Part 2 was successfully implemented.

## Prerequisites

1. Ensure the backend code changes from Part 2 are saved.
2. Ensure you have activated your Python virtual environment and installed all dependencies:
   ```bash
   cd backend
   source .venv/bin/activate  # On Linux/macOS
   # .\venv\Scripts\activate  # On Windows
   ```

## Step 1: Run the [supabase_schema.sql](file:///home/rafi/Workspace/Projects/cse226_project/project1_antigravity/backend/supabase_schema.sql) script
1. Log in to your project on the [Supabase Dashboard](https://supabase.com/dashboard/).
2. Go to the **SQL Editor** on the left panel.
3. Open [backend/supabase_schema.sql](file:///home/rafi/Workspace/Projects/cse226_project/project1_antigravity/backend/supabase_schema.sql) on your computer, copy its entirely, and paste it into the Supabase SQL Editor.
4. Click **Run** on the bottom right.
5. If it finishes without error, your database is initialized with tables, RLS policies, and the user initialization triggers.

## Step 2: Ensure Google Auth is Enabled
1. In the Supabase dashboard, go to **Authentication** > **Providers**.
2. Make sure **Google** is toggled ON and configured with a Client ID and Client Secret from your Google Cloud Console.

## Step 3: Start the Backend API
1. Open a terminal to your project's `backend/` directory.
2. Source your virtual environment (if not already done).
3. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
4. Look for the message: `Application startup complete.`

## Step 4: Obtain a valid Supabase JWT via Postman (or Web App UI)
Because we haven't built the frontend UI fully yet, the easiest way to get a real Google login JWT right now is to test using the API URL provided in your Supabase Auth settings.

Alternatively, if you have a simple React/HTML page running that uses `@supabase/supabase-js`, you can extract the token from there. For testing purposes through Supabase directly without a frontend:
1. In the Supabase Dashboard, navigate to **Project Settings** > **API**.
2. Find the URL under **Project URL** and the key under **Project API keys** (use `anon`, `public`).

A quick way to simulate a login directly if you don't have a Google button ready: 
1. Go to the **Authentication** section on Supabase > **Users**.
2. Click **Add User** -> **Create New User**. Put a test email (`test@example.com`) and a password (e.g., `Password123!`). Ensure "Auto Confirm User?" is checked. If it isn't checked, confirm the email if necessary.
   *(We can use Email/Password just to test the API route logic quickly since Google Auth gives the exact same shape of JWT.)*
3. Make an API request to Supabase to login and get the token:
   
   **Using cURL:**
   ```bash
   curl -X POST 'https://[YOUR_SUPABASE_PROJECT_ID].supabase.co/auth/v1/token?grant_type=password' \
   -H "apikey: [YOUR_SUPABASE_ANON_KEY]" \
   -H "Content-Type: application/json" \
   -d '{
     "email": "test@example.com",
     "password": "Password123!"
   }'
   ```
4. The response will return a JSON object containing an `access_token`. Copy that `access_token` string. It starts with `eyJ`.

## Step 5: Test the API Endpoint Without Auth
Try calling the `/api/v1/me` endpoint in a new terminal window to see if your unauthenticated request gets rejected as it should.
```bash
curl -X GET 'http://127.0.0.01:8000/api/v1/me'
```
**Expected Output:**
```json
{"detail":"Not authenticated"}
```

## Step 6: Test the API Endpoint With Auth
Now append the `access_token` you copied in Step 4.
```bash
curl -X GET 'http://127.0.0.1:8000/api/v1/me' \
     -H "Authorization: Bearer [PASTE_YOUR_ACCESS_TOKEN_HERE]"
```
**Expected Output:**
```json
{
  "user_id": "[Your_UUID]",
  "email": "test@example.com",
  "role": "student"
}
```
*If you see this, Part 2 is 100% working!* Your FastAPI server has successfully verified the JWT against the Supabase public keys and fetched the role (defaulting to student).

## Step 7 (Optional Check): Verify Profile Auto-Creation
1. In the Supabase dashboard, go to the **Table Editor**.
2. Open the `profiles` table.
3. You should see a row automatically generated matching your UUID with the email `test@example.com` and `role` = `student`. 
This confirms `Step 2.3` (Profiles Auto-Create Trigger) worked perfectly.

## Summary
Once you have run through these steps and seen the successful `user_id` output, you have confirmed that the Supabase client, auth middleware, triggers, and test endpoints for **Part 2** are completely done. 

Please follow this and confirm when everything passes!
