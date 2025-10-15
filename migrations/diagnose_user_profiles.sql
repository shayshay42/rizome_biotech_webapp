-- Diagnostic queries to understand the current database state
-- Run these in Supabase SQL Editor to see what's wrong

-- 1. Check if user_profiles exists and what type it is
SELECT 
    schemaname,
    tablename,
    tableowner,
    'TABLE' as object_type
FROM pg_tables 
WHERE schemaname = 'public' AND tablename = 'user_profiles'
UNION ALL
SELECT 
    schemaname,
    viewname as tablename,
    viewowner as tableowner,
    'VIEW' as object_type
FROM pg_views 
WHERE schemaname = 'public' AND viewname = 'user_profiles';

-- 2. If it exists as a table, show its structure
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'user_profiles'
ORDER BY ordinal_position;

-- 3. Check for any constraints that might be failing
SELECT
    con.conname AS constraint_name,
    con.contype AS constraint_type,
    pg_get_constraintdef(con.oid) AS definition
FROM pg_constraint con
JOIN pg_class rel ON rel.oid = con.conrelid
JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
WHERE nsp.nspname = 'public'
  AND rel.relname = 'user_profiles';

-- 4. Check RLS status
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public' 
  AND tablename = 'user_profiles';

-- 5. Check what policies exist
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename = 'user_profiles';

-- 6. Try to see if we have the backup table
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename LIKE '%user_profile%';
