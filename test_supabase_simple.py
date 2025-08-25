#!/usr/bin/env python3
"""
Simple Supabase Connection Test
Direct connection test using the provided credentials
"""

import psycopg2
import toml
from pathlib import Path

def test_supabase_connection():
    """Test Supabase connection using direct credentials"""
    
    print("🐘 SIMPLE SUPABASE CONNECTION TEST")
    print("="*50)
    
    # Load credentials from secrets.toml
    secrets_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'
    
    try:
        secrets = toml.load(secrets_path)
        config = secrets['supabase']
        
        print(f"📁 Loaded credentials:")
        print(f"   Host: {config['host']}")
        print(f"   Port: {config['port']}")
        print(f"   Database: {config['database']}")
        print(f"   User: {config['user']}")
        print(f"   Password: {'*' * len(config['password'])}")
        
    except Exception as e:
        print(f"❌ Error loading secrets: {e}")
        return False
    
    # Test connection
    print(f"\n🔗 Attempting connection...")
    
    try:
        connection = psycopg2.connect(
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port'],
            dbname=config['database']
        )
        print("✅ Connection successful!")
        
        # Create a cursor to execute SQL queries
        cursor = connection.cursor()
        
        # Test basic query
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
        print(f"📅 Current Time: {result[0]}")
        
        # Test PostgreSQL version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"📊 PostgreSQL Version: {version[0][:80]}...")
        
        # Test table creation
        print(f"\n🏗️  Testing table operations...")
        
        # Create a test table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connection_test (
                id SERIAL PRIMARY KEY,
                test_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Test table created")
        
        # Insert test data
        cursor.execute("""
            INSERT INTO connection_test (test_message) 
            VALUES ('Supabase connection successful!')
        """)
        print("✅ Test data inserted")
        
        # Query test data
        cursor.execute("SELECT COUNT(*) FROM connection_test")
        count = cursor.fetchone()[0]
        print(f"📊 Test records in database: {count}")
        
        # Clean up test table
        cursor.execute("DROP TABLE connection_test")
        print("🗑️  Test table cleaned up")
        
        # Commit changes
        connection.commit()
        
        # Close the cursor and connection
        cursor.close()
        connection.close()
        print("🔒 Connection closed.")
        
        print(f"\n🎉 Supabase connection test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        
        # Detailed error analysis
        error_str = str(e).lower()
        print(f"\n🔧 Troubleshooting:")
        
        if "could not translate host name" in error_str:
            print(f"   • DNS/Hostname issue - check if host is correct")
            print(f"   • Try: ping {config['host']}")
        elif "authentication failed" in error_str:
            print(f"   • Password/username incorrect")
            print(f"   • Check Supabase dashboard for correct credentials")
        elif "connection refused" in error_str:
            print(f"   • Port/firewall issue")
            print(f"   • Verify port 5432 is accessible")
        elif "timeout" in error_str:
            print(f"   • Network connectivity issue")
            print(f"   • Check internet connection")
        else:
            print(f"   • Unexpected error: {e}")
        
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    
    if success:
        print(f"\n🚀 Next steps:")
        print(f"   1. Your Supabase database is ready!")
        print(f"   2. Now let's set up the production tables")
        print(f"   3. Deploy to Streamlit Cloud with these same secrets")
    else:
        print(f"\n❌ Please resolve connection issues above.")