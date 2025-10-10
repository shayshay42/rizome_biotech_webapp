#!/usr/bin/env python3
"""
Local testing script for authentication system
Tests bcrypt password hashing, user registration, and login
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.auth import hash_password, verify_password, register_user, authenticate_user
from utils.database import DatabaseManager

def test_password_hashing():
    """Test that password hashing works correctly"""
    print("\n" + "="*60)
    print("TEST 1: Password Hashing")
    print("="*60)

    password = "TestPassword123!"

    # Test hashing
    hashed = hash_password(password)
    print(f"✓ Password hashed successfully")
    print(f"  Original: {password}")
    print(f"  Hashed: {hashed[:50]}... (length: {len(hashed)})")
    print(f"  Type: {type(hashed)}")

    # Verify it's a string (for database storage)
    assert isinstance(hashed, str), "Hash should be string for database"
    print(f"✓ Hash is string type (ready for database)")

    # Test verification
    assert verify_password(password, hashed), "Password verification failed"
    print(f"✓ Password verification successful")

    # Test wrong password
    assert not verify_password("WrongPassword", hashed), "Wrong password should not verify"
    print(f"✓ Wrong password correctly rejected")

    print("\n✅ Password hashing tests PASSED")
    return True

def test_database_connection():
    """Test database connection and table creation"""
    print("\n" + "="*60)
    print("TEST 2: Database Connection")
    print("="*60)

    db = DatabaseManager()
    print(f"✓ Database type: {db.db_type}")

    conn = db.get_connection()
    print(f"✓ Connection established")

    # Check tables exist
    cursor = conn.cursor()

    if db.db_type == 'sqlite':
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
    else:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = [row[0] if isinstance(row, tuple) else row['table_name'] for row in cursor.fetchall()]

    print(f"✓ Tables found: {tables}")

    required_tables = ['users', 'questionnaires', 'cbc_results']
    for table in required_tables:
        assert table in tables, f"Missing table: {table}"

    print(f"✓ All required tables present")

    conn.close()

    print("\n✅ Database connection tests PASSED")
    return True

def test_user_registration():
    """Test user registration flow"""
    print("\n" + "="*60)
    print("TEST 3: User Registration")
    print("="*60)

    # Clean up test user if exists
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()

    placeholder = "%s" if db.db_type == 'postgresql' else "?"

    try:
        cursor.execute(f"DELETE FROM users WHERE username = {placeholder} OR email = {placeholder}",
                      ('testuser', 'test@example.com'))
        conn.commit()
        print("✓ Cleaned up existing test user")
    except:
        pass

    conn.close()

    # Test registration
    username = "testuser"
    email = "test@example.com"
    password = "SecurePassword123!"

    success, message = register_user(username, email, password)

    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print(f"  Result: {message}")

    assert success, f"Registration failed: {message}"
    print(f"✓ Registration successful")

    # Verify user exists in database
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"SELECT username, email, password_hash FROM users WHERE username = {placeholder}",
        (username,)
    )
    result = cursor.fetchone()

    if isinstance(result, dict):
        db_username = result['username']
        db_email = result['email']
        db_hash = result['password_hash']
    else:
        db_username = result[0]
        db_email = result[1]
        db_hash = result[2]

    print(f"✓ User found in database")
    print(f"  Username: {db_username}")
    print(f"  Email: {db_email}")
    print(f"  Hash type: {type(db_hash)}")
    print(f"  Hash length: {len(db_hash) if isinstance(db_hash, str) else 'N/A'}")

    assert db_username == username, "Username mismatch"
    assert db_email == email, "Email mismatch"
    assert isinstance(db_hash, str), "Password hash should be string"

    conn.close()

    print("\n✅ User registration tests PASSED")
    return username, password

def test_user_authentication(username, password):
    """Test user authentication flow"""
    print("\n" + "="*60)
    print("TEST 4: User Authentication")
    print("="*60)

    # Test correct password
    print(f"\nAttempting login with correct password...")
    success, user_id, email = authenticate_user(username, password)

    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print(f"  Success: {success}")
    print(f"  User ID: {user_id}")
    print(f"  Email: {email}")

    assert success, "Authentication with correct password failed"
    assert user_id is not None, "User ID should not be None"
    assert email is not None, "Email should not be None"
    print(f"✓ Login successful with correct password")

    # Test wrong password
    print(f"\nAttempting login with wrong password...")
    success, user_id, email = authenticate_user(username, "WrongPassword123!")

    print(f"  Success: {success}")
    print(f"  User ID: {user_id}")
    print(f"  Email: {email}")

    assert not success, "Authentication should fail with wrong password"
    assert user_id is None, "User ID should be None on failed auth"
    assert email is None, "Email should be None on failed auth"
    print(f"✓ Login correctly rejected with wrong password")

    # Test non-existent user
    print(f"\nAttempting login with non-existent user...")
    success, user_id, email = authenticate_user("nonexistent", "password")

    print(f"  Success: {success}")

    assert not success, "Authentication should fail for non-existent user"
    print(f"✓ Login correctly rejected for non-existent user")

    print("\n✅ User authentication tests PASSED")
    return True

def run_all_tests():
    """Run all authentication tests"""
    print("\n" + "="*60)
    print("AUTHENTICATION SYSTEM TEST SUITE")
    print("="*60)
    print("\nTesting local SQLite database...")
    print("This validates the authentication flow before deploying to Supabase")

    try:
        # Test 1: Password hashing
        test_password_hashing()

        # Test 2: Database connection
        test_database_connection()

        # Test 3: User registration
        username, password = test_user_registration()

        # Test 4: User authentication
        test_user_authentication(username, password)

        # All tests passed
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\n✅ Authentication system is working correctly")
        print("✅ Safe to deploy to production")
        print("\nNext steps:")
        print("1. Run reset_supabase_database.sql in Supabase SQL Editor")
        print("2. Deploy to Streamlit Cloud")
        print("3. Test registration and login on production")

        return True

    except Exception as e:
        print("\n" + "="*60)
        print("❌ TEST FAILED!")
        print("="*60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
