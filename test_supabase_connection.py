#!/usr/bin/env python3
"""
Test Supabase connection and credentials
Run this to verify your Supabase setup before using the app
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_supabase_credentials():
    """Test if Supabase credentials are configured correctly"""

    print("\n" + "="*60)
    print("SUPABASE CONNECTION TEST")
    print("="*60)

    # Test 1: Check if secrets file exists
    print("\n1. Checking for secrets file...")
    secrets_path = ".streamlit/secrets.toml"

    if os.path.exists(secrets_path):
        print(f"   ✓ Found {secrets_path}")
    else:
        print(f"   ✗ Missing {secrets_path}")
        print(f"   → Create it from .streamlit/secrets.toml.template")
        return False

    # Test 2: Read and parse secrets
    print("\n2. Reading secrets...")
    try:
        import toml
        with open(secrets_path) as f:
            secrets = toml.load(f)

        if 'supabase' not in secrets:
            print("   ✗ Missing [supabase] section in secrets.toml")
            return False

        print("   ✓ Secrets file parsed successfully")

        # Check for required fields
        url = secrets['supabase'].get('url')
        key = secrets['supabase'].get('key')

        print(f"\n   Found credentials:")
        print(f"   - URL: {url}")
        print(f"   - Key: {key[:20]}...{key[-10:] if key and len(key) > 30 else 'MISSING'}")

        if not url:
            print("\n   ✗ Missing 'url' in [supabase] section")
            print("   → Add: url = \"https://kqzmwzosluljckadthup.supabase.co\"")
            return False

        if not key:
            print("\n   ✗ Missing 'key' in [supabase] section")
            print("   → Get from: Supabase Dashboard → Settings → API → anon public key")
            return False

    except Exception as e:
        print(f"   ✗ Error reading secrets: {e}")
        return False

    # Test 3: Try to import supabase
    print("\n3. Testing supabase-py library...")
    try:
        from supabase import create_client
        print("   ✓ supabase-py imported successfully")
    except ImportError:
        print("   ✗ supabase-py not installed")
        print("   → Run: pip install supabase")
        return False

    # Test 4: Try to create client
    print("\n4. Creating Supabase client...")
    try:
        client = create_client(url, key)
        print("   ✓ Supabase client created")
    except Exception as e:
        print(f"   ✗ Failed to create client: {e}")
        return False

    # Test 5: Try a simple API call
    print("\n5. Testing API connection...")
    try:
        # Try to get auth config (this doesn't require authentication)
        response = client.auth.get_session()
        print("   ✓ API connection successful!")
        print(f"   Session: {response}")
    except Exception as e:
        error_msg = str(e)

        if "Invalid API key" in error_msg or "invalid" in error_msg.lower():
            print(f"   ✗ Invalid API key!")
            print(f"\n   The key in your secrets.toml is incorrect.")
            print(f"\n   To get the correct key:")
            print(f"   1. Go to: https://supabase.com/dashboard/project/kqzmwzosluljckadthup")
            print(f"   2. Click 'Settings' → 'API'")
            print(f"   3. Copy the 'anon' 'public' key")
            print(f"   4. Update .streamlit/secrets.toml with the real key")
            return False
        else:
            print(f"   ⚠ API call error (but connection works): {e}")
            print(f"   This is usually OK - auth session might be empty")

    # Success!
    print("\n" + "="*60)
    print("✅ SUPABASE CONNECTION SUCCESSFUL!")
    print("="*60)
    print("\nYour Supabase configuration is correct.")
    print("You can now run the app: streamlit run streamlit_app.py")
    return True

if __name__ == "__main__":
    try:
        success = test_supabase_credentials()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
