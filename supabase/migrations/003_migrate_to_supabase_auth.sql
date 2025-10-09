-- Migration to fully integrate Supabase Auth
-- This removes the legacy users table and properly links to auth.users

-- Step 1: Drop old foreign key constraints
ALTER TABLE questionnaires DROP CONSTRAINT IF EXISTS questionnaires_user_id_fkey;
ALTER TABLE cbc_results DROP CONSTRAINT IF EXISTS cbc_results_user_id_fkey;

-- Step 2: Change user_id columns to UUID type (matching Supabase Auth)
-- First, we need to handle existing data if any
-- For new installations, this will be clean
-- For existing data, you may need to manually migrate users

ALTER TABLE questionnaires 
    ALTER COLUMN user_id TYPE UUID USING user_id::text::uuid;

ALTER TABLE cbc_results 
    ALTER COLUMN user_id TYPE UUID USING user_id::text::uuid;

-- Note: This creates a reference to auth.users (Supabase's internal table)
ALTER TABLE questionnaires 
    ADD CONSTRAINT questionnaires_user_id_fkey 
    FOREIGN KEY (user_id) 
    REFERENCES auth.users(id) 
    ON DELETE CASCADE;

ALTER TABLE cbc_results 
    ADD CONSTRAINT cbc_results_user_id_fkey 
    FOREIGN KEY (user_id) 
    REFERENCES auth.users(id) 
    ON DELETE CASCADE;

-- Step 4: Create a user_profiles table to store additional user information
-- This complements Supabase Auth with app-specific data
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username VARCHAR(50) UNIQUE,
    display_name VARCHAR(100),
    bio TEXT,
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 5: Create function to automatically create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id, username, display_name)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'username', split_part(NEW.email, '@', 1)),
        COALESCE(NEW.raw_user_meta_data->>'username', split_part(NEW.email, '@', 1))
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 6: Create trigger to call the function on new user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Step 7: Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_username ON user_profiles(username);
CREATE INDEX IF NOT EXISTS idx_questionnaires_user_id ON questionnaires(user_id);
CREATE INDEX IF NOT EXISTS idx_cbc_results_user_id ON cbc_results(user_id);

-- Step 8: Enable Row Level Security (RLS) for user_profiles
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Users can view their own profile
CREATE POLICY "Users can view own profile" 
    ON user_profiles 
    FOR SELECT 
    USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" 
    ON user_profiles 
    FOR UPDATE 
    USING (auth.uid() = id);

-- Step 9: Enable RLS for questionnaires
ALTER TABLE questionnaires ENABLE ROW LEVEL SECURITY;

-- Users can view their own questionnaires
CREATE POLICY "Users can view own questionnaires" 
    ON questionnaires 
    FOR SELECT 
    USING (auth.uid() = user_id);

-- Users can insert their own questionnaires
CREATE POLICY "Users can insert own questionnaires" 
    ON questionnaires 
    FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own questionnaires
CREATE POLICY "Users can update own questionnaires" 
    ON questionnaires 
    FOR UPDATE 
    USING (auth.uid() = user_id);

-- Step 10: Enable RLS for cbc_results
ALTER TABLE cbc_results ENABLE ROW LEVEL SECURITY;

-- Users can view their own CBC results
CREATE POLICY "Users can view own cbc_results" 
    ON cbc_results 
    FOR SELECT 
    USING (auth.uid() = user_id);

-- Users can insert their own CBC results
CREATE POLICY "Users can insert own cbc_results" 
    ON cbc_results 
    FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own CBC results
CREATE POLICY "Users can update own cbc_results" 
    ON cbc_results 
    FOR UPDATE 
    USING (auth.uid() = user_id);

-- Step 11: Update questionnaires table to match current schema
-- Add missing columns that are used in the app
ALTER TABLE questionnaires 
    ADD COLUMN IF NOT EXISTS age INTEGER,
    ADD COLUMN IF NOT EXISTS weight REAL,
    ADD COLUMN IF NOT EXISTS height REAL,
    ADD COLUMN IF NOT EXISTS sex VARCHAR(20),
    ADD COLUMN IF NOT EXISTS activity_level VARCHAR(50),
    ADD COLUMN IF NOT EXISTS smoking VARCHAR(20),
    ADD COLUMN IF NOT EXISTS chronic_conditions TEXT,
    ADD COLUMN IF NOT EXISTS medications TEXT,
    ADD COLUMN IF NOT EXISTS family_history TEXT,
    ADD COLUMN IF NOT EXISTS symptoms TEXT,
    ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Step 12: Update cbc_results table to match current schema
ALTER TABLE cbc_results 
    ADD COLUMN IF NOT EXISTS extraction_success BOOLEAN DEFAULT true,
    ADD COLUMN IF NOT EXISTS raw_extraction_data JSONB,
    ADD COLUMN IF NOT EXISTS risk_score REAL,
    ADD COLUMN IF NOT EXISTS risk_interpretation JSONB,
    ADD COLUMN IF NOT EXISTS cbc_vector TEXT;

-- Step 13: Drop the old users table (no longer needed)
-- IMPORTANT: Only run this after migrating any existing data!
-- Uncomment the line below when you're ready
-- DROP TABLE IF EXISTS users CASCADE;

-- Step 14: Add comments for documentation
COMMENT ON TABLE user_profiles IS 'User profile data complementing Supabase Auth';
COMMENT ON COLUMN user_profiles.username IS 'User chosen username, synced from auth metadata';
COMMENT ON COLUMN user_profiles.preferences IS 'JSON object for user preferences and settings';

-- Step 15: Create helper function to get username from user_id
CREATE OR REPLACE FUNCTION public.get_username(user_uuid UUID)
RETURNS TEXT AS $$
    SELECT username FROM public.user_profiles WHERE id = user_uuid;
$$ LANGUAGE SQL STABLE;

-- Step 16: Create view for easy user data access
CREATE OR REPLACE VIEW public.user_details AS
SELECT 
    au.id,
    au.email,
    au.created_at as auth_created_at,
    au.last_sign_in_at,
    au.email_confirmed_at,
    up.username,
    up.display_name,
    up.bio,
    up.avatar_url,
    up.preferences,
    up.created_at as profile_created_at,
    up.updated_at as profile_updated_at
FROM 
    auth.users au
    LEFT JOIN public.user_profiles up ON au.id = up.id;

-- Grant access to the view
GRANT SELECT ON public.user_details TO authenticated;

COMMENT ON VIEW public.user_details IS 'Combined view of auth.users and user_profiles for easy access';
