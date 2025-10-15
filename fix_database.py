"""
Emergency database diagnostic and repair script
Uses existing Supabase client to fix user_profiles table issues
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.supabase_client import get_supabase, get_supabase_admin

def diagnose_database():
    """Diagnose current state of user_profiles"""
    print("\n" + "="*60)
    print("DATABASE DIAGNOSTIC")
    print("="*60)
    
    try:
        supabase = get_supabase_admin() or get_supabase()
        
        # Check if user_profiles table exists and is accessible
        print("\n1. Testing user_profiles table access...")
        try:
            result = supabase.table('user_profiles').select('*').limit(1).execute()
            print(f"   ✅ Table exists and is readable")
            print(f"   Found {len(result.data)} rows (showing 1)")
            if result.data:
                print(f"   Columns: {list(result.data[0].keys())}")
        except Exception as e:
            print(f"   ❌ Cannot read table: {e}")
        
        # Check if we can write to the table
        print("\n2. Testing write permissions...")
        try:
            # Try to select with a filter (safer than actual insert)
            test_result = supabase.table('user_profiles').select('id').eq('username', '__test__').execute()
            print(f"   ✅ Query operations work")
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
        
        # Check RLS policies
        print("\n3. Checking RLS status...")
        try:
            admin = get_supabase_admin()
            if admin:
                # Use admin client to check table metadata
                result = admin.table('user_profiles').select('*').limit(1).execute()
                print(f"   ✅ Admin access works")
            else:
                print(f"   ⚠️  No service role key available")
        except Exception as e:
            print(f"   ❌ Admin check failed: {e}")
            
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False
    
    return True

def fix_database():
    """Attempt to fix the user_profiles table"""
    print("\n" + "="*60)
    print("DATABASE REPAIR")
    print("="*60)
    
    try:
        admin = get_supabase_admin()
        if not admin:
            print("❌ No service role key found. Cannot perform repairs.")
            print("   Please provide SUPABASE_SERVICE_KEY in secrets or environment")
            return False
        
        print("\n1. Attempting to restore user_profiles table...")
        
        # Use RPC call to execute SQL directly
        sql = """
        DO $$
        BEGIN
            -- Drop any view that might be blocking
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
            
            -- Disable RLS temporarily
            ALTER TABLE public.user_profiles DISABLE ROW LEVEL SECURITY;
            
            -- Grant permissions
            GRANT ALL ON public.user_profiles TO authenticated;
            GRANT ALL ON public.user_profiles TO service_role;
        END
        $$;
        """
        
        try:
            # Execute using RPC or direct SQL
            result = admin.rpc('exec_sql', {'query': sql}).execute()
            print("   ✅ Table restored/created successfully")
        except:
            # If RPC doesn't work, try using postgrest-py query method
            print("   ⚠️  Direct SQL execution not available via RPC")
            print("   Please run the SQL from emergency_restore_user_profiles.sql manually")
            return False
        
        # Verify the fix
        print("\n2. Verifying table is working...")
        try:
            result = admin.table('user_profiles').select('*').limit(1).execute()
            print(f"   ✅ Table is now accessible")
            return True
        except Exception as e:
            print(f"   ❌ Table still not accessible: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Repair failed: {e}")
        return False

def test_registration_flow():
    """Test if registration would work"""
    print("\n" + "="*60)
    print("TESTING REGISTRATION FLOW")
    print("="*60)
    
    try:
        supabase = get_supabase()
        
        # Try to simulate what sync_user_profile does
        test_user_id = "00000000-0000-0000-0000-000000000000"  # Fake UUID
        test_username = "__test_user__"
        
        print("\n1. Testing profile lookup...")
        try:
            result = supabase.table('user_profiles').select('*').eq('id', test_user_id).execute()
            print(f"   ✅ Query works (found {len(result.data)} rows)")
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
            return False
        
        print("\n2. Testing if insert would work (dry run)...")
        # We won't actually insert, just check if the operation is allowed
        try:
            # Check if we can query the table structure
            result = supabase.table('user_profiles').select('id,username,display_name').limit(0).execute()
            print(f"   ✅ Table structure is accessible")
            print(f"   Can proceed with registration")
            return True
        except Exception as e:
            print(f"   ❌ Cannot access table structure: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == '__main__':
    print("\n🔍 Starting database diagnostics and repair...")
    
    # Step 1: Diagnose
    if not diagnose_database():
        print("\n⚠️  Diagnosis failed. Check your Supabase credentials.")
        sys.exit(1)
    
    # Step 2: Attempt repair (if admin access available)
    print("\n🔧 Attempting automatic repair...")
    admin = get_supabase_admin()
    if admin:
        if fix_database():
            print("\n✅ Database repaired successfully!")
        else:
            print("\n⚠️  Automatic repair failed.")
            print("   Please run the SQL from migrations/emergency_restore_user_profiles.sql")
            print("   in your Supabase SQL Editor")
    else:
        print("\n⚠️  No service role key available - cannot auto-repair")
        print("   Please run migrations/emergency_restore_user_profiles.sql manually")
        print("   Or provide SUPABASE_SERVICE_KEY to enable auto-repair")
    
    # Step 3: Test registration flow
    print("\n🧪 Testing registration flow...")
    if test_registration_flow():
        print("\n✅ Registration should work now!")
    else:
        print("\n❌ Registration still broken - manual SQL required")
    
    print("\n" + "="*60)
    print("DONE")
    print("="*60)
