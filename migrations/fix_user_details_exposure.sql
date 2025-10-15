-- Migration: Fix public.user_details security exposure
-- Issue: View may expose auth.users sensitive data to anon/authenticated roles
-- Solution: Drop the insecure view, keep user_profiles table for app functionality

-- ============================================================================
-- STEP 0: Restore user_profiles table if it was renamed
-- ============================================================================
DO $$
BEGIN
  -- If we previously renamed the table, restore it
  IF EXISTS (
    SELECT 1 FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'user_profiles_table_backup'
      AND n.nspname = 'public'
      AND c.relkind = 'r'
  ) THEN
    RAISE NOTICE 'Restoring user_profiles table from backup';
    -- Drop any view that might be using the name
    EXECUTE 'DROP VIEW IF EXISTS public.user_profiles CASCADE';
    -- Restore the table
    EXECUTE 'ALTER TABLE public.user_profiles_table_backup RENAME TO user_profiles';
  END IF;
END
$$;

-- ============================================================================
-- STEP 1: Drop ONLY the insecure user_details view
-- ============================================================================
-- This is the view that was exposing auth.users data
DROP VIEW IF EXISTS public.user_details CASCADE;

-- ============================================================================
-- STEP 2: Ensure user_profiles table has RLS enabled
-- ============================================================================
-- The user_profiles table should already exist from your app's setup
-- We just need to make sure it has proper RLS policies

-- Enable RLS if not already enabled
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Drop any overly permissive policies
DROP POLICY IF EXISTS "Users can read own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON public.user_profiles;

-- Create secure policies that enforce auth.uid() filtering
CREATE POLICY "Users can read own profile"
  ON public.user_profiles
  FOR SELECT
  TO authenticated
  USING (id = auth.uid());

CREATE POLICY "Users can update own profile"
  ON public.user_profiles
  FOR UPDATE
  TO authenticated
  USING (id = auth.uid())
  WITH CHECK (id = auth.uid());

CREATE POLICY "Users can insert own profile"
  ON public.user_profiles
  FOR INSERT
  TO authenticated
  WITH CHECK (id = auth.uid());

-- Service role needs full access for admin operations
CREATE POLICY "Service role has full access"
  ON public.user_profiles
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- ============================================================================
-- STEP 3: Create a safe read-only view of auth.users (if needed)
-- ============================================================================
-- If you need to query auth.users data safely, use a properly named view
-- (avoid reusing user_profiles name to prevent confusion with the table)
DROP VIEW IF EXISTS public.auth_user_profiles_view CASCADE;
CREATE VIEW public.auth_user_profiles_view AS
SELECT 
    id,
    email,
    created_at,
    (raw_user_meta_data->>'display_name')::text AS display_name,
    (raw_user_meta_data->>'avatar_url')::text AS avatar_url
FROM auth.users
WHERE id = auth.uid();  -- Users can only see their own auth data

REVOKE ALL ON public.auth_user_profiles_view FROM PUBLIC;
GRANT SELECT ON public.auth_user_profiles_view TO authenticated;

-- ============================================================================
-- STEP 4: Verify table structure (create if missing)
-- ============================================================================
-- In case user_profiles table doesn't exist, create it with proper schema
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT UNIQUE,
    display_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for username lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_username ON public.user_profiles(username);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION public.update_user_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_user_profiles_updated_at ON public.user_profiles;
CREATE TRIGGER set_user_profiles_updated_at
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.update_user_profiles_updated_at();

-- ============================================================================
-- VALIDATION QUERIES (Run these to confirm security)
-- ============================================================================
-- 1. Verify user_profiles table exists and has RLS:
--    SELECT tablename, rowsecurity FROM pg_tables 
--    WHERE schemaname = 'public' AND tablename = 'user_profiles';
--    -- Should show rowsecurity = true
--
-- 2. Verify RLS policies are active:
--    SELECT schemaname, tablename, policyname, roles, cmd 
--    FROM pg_policies 
--    WHERE tablename = 'user_profiles';
--
-- 3. Test as authenticated user (should only see own profile):
--    SET ROLE authenticated;
--    SET request.jwt.claims.sub = '<test-user-uuid>';
--    SELECT * FROM public.user_profiles;  -- Should return 1 row max
--    RESET ROLE;
--
-- 4. Verify insecure view is gone:
--    \dv public.user_details  -- Should not exist

-- ============================================================================
-- SUMMARY
-- ============================================================================
-- ✅ Dropped insecure user_details view that exposed auth.users
-- ✅ Kept user_profiles TABLE for app registration/profile functionality
-- ✅ Added RLS policies to user_profiles table (users see only their own data)
-- ✅ Created safe auth_user_profiles_view for read-only auth.users access
-- ✅ App registration will now work correctly
