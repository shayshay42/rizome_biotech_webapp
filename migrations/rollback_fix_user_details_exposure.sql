-- Rollback script for fix_user_details_exposure migration
-- Run this if you need to undo the security fix

-- Remove RLS policies
DROP POLICY IF EXISTS "Users can read own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Service role has full access" ON public.user_profiles;

-- Disable RLS (WARNING: This makes the table less secure)
-- ALTER TABLE public.user_profiles DISABLE ROW LEVEL SECURITY;

-- Drop the safe auth view
DROP VIEW IF EXISTS public.auth_user_profiles_view CASCADE;

-- Note: We don't recreate user_details view as it was insecure
-- If you need it back, you'll need to provide the original DDL
