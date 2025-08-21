#!/usr/bin/env python3
"""
Fix Database Schema for Rhizome CBC Analysis
Adds missing columns to the cbc_results table
"""

import sqlite3
from pathlib import Path

def fix_database_schema():
    """Add missing columns to the database schema"""
    db_path = Path(__file__).parent / "data" / "users.db"
    
    if not db_path.exists():
        print("Database file not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check existing schema
        cursor.execute("PRAGMA table_info(cbc_results)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Add missing columns if they don't exist
        missing_columns = [
            ('file_format', 'TEXT'),
            ('raw_extraction_data', 'TEXT'),
            ('patient_info', 'TEXT'),
            ('additional_tests', 'TEXT'),
            ('cbc_vector', 'TEXT'),
            ('risk_interpretation', 'TEXT')
        ]
        
        for column_name, column_type in missing_columns:
            if column_name not in existing_columns:
                print(f"Adding missing column: {column_name}")
                cursor.execute(f"ALTER TABLE cbc_results ADD COLUMN {column_name} {column_type}")
            else:
                print(f"Column {column_name} already exists")
        
        conn.commit()
        
        # Verify the updated schema
        cursor.execute("PRAGMA table_info(cbc_results)")
        updated_columns = [row[1] for row in cursor.fetchall()]
        print(f"\n✅ Updated schema with {len(updated_columns)} columns:")
        for col in updated_columns:
            print(f"  - {col}")
        
    except Exception as e:
        print(f"Error fixing database schema: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔧 Fixing Rhizome Database Schema...")
    print("=" * 40)
    fix_database_schema()