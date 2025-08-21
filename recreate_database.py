#!/usr/bin/env python3
"""
Recreate Database for Rhizome CBC Analysis
Drops and recreates tables with the correct enhanced schema
"""

import sqlite3
from pathlib import Path

def recreate_database():
    """Drop and recreate all tables with the correct schema"""
    db_path = Path(__file__).parent / "data" / "users.db"
    
    # Ensure data directory exists
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        print("Dropping existing tables...")
        
        # Drop tables in reverse order (due to foreign keys)
        cursor.execute("DROP TABLE IF EXISTS cbc_results")
        cursor.execute("DROP TABLE IF EXISTS questionnaires") 
        cursor.execute("DROP TABLE IF EXISTS users")
        
        print("Creating users table...")
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        print("Creating questionnaires table...")
        cursor.execute('''
            CREATE TABLE questionnaires (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                age INTEGER,
                weight REAL,
                height REAL,
                sex TEXT,
                activity_level TEXT,
                smoking TEXT,
                chronic_conditions TEXT,
                medications TEXT,
                family_history TEXT,
                symptoms TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        print("Creating cbc_results table...")
        cursor.execute('''
            CREATE TABLE cbc_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                questionnaire_id INTEGER,
                filename TEXT,
                file_format TEXT,  -- PDF format (carnetsante, etc.)
                extraction_success BOOLEAN DEFAULT TRUE,
                
                -- Raw extraction data
                raw_extraction_data TEXT,  -- Full JSON of extraction result
                patient_info TEXT,  -- JSON of patient demographics from PDF
                
                -- Standardized CBC values (main biomarkers)
                wbc REAL,  -- White Blood Cells (10^9/L)
                rbc REAL,  -- Red Blood Cells (10^12/L)
                hgb REAL,  -- Hemoglobin (g/L)
                hct REAL,  -- Hematocrit (L)
                mcv REAL,  -- Mean Corpuscular Volume (fL)
                mch REAL,  -- Mean Corpuscular Hemoglobin (pg)
                mchc REAL, -- Mean Corpuscular Hemoglobin Concentration (g/L)
                rdw REAL,  -- Red Cell Distribution Width (%)
                plt REAL,  -- Platelets (10^9/L)
                mpv REAL,  -- Mean Platelet Volume (fL)
                
                -- Differential counts
                neut_abs REAL,  -- Neutrophils Absolute (10^9/L)
                neut_pct REAL,  -- Neutrophils Percentage (%)
                lymph_abs REAL, -- Lymphocytes Absolute (10^9/L)
                lymph_pct REAL, -- Lymphocytes Percentage (%)
                mono_abs REAL,  -- Monocytes Absolute (10^9/L)
                mono_pct REAL,  -- Monocytes Percentage (%)
                eos_abs REAL,   -- Eosinophils Absolute (10^9/L)
                eos_pct REAL,   -- Eosinophils Percentage (%)
                baso_abs REAL,  -- Basophils Absolute (10^9/L)
                baso_pct REAL,  -- Basophils Percentage (%)
                
                -- Calculated ratios
                nlr REAL,  -- Neutrophil to Lymphocyte Ratio
                
                -- Additional tests (when available)
                additional_tests TEXT,  -- JSON of other lab values
                
                -- ML processing results
                cbc_vector TEXT,  -- JSON string of 175 engineered features
                risk_score REAL,
                risk_interpretation TEXT,  -- JSON of risk analysis
                
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (questionnaire_id) REFERENCES questionnaires (id)
            )
        ''')
        
        conn.commit()
        
        # Verify tables were created correctly
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n✅ Database recreated successfully!")
        print(f"Tables created: {[table[0] for table in tables]}")
        
        # Show CBC results table schema
        cursor.execute("PRAGMA table_info(cbc_results)")
        columns = cursor.fetchall()
        print(f"\nCBC Results table has {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
    except Exception as e:
        print(f"Error recreating database: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Recreating Rhizome Database...")
    print("=" * 40)
    recreate_database()