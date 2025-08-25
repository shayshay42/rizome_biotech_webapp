#!/usr/bin/env python3
"""
Database Migration Script
Migrates from local SQLite to PostgreSQL (Supabase) or initializes new database
"""

import sys
from pathlib import Path
import sqlite3

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.database import get_db_manager, init_database

def migrate_local_to_postgres():
    """Migrate existing SQLite data to PostgreSQL"""
    
    print("🔄 DATABASE MIGRATION UTILITY")
    print("="*50)
    
    # Initialize new database system
    print("📊 Initializing database system...")
    db_type = init_database()
    print(f"✅ Database type: {db_type}")
    
    if db_type == 'sqlite':
        print("ℹ️  Using local SQLite database (development mode)")
        print("   To use PostgreSQL, configure Supabase credentials in secrets.toml")
        return
    
    print("🐘 Using PostgreSQL database (production mode)")
    
    # Check if we have local SQLite data to migrate
    local_db_path = Path(__file__).parent / 'data' / 'users.db'
    
    if not local_db_path.exists():
        print("ℹ️  No local SQLite database found. Starting fresh.")
        return
    
    print(f"📁 Found local database: {local_db_path}")
    
    # Connect to local SQLite
    try:
        sqlite_conn = sqlite3.connect(local_db_path)
        cursor = sqlite_conn.cursor()
        
        # Check what data exists
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cbc_results")
        cbc_count = cursor.fetchone()[0]
        
        print(f"📈 Local data found:")
        print(f"   Users: {user_count}")
        print(f"   CBC Results: {cbc_count}")
        
        if user_count == 0 and cbc_count == 0:
            print("ℹ️  No data to migrate. Database is empty.")
            sqlite_conn.close()
            return
        
        # Ask for confirmation
        response = input(f"\n🤔 Do you want to migrate {user_count} users and {cbc_count} CBC results to PostgreSQL? (y/N): ")
        
        if response.lower() != 'y':
            print("❌ Migration cancelled.")
            sqlite_conn.close()
            return
        
        # TODO: Implement actual migration logic here
        print("⚠️  Migration logic not yet implemented.")
        print("   For now, you can manually recreate users in the web app.")
        
        sqlite_conn.close()
        
    except Exception as e:
        print(f"❌ Error accessing local database: {e}")

def test_database_connection():
    """Test database connection and basic operations"""
    
    print("\n🧪 TESTING DATABASE CONNECTION")
    print("="*40)
    
    try:
        db = get_db_manager()
        print(f"✅ Database type: {db.db_type}")
        
        # Test basic query
        if db.db_type == 'postgresql':
            result = db.execute_query("SELECT version()", fetch='one')
            print(f"✅ PostgreSQL version: {result[0] if result else 'Unknown'}")
        else:
            result = db.execute_query("SELECT sqlite_version()", fetch='one')
            print(f"✅ SQLite version: {result[0] if result else 'Unknown'}")
        
        # Test table creation
        print("🏗️  Testing table creation...")
        db.create_tables()
        print("✅ Tables created successfully")
        
        print("\n🎉 Database connection test successful!")
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")

if __name__ == "__main__":
    migrate_local_to_postgres()
    test_database_connection()