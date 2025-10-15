-- Fix RLS policies for questionnaires and cbc_results tables
-- These tables need policies to allow authenticated users to insert their own data

-- 1. Fix questionnaires table
-- Drop existing restrictive policies
DROP POLICY IF EXISTS "Users can only view their own questionnaires" ON public.questionnaires;
DROP POLICY IF EXISTS "Users can only insert their own questionnaires" ON public.questionnaires;
DROP POLICY IF EXISTS "Users can only update their own questionnaires" ON public.questionnaires;
DROP POLICY IF EXISTS "Users can only delete their own questionnaires" ON public.questionnaires;

-- Enable RLS
ALTER TABLE public.questionnaires ENABLE ROW LEVEL SECURITY;

-- Create permissive policies for authenticated users
CREATE POLICY "Allow authenticated users to insert their own questionnaires"
ON public.questionnaires
FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Allow authenticated users to view their own questionnaires"
ON public.questionnaires
FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Allow authenticated users to update their own questionnaires"
ON public.questionnaires
FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Allow authenticated users to delete their own questionnaires"
ON public.questionnaires
FOR DELETE
TO authenticated
USING (auth.uid() = user_id);

-- 2. Fix cbc_results table
-- Drop existing restrictive policies
DROP POLICY IF EXISTS "Users can only view their own cbc_results" ON public.cbc_results;
DROP POLICY IF EXISTS "Users can only insert their own cbc_results" ON public.cbc_results;
DROP POLICY IF EXISTS "Users can only update their own cbc_results" ON public.cbc_results;
DROP POLICY IF EXISTS "Users can only delete their own cbc_results" ON public.cbc_results;

-- Enable RLS
ALTER TABLE public.cbc_results ENABLE ROW LEVEL SECURITY;

-- Create permissive policies for authenticated users
CREATE POLICY "Allow authenticated users to insert their own cbc_results"
ON public.cbc_results
FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Allow authenticated users to view their own cbc_results"
ON public.cbc_results
FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Allow authenticated users to update their own cbc_results"
ON public.cbc_results
FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Allow authenticated users to delete their own cbc_results"
ON public.cbc_results
FOR DELETE
TO authenticated
USING (auth.uid() = user_id);

-- Grant necessary permissions
GRANT ALL ON public.questionnaires TO authenticated;
GRANT ALL ON public.cbc_results TO authenticated;
GRANT ALL ON public.questionnaires TO service_role;
GRANT ALL ON public.cbc_results TO service_role;

-- Verification
SELECT 'questionnaires policies:' as status;
SELECT schemaname, tablename, policyname, cmd
FROM pg_policies
WHERE schemaname = 'public' AND tablename = 'questionnaires';

SELECT 'cbc_results policies:' as status;
SELECT schemaname, tablename, policyname, cmd
FROM pg_policies
WHERE schemaname = 'public' AND tablename = 'cbc_results';
