"""
Interactive database repair with service role key
This will prompt you for the service role key and fix the database
"""

import sys
import os
from getpass import getpass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from supabase import create_client

def fix_user_profiles_table(service_key: str):
    """Fix the user_profiles table using service role key"""
    
    url = "https://kqzmwzosluljckadthup.supabase.co"
    
    print("\n🔧 Connecting to Supabase with service role...")
    try:
        admin = create_client(url, service_key)
        print("✅ Connected successfully")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # SQL to restore the table
    sql = """
DO $$
BEGIN
    -- Drop the broken view
    DROP VIEW IF EXISTS public.user_profiles CASCADE;
    
    -- Restore from backup if it exists
    IF EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = 'user_profiles_table_backup'
    ) THEN
        ALTER TABLE public.user_profiles_table_backup RENAME TO user_profiles;
        RAISE NOTICE 'Restored from backup';
    END IF;
    
    -- Create table if it doesn't exist
    CREATE TABLE IF NOT EXISTS public.user_profiles (
        id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
        username TEXT UNIQUE,
        display_name TEXT,
        avatar_url TEXT,
        bio TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    -- Create index
    CREATE INDEX IF NOT EXISTS idx_user_profiles_username 
    ON public.user_profiles(username);
    
    -- Create updated_at trigger
    CREATE OR REPLACE FUNCTION public.handle_user_profiles_updated_at()
    RETURNS TRIGGER AS $func$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $func$ LANGUAGE plpgsql;
    
    DROP TRIGGER IF EXISTS set_user_profiles_updated_at ON public.user_profiles;
    CREATE TRIGGER set_user_profiles_updated_at
        BEFORE UPDATE ON public.user_profiles
        FOR EACH ROW
        EXECUTE FUNCTION public.handle_user_profiles_updated_at();
    
    -- Disable RLS for now (we can re-enable with proper policies later)
    ALTER TABLE public.user_profiles DISABLE ROW LEVEL SECURITY;
    
    -- Grant permissions
    GRANT ALL ON public.user_profiles TO authenticated;
    GRANT ALL ON public.user_profiles TO service_role;
    GRANT ALL ON public.user_profiles TO anon;
END
$$;
"""
    
    print("\n🔨 Executing repair SQL...")
    try:
        # Execute using postgrest-py - we need to use the SQL editor endpoint
        # Since postgrest doesn't have direct SQL execution, we'll use the REST API
        import requests
        
        response = requests.post(
            f"{url}/rest/v1/rpc/exec_sql",
            headers={
                "apikey": service_key,
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json"
            },
            json={"query": sql}
        )
        
        if response.status_code == 404:
            print("⚠️  Direct SQL execution via RPC not available")
            print("\n📋 Please run this SQL manually in Supabase SQL Editor:")
            print("=" * 60)
            print(sql)
            print("=" * 60)
            return None
        elif response.status_code >= 400:
            print(f"❌ SQL execution failed: {response.text}")
            return False
        else:
            print("✅ SQL executed successfully")
            
    except Exception as e:
        print(f"⚠️  Could not execute SQL automatically: {e}")
        print("\n📋 Please run this SQL manually in Supabase SQL Editor:")
        print("=" * 60)
        print(sql)
        print("=" * 60)
        return None
    
    # Verify the fix
    print("\n✅ Verifying table is working...")
    try:
        result = admin.table('user_profiles').select('*').limit(1).execute()
        print(f"✅ Table is now accessible!")
        print(f"   Found {len(result.data)} existing profiles")
        return True
    except Exception as e:
        print(f"❌ Table still not accessible: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("SUPABASE DATABASE REPAIR TOOL")
    print("=" * 60)
    print("\nThis tool will restore the user_profiles TABLE")
    print("(it's currently a broken VIEW)")
    print("\nYou need your Supabase SERVICE ROLE KEY (not the anon key)")
    print("Find it at: https://supabase.com/dashboard/project/kqzmwzosluljckadthup/settings/api")
    print("\n⚠️  The service role key will NOT be saved or displayed")
    
    service_key = getpass("\nEnter your Supabase service role key: ")
    
    if not service_key or len(service_key) < 100:
        print("❌ Invalid service key (too short)")
        return
    
    result = fix_user_profiles_table(service_key)
    
    if result is True:
        print("\n" + "=" * 60)
        print("✅ DATABASE REPAIRED SUCCESSFULLY!")
        print("=" * 60)
        print("\nYou can now test registration in your app")
    elif result is False:
        print("\n" + "=" * 60)
        print("❌ AUTOMATIC REPAIR FAILED")
        print("=" * 60)
        print("\nPlease run the SQL manually from:")
        print("  streamlit_app/migrations/emergency_restore_user_profiles.sql")
    else:
        print("\n" + "=" * 60)
        print("⚠️  MANUAL SQL REQUIRED")
        print("=" * 60)
        print("\nThe SQL has been displayed above.")
        print("Copy it and run in: https://supabase.com/dashboard/project/kqzmwzosluljckadthup/sql/new")

if __name__ == '__main__':
    main()
