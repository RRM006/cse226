-- Supabase Schema for NSU Audit Core Phase 2

-- Run this in Supabase SQL Editor
-- File: backend/supabase_schema.sql

-- Drop existing tables (cascade removes policies, triggers, foreign keys)
DROP TABLE IF EXISTS scans CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;
-- Drop existing functions
DROP FUNCTION IF EXISTS is_admin();
DROP FUNCTION IF EXISTS handle_new_user() CASCADE;
-- Drop existing trigger (already removed by cascade but just in case)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Profiles table (extends Supabase auth.users)
CREATE TABLE profiles (
  id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email       TEXT UNIQUE NOT NULL,
  full_name   TEXT,
  role        TEXT NOT NULL DEFAULT 'admin' CHECK (role IN ('student', 'admin')),
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

-- =====================
-- PROFILES POLICIES
-- =====================

-- Profiles: allow trigger to insert new profiles on signup  ← FIX #1 (NEW)
CREATE POLICY "profiles_insert_own" ON profiles
FOR INSERT WITH CHECK (true);

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

-- =====================
-- SCANS POLICIES
-- =====================

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

-- =====================
-- TRIGGER FUNCTION       ← FIX #2 (UPDATED - safer with COALESCE + EXCEPTION handler)
-- =====================

-- Auto-create profile when new user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, role)
  VALUES (
    NEW.id,
    COALESCE(NEW.email, ''),
    COALESCE(NEW.raw_user_meta_data->>'full_name', COALESCE(NEW.email, '')),
    'admin'
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
EXCEPTION WHEN OTHERS THEN
  -- Log error but don't block user creation
  RAISE WARNING 'handle_new_user failed: %', SQLERRM;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- =====================
-- MIGRATION: Update existing records to 'admin' role
-- =====================
-- Run this query if you have existing users with 'student' role:
-- UPDATE profiles SET role = 'admin' WHERE role = 'student';

-- =====================
-- STUDENTS TABLE (separate from Supabase auth)
-- =====================
CREATE TABLE IF NOT EXISTS students (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id      TEXT UNIQUE NOT NULL,
  password_hash   TEXT NOT NULL,
  name            TEXT,
  email           TEXT,
  is_first_login  BOOLEAN DEFAULT TRUE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- AUDIT_RESULTS table (admin creates, student views)
CREATE TABLE IF NOT EXISTS audit_results (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id      TEXT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
  scan_id         UUID REFERENCES scans(id) ON DELETE SET NULL,
  program         TEXT NOT NULL,
  audit_level     INTEGER NOT NULL,
  result_json     JSONB NOT NULL,
  result_text     TEXT NOT NULL,
  eligible        BOOLEAN NOT NULL,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- REQUESTS table (review/appeal)
CREATE TABLE IF NOT EXISTS requests (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id      TEXT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
  audit_result_id UUID REFERENCES audit_results(id) ON DELETE SET NULL,
  message         TEXT NOT NULL,
  status          TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'approved', 'rejected')),
  admin_notes     TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- =====================
-- RLS POLICIES for student tables
-- =====================
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE requests ENABLE ROW LEVEL SECURITY;

-- Students: admin full access
CREATE POLICY "students_admin_select" ON students FOR SELECT USING (is_admin());
CREATE POLICY "students_admin_insert" ON students FOR INSERT WITH CHECK (is_admin());
CREATE POLICY "students_admin_update" ON students FOR UPDATE USING (is_admin());
CREATE POLICY "students_admin_delete" ON students FOR DELETE USING (is_admin());

-- Audit results: admin full access
CREATE POLICY "audit_results_admin_select" ON audit_results FOR SELECT USING (is_admin());
CREATE POLICY "audit_results_admin_insert" ON audit_results FOR INSERT WITH CHECK (is_admin());
CREATE POLICY "audit_results_admin_update" ON audit_results FOR UPDATE USING (is_admin());
CREATE POLICY "audit_results_admin_delete" ON audit_results FOR DELETE USING (is_admin());

-- Requests: admin full access
CREATE POLICY "requests_admin_select" ON requests FOR SELECT USING (is_admin());
CREATE POLICY "requests_admin_insert" ON requests FOR INSERT WITH CHECK (is_admin());
CREATE POLICY "requests_admin_update" ON requests FOR UPDATE USING (is_admin());
CREATE POLICY "requests_admin_delete" ON requests FOR DELETE USING (is_admin());
