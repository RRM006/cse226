# Supabase Setup Guide — Phase 2
**One-time setup. Do this before writing any backend code.**

---

## Step 1 — Create Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Name: `nsu-audit-core`
4. Password: generate a strong DB password and save it
5. Region: choose closest to Bangladesh (Singapore: `ap-southeast-1`)
6. Wait for project to provision (~2 min)

---

## Step 2 — Get Your Keys

Go to **Project Settings → API**

Copy these three values into `backend/.env`:
```
SUPABASE_URL=https://<your-project-id>.supabase.co
SUPABASE_ANON_KEY=<your anon key>
SUPABASE_SERVICE_KEY=<your service_role key>
```

⚠️ NEVER commit `.env` to git. It is in `.gitignore`.

---

## Step 3 — Run the Schema SQL

Go to **SQL Editor** in Supabase dashboard.
Paste and run the contents of `backend/supabase_schema.sql`.

This creates:
- `profiles` table
- `scans` table
- Row Level Security policies
- Auto-create profile trigger on Google login

Verify in **Table Editor** that both tables exist.

---

## Step 4 — Enable Google OAuth

Go to **Authentication → Providers → Google**

1. Enable Google provider
2. Go to https://console.cloud.google.com
3. Create a new project or use existing
4. Go to **APIs & Services → Credentials**
5. Create **OAuth 2.0 Client ID**
   - Application type: Web application
   - Authorized redirect URIs: add `https://<your-project-id>.supabase.co/auth/v1/callback`
6. Copy **Client ID** and **Client Secret**
7. Paste them into Supabase Google provider settings
8. Save

---

## Step 5 — Set Redirect URLs

In Supabase **Authentication → URL Configuration**:

Site URL:
```
https://<your-vercel-app>.vercel.app
```

Additional redirect URLs (add all of these):
```
https://<your-vercel-app>.vercel.app/
http://localhost:5173/
http://localhost:5173
```

---

## Step 6 — Verify RLS is Active

In **Authentication → Policies**, confirm:

For `scans` table:
- `student_own_scans` → SELECT WHERE `auth.uid() = user_id`
- `admin_all_scans` → SELECT WHERE user has admin role
- `insert_own_scan` → INSERT WITH CHECK `auth.uid() = user_id`

For `profiles` table:
- Users can read their own profile
- Admins can read all profiles

---

## Step 7 — Test Google Login

1. Start frontend locally: `npm run dev` in `frontend/`
2. Go to `http://localhost:5173/login`
3. Click "Login with Google"
4. Sign in with a Google account
5. In Supabase dashboard → **Authentication → Users**, confirm the user appears
6. In **Table Editor → profiles**, confirm a row was auto-created

---

## Step 8 — Make Yourself Admin

After first login, manually promote yourself to admin:

In Supabase **SQL Editor**:
```sql
UPDATE profiles
SET role = 'admin'
WHERE email = 'your-email@gmail.com';
```

Verify in **Table Editor → profiles** that `role = 'admin'`.

---

## Schema Reference

```sql

-- Run this in Supabase SQL Editor
-- File: backend/supabase_schema.sql

-- Drop existing tables (cascade removes policies, triggers, foreign keys)
DROP TABLE IF EXISTS scans CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;
-- Drop existing functions
DROP FUNCTION IF EXISTS is_admin();
DROP FUNCTION IF EXISTS handle_new_user();
-- Drop existing trigger (already removed by cascade but just in case)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Profiles table (extends Supabase auth.users)
CREATE TABLE profiles (
  id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email       TEXT UNIQUE NOT NULL,
  full_name   TEXT,
role        TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'admin')),
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
-- Scans table (one row per audit run)
CREATE TABLE scans (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  student_id      TEXT,
  program         TEXT CHECK (program IN ('BSCSE', 'BSEEE', 'LLB')),
  input_type      TEXT NOT NULL CHECK (input_type IN ('csv', 'ocr_image')),
  raw_input       TEXT,
  waivers         TEXT[] DEFAULT '{}',
  audit_level     INTEGER NOT NULL CHECK (audit_level IN (1, 2, 3)),
  result_json     JSONB NOT NULL,
  result_text     TEXT NOT NULL,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE scans ENABLE ROW LEVEL SECURITY;
-- Helper function to avoid recursive RLS on profiles
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin'
  );
$$ LANGUAGE sql SECURITY DEFINER STABLE;
-- Profiles: users can read their own profile
CREATE POLICY "profiles_own_read" ON profiles
FOR SELECT USING (auth.uid() = id);
-- Profiles: admins can read all profiles
CREATE POLICY "profiles_admin_read" ON profiles
FOR SELECT USING (is_admin());
-- Profiles: users can update their own profile
CREATE POLICY "profiles_own_update" ON profiles
FOR UPDATE USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);
-- Profiles: admins can update any profile (role changes)
CREATE POLICY "profiles_admin_update" ON profiles
FOR UPDATE USING (is_admin());
-- Scans: students see only their own
CREATE POLICY "scans_student_own" ON scans
FOR SELECT USING (auth.uid() = user_id);
-- Scans: admins see all
CREATE POLICY "scans_admin_all" ON scans
FOR SELECT USING (is_admin());
-- Scans: any authenticated user can insert their own
CREATE POLICY "scans_insert_own" ON scans
FOR INSERT WITH CHECK (auth.uid() = user_id);
-- Scans: users can delete their own
CREATE POLICY "scans_delete_own" ON scans
FOR DELETE USING (auth.uid() = user_id);
-- Scans: admins can delete any
CREATE POLICY "scans_admin_delete" ON scans
FOR DELETE USING (is_admin());
-- Auto-create profile when new user signs up
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
INSERT INTO profiles (id, email, full_name, role)
VALUES (
    NEW.id,
    NEW.email,
COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
'student'
  )
ON CONFLICT (id) DO NOTHING;
RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION handle_new_user();

---

## Common Issues

| Issue | Fix |
|-------|-----|
| "JWT expired" errors in tests | Re-login and copy fresh JWT |
| Profile not created after login | Check trigger is active in SQL Editor: `SELECT * FROM pg_trigger WHERE tgname = 'on_auth_user_created'` |
| Google OAuth redirect mismatch | Double-check redirect URI in Google Cloud Console matches Supabase callback URL exactly |
| RLS blocking all reads | Make sure you're passing the user JWT, not the anon key, in API requests |
| `role` column missing | Re-run schema SQL |
