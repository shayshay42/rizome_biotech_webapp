-- Emergency fix: Restore user_profiles TABLE (it's currently a broken VIEW)
-- Run this in Supabase SQL Editor to restore registration functionality
-- 
-- DIAGNOSIS: user_profiles is a VIEW with permission issues, needs to be a TABLE

-- Step 1: Drop the broken view that's blocking registration
DROP VIEW IF EXISTS public.user_profiles CASCADE;

-- Step 2: If there's a backup table, restore it
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_tables 
    WHERE schemaname = 'public' 
    AND tablename = 'user_profiles_table_backup'
  ) THEN
    ALTER TABLE public.user_profiles_table_backup RENAME TO user_profiles;
    RAISE NOTICE 'Restored user_profiles from backup';
  END IF;
END
$$;

-- Step 3: Create the table if it still doesn't exist
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT UNIQUE,
    display_name TEXT,
    avatar_url TEXT,
    bio TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Step 4: Create index for fast username lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_username 
ON public.user_profiles(username);

-- Step 5: Create trigger for updated_at
CREATE OR REPLACE FUNCTION public.handle_user_profiles_updated_at()
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
    EXECUTE FUNCTION public.handle_user_profiles_updated_at();

-- Step 6: Disable RLS temporarily for testing (you can re-enable later)
ALTER TABLE public.user_profiles DISABLE ROW LEVEL SECURITY;

-- Step 7: Grant necessary permissions
GRANT ALL ON public.user_profiles TO authenticated;
GRANT ALL ON public.user_profiles TO service_role;

-- Step 8: Create a trigger to auto-create profile on user signup (optional but recommended)
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (id, username, display_name)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'username', NEW.email),
    COALESCE(NEW.raw_user_meta_data->>'display_name', NEW.raw_user_meta_data->>'username', NEW.email)
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- Verification
SELECT 'user_profiles table ready!' as status,
       COUNT(*) as existing_profiles
FROM public.user_profiles;
