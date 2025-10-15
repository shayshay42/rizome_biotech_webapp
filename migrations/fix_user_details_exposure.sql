-- Migration: Fix public.user_details security exposure
-- Issue: View may expose auth.users sensitive data to anon/authenticated roles
-- Solution: Replace with a secure view that only shows user's own public profile

-- ============================================================================
-- STEP 1: Drop the existing insecure view
-- ============================================================================
DROP VIEW IF EXISTS public.user_details CASCADE;

-- ============================================================================
-- STEP 2: Create a secure replacement that enforces auth.uid() filtering
-- ============================================================================
CREATE OR REPLACE VIEW public.user_profiles AS
SELECT 
    id,
    email,
    created_at,
    -- Only include safe metadata fields; avoid raw_user_metadata/raw_app_metadata
    (raw_user_metadata->>'display_name')::text AS display_name,
    (raw_user_metadata->>'avatar_url')::text AS avatar_url
FROM auth.users
WHERE id = auth.uid()  -- Critical: users can only see their own record
WITH CHECK OPTION;

-- ============================================================================
-- STEP 3: Lock down privileges
-- ============================================================================
-- Revoke all default access
REVOKE ALL ON public.user_profiles FROM PUBLIC;
REVOKE ALL ON public.user_profiles FROM anon;
REVOKE ALL ON public.user_profiles FROM authenticated;

-- Grant SELECT only to authenticated users (RLS enforces auth.uid() filter)
GRANT SELECT ON public.user_profiles TO authenticated;

-- ============================================================================
-- STEP 4: Enable RLS on the view (defense in depth)
-- ============================================================================
ALTER VIEW public.user_profiles SET (security_barrier = true);

-- ============================================================================
-- STEP 5: Optional - Create a safe public profile view (if needed)
-- ============================================================================
-- If you need a truly public profile view (e.g., for team pages), create:
CREATE OR REPLACE VIEW public.public_user_profiles AS
SELECT 
    id,
    (raw_user_metadata->>'display_name')::text AS display_name,
    (raw_user_metadata->>'avatar_url')::text AS avatar_url,
    (raw_user_metadata->>'public_bio')::text AS public_bio
FROM auth.users
WHERE (raw_user_metadata->>'is_public')::boolean = true;  -- Only public profiles

REVOKE ALL ON public.public_user_profiles FROM PUBLIC;
GRANT SELECT ON public.public_user_profiles TO anon, authenticated;

-- ============================================================================
-- STEP 6: Create a SECURITY DEFINER function for admin queries (optional)
-- ============================================================================
-- If backend needs to query all users (e.g., admin panel), use:
CREATE OR REPLACE FUNCTION public.admin_get_user_details(target_user_id uuid)
RETURNS TABLE (
    id uuid,
    email text,
    created_at timestamptz,
    display_name text
)
LANGUAGE sql
SECURITY DEFINER  -- Runs with view owner's privileges
SET search_path = public, auth
AS $$
    -- Add authorization check here (e.g., is_admin role)
    SELECT 
        u.id,
        u.email,
        u.created_at,
        (u.raw_user_metadata->>'display_name')::text
    FROM auth.users u
    WHERE u.id = target_user_id;
$$;

REVOKE EXECUTE ON FUNCTION public.admin_get_user_details FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.admin_get_user_details TO service_role;

-- ============================================================================
-- VALIDATION QUERIES (Run these to confirm security)
-- ============================================================================
-- 1. Verify anon cannot access user_profiles:
--    SET ROLE anon;
--    SELECT * FROM public.user_profiles;  -- Should return 0 rows or error
--    RESET ROLE;

-- 2. Verify authenticated user sees only their own row:
--    SET ROLE authenticated;
--    SET request.jwt.claims.sub = '<some-user-uuid>';
--    SELECT * FROM public.user_profiles;  -- Should return 1 row (their own)
--    RESET ROLE;

-- 3. Confirm public_user_profiles only shows opted-in users:
--    SELECT * FROM public.public_user_profiles;

-- ============================================================================
-- ROLLBACK (if needed)
-- ============================================================================
-- DROP VIEW IF EXISTS public.user_profiles CASCADE;
-- DROP VIEW IF EXISTS public.public_user_profiles CASCADE;
-- DROP FUNCTION IF EXISTS public.admin_get_user_details CASCADE;
-- -- Recreate original view if you have the DDL saved
