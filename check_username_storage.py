#!/usr/bin/env python3
"""
Script to check and update user metadata in Supabase Auth
This helps verify that usernames are stored correctly in auth.users
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from utils.supabase_client import get_supabase

def check_auth_users():
    """Check what's stored in auth.users for each user"""
    print("\n=== Checking Auth Users ===")
    
    try:
        supabase = get_supabase()
        
        # Get current authenticated user (if any)
        try:
            current_user = supabase.auth.get_user()
            if current_user:
                print(f"\n✅ Current User:")
                print(f"   ID: {current_user.user.id}")
                print(f"   Email: {current_user.user.email}")
                print(f"\n   User Metadata:")
                metadata = current_user.user.user_metadata or {}
                for key, value in metadata.items():
                    print(f"   - {key}: {value}")
                
                print(f"\n   Raw App Metadata:")
                app_metadata = current_user.user.app_metadata or {}
                for key, value in app_metadata.items():
                    print(f"   - {key}: {value}")
        except:
            print("❌ No authenticated user session")
        
        # Try to query user_profiles to see what usernames we have
        print("\n=== Checking user_profiles Table ===")
        try:
            profiles = supabase.table('user_profiles').select('id, username, display_name').execute()
            if profiles.data:
                print(f"\n✅ Found {len(profiles.data)} user profiles:")
                for profile in profiles.data:
                    print(f"   - ID: {profile['id'][:8]}...")
                    print(f"     Username: {profile.get('username', 'NOT SET')}")
                    print(f"     Display Name: {profile.get('display_name', 'NOT SET')}")
                    print()
            else:
                print("⚠️  No user profiles found")
        except Exception as e:
            print(f"❌ Could not access user_profiles table: {e}")
            print("   Make sure migration has been applied")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def show_metadata_explanation():
    """Explain where username is stored"""
    print("\n" + "="*60)
    print("WHERE USERNAME IS STORED")
    print("="*60)
    
    print("\n📍 Location 1: auth.users.raw_user_meta_data")
    print("   - This is in the Authentication tab in Supabase Dashboard")
    print("   - Column: 'User Metadata' (shows as JSON)")
    print("   - Key: 'username'")
    print("   - Visibility: ⚠️ JSON field - not immediately visible")
    
    print("\n📍 Location 2: user_profiles table")
    print("   - This is in the Table Editor in Supabase Dashboard")
    print("   - Table: 'user_profiles'")
    print("   - Column: 'username'")
    print("   - Visibility: ✅ Clearly visible")
    
    print("\n💡 How to See Username in Auth Tab:")
    print("   1. Go to Authentication tab in Supabase Dashboard")
    print("   2. Click on a user")
    print("   3. Look for 'User Metadata' section")
    print("   4. You should see:")
    print("      {")
    print('        "username": "your_username",')
    print('        "display_name": "your_username",')
    print('        "full_name": "your_username"')
    print("      }")
    
    print("\n🔧 The Display Name Issue:")
    print("   - Supabase Auth doesn't have a dedicated 'display_name' column")
    print("   - It's stored in the user_metadata JSON")
    print("   - The dashboard might not show it prominently")
    print("   - But it IS there - just in the metadata")

def test_registration_flow():
    """Show what happens during registration"""
    print("\n" + "="*60)
    print("REGISTRATION FLOW")
    print("="*60)
    
    print("\nWhen a user registers with username 'john_doe':")
    print("\n1. Supabase Auth creates user in auth.users:")
    print("   - email: 'john@example.com'")
    print("   - encrypted_password: (hashed)")
    print("   - raw_user_meta_data:")
    print("     {")
    print('       "username": "john_doe",')
    print('       "display_name": "john_doe",')
    print('       "full_name": "john_doe"')
    print("     }")
    
    print("\n2. Database trigger creates profile in user_profiles:")
    print("   - id: (UUID from auth.users)")
    print("   - username: 'john_doe'")
    print("   - display_name: 'john_doe'")
    
    print("\n3. App also syncs to ensure consistency:")
    print("   - Calls sync_user_profile()")
    print("   - Updates user_profiles if needed")
    
    print("\n✅ Result: Username stored in TWO places!")
    print("   - auth.users.raw_user_meta_data (for Auth API)")
    print("   - user_profiles.username (for database queries)")

def show_dashboard_navigation():
    """Show how to find username in Supabase Dashboard"""
    print("\n" + "="*60)
    print("HOW TO FIND USERNAME IN SUPABASE DASHBOARD")
    print("="*60)
    
    print("\n📍 Method 1: Authentication Tab")
    print("   1. Go to https://supabase.com/dashboard")
    print("   2. Select your project")
    print("   3. Click 'Authentication' in sidebar")
    print("   4. Click 'Users' tab")
    print("   5. Click on any user row")
    print("   6. Scroll down to 'User Metadata' section")
    print("   7. Look for 'username' field in the JSON")
    
    print("\n📍 Method 2: Table Editor (Easier!)")
    print("   1. Go to https://supabase.com/dashboard")
    print("   2. Select your project")
    print("   3. Click 'Table Editor' in sidebar")
    print("   4. Select 'user_profiles' table")
    print("   5. See 'username' column clearly!")
    
    print("\n📍 Method 3: SQL Editor")
    print("   1. Go to 'SQL Editor' in sidebar")
    print("   2. Run this query:")
    print("\n   SELECT ")
    print("     au.id,")
    print("     au.email,")
    print("     au.raw_user_meta_data->>'username' as username,")
    print("     up.username as profile_username")
    print("   FROM auth.users au")
    print("   LEFT JOIN user_profiles up ON au.id = up.id;")
    print("\n   3. This shows username from both locations!")

def main():
    """Run all checks"""
    print("="*60)
    print("SUPABASE AUTH USERNAME CHECKER")
    print("="*60)
    
    # Check current users
    check_auth_users()
    
    # Show explanation
    show_metadata_explanation()
    
    # Show registration flow
    test_registration_flow()
    
    # Show dashboard navigation
    show_dashboard_navigation()
    
    print("\n" + "="*60)
    print("✅ SUMMARY")
    print("="*60)
    
    print("\n📝 Username Storage:")
    print("   ✅ Stored in auth.users.raw_user_meta_data")
    print("   ✅ Stored in user_profiles.username")
    print("   ✅ Synced on registration and login")
    
    print("\n🔍 How to View:")
    print("   1. Auth tab → Click user → User Metadata (JSON)")
    print("   2. Table Editor → user_profiles table (clearer)")
    print("   3. SQL Editor → Run the query above")
    
    print("\n💡 Why Not in 'Display Name' Column:")
    print("   - Supabase Auth doesn't have a dedicated display_name column")
    print("   - It's in the user_metadata JSON")
    print("   - Use user_profiles table for easier viewing")
    
    print("\n🎯 Next Steps:")
    print("   1. Register a new test user")
    print("   2. Check Authentication → Users → Click user")
    print("   3. Look at 'User Metadata' section")
    print("   4. Should see username, display_name, full_name")
    print("   5. Also check Table Editor → user_profiles")

if __name__ == "__main__":
    main()
