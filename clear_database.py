#!/usr/bin/env python3
"""
Clear Database Script for Rhizome CBC Analysis
Clears all data from users, questionnaires, and cbc_results tables
"""

import sqlite3
from pathlib import Path

def clear_database():
    """Clear all data from the database tables"""
    db_path = Path(__file__).parent / "data" / "users.db"
    
    if not db_path.exists():
        print("Database file not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Clear all tables
        print("Clearing cbc_results table...")
        cursor.execute("DELETE FROM cbc_results")
        
        print("Clearing questionnaires table...")
        cursor.execute("DELETE FROM questionnaires")
        
        print("Clearing users table...")
        cursor.execute("DELETE FROM users")
        
        # Reset auto-increment counters
        print("Resetting auto-increment counters...")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='questionnaires'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='cbc_results'")
        
        conn.commit()
        
        # Verify tables are empty
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM questionnaires")
        questionnaires_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cbc_results")
        cbc_count = cursor.fetchone()[0]
        
        print(f"\n✅ Database cleared successfully!")
        print(f"Users: {users_count}")
        print(f"Questionnaires: {questionnaires_count}")
        print(f"CBC Results: {cbc_count}")
        
    except Exception as e:
        print(f"Error clearing database: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🗑️  Clearing Rhizome Database...")
    print("=" * 40)
    
    confirm = input("Are you sure you want to clear ALL data? (yes/no): ")
    if confirm.lower() == 'yes':
        clear_database()
    else:
        print("Operation cancelled.")