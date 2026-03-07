-- Supabase Schema for NSU Audit Core Phase 2

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
