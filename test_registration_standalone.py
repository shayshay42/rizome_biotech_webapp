#!/usr/bin/env python3
"""
Standalone test of Supabase registration (no Streamlit)
"""

from supabase import create_client
import toml

# Load secrets
with open('.streamlit/secrets.toml') as f:
    secrets = toml.load(f)

url = secrets['supabase']['url']
key = secrets['supabase']['key']

print("="*60)
print("TESTING SUPABASE REGISTRATION")
print("="*60)

print(f"\nURL: {url}")
print(f"Key: {key[:20]}...{key[-10:]}")

# Create client
print("\n1. Creating Supabase client...")
client = create_client(url, key)
print("   ✓ Client created")

# Try to register a test user
print("\n2. Attempting to register test user...")
test_email = "testuser12345@example.com"
test_password = "SecurePass123!"

try:
    response = client.auth.sign_up({
        "email": test_email,
        "password": test_password,
        "options": {
            "data": {
                "username": "testuser12345"
            }
        }
    })

    print(f"\n✅ REGISTRATION SUCCESSFUL!")
    print(f"   User: {response.user}")
    print(f"   Session: {response.session}")

except Exception as e:
    error_msg = str(e)
    print(f"\n❌ REGISTRATION FAILED")
    print(f"   Error: {error_msg}")

    # Provide helpful guidance
    if "Invalid API key" in error_msg or "invalid" in error_msg.lower():
        print(f"\n📋 The API key is invalid. To fix:")
        print(f"   1. Go to: https://supabase.com/dashboard/project/kqzmwzosluljckadthup")
        print(f"   2. Click Settings → API")
        print(f"   3. Copy the 'anon' 'public' key")
        print(f"   4. Paste it in .streamlit/secrets.toml")

    elif "Email rate limit exceeded" in error_msg:
        print(f"\n⏰ Rate limit hit - wait a bit and try again")

    elif "User already registered" in error_msg or "already exists" in error_msg:
        print(f"\n✓ This actually means the API key works!")
        print(f"   The user {test_email} already exists in Supabase")
        print(f"   Try with a different email")

    elif "Email not allowed" in error_msg:
        print(f"\n🔒 Email provider might need to be enabled")
        print(f"   Go to: Auth → Providers → Enable Email")

print("\n" + "="*60)
