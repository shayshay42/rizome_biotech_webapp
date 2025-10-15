-- Fix existing RLS policies by dropping and recreating them
-- This handles the case where policies already exist

BEGIN;

-- 1. Drop ALL existing policies for questionnaires
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE schemaname = 'public' AND tablename = 'questionnaires')
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.questionnaires', r.policyname);
    END LOOP;
END $$;

-- 2. Drop ALL existing policies for cbc_results
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE schemaname = 'public' AND tablename = 'cbc_results')
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.cbc_results', r.policyname);
    END LOOP;
END $$;

-- 3. Enable RLS
ALTER TABLE public.questionnaires ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cbc_results ENABLE ROW LEVEL SECURITY;

-- 4. Create new permissive policies for questionnaires
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

-- 5. Create new permissive policies for cbc_results
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

-- 6. Grant necessary permissions
GRANT ALL ON public.questionnaires TO authenticated;
GRANT ALL ON public.cbc_results TO authenticated;
GRANT ALL ON public.questionnaires TO service_role;
GRANT ALL ON public.cbc_results TO service_role;

COMMIT;

-- Verification
SELECT 'questionnaires policies:' as info, schemaname, tablename, policyname, cmd
FROM pg_policies
WHERE schemaname = 'public' AND tablename = 'questionnaires';

SELECT 'cbc_results policies:' as info, schemaname, tablename, policyname, cmd
FROM pg_policies
WHERE schemaname = 'public' AND tablename = 'cbc_results';
