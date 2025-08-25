#!/usr/bin/env python3
"""
Update Local Database Schema
Updates the local SQLite database to match the unified schema
"""

import sqlite3
import os
from pathlib import Path

def update_local_database():
    """Update local database to unified schema"""
    
    print("🔄 UPDATING LOCAL DATABASE SCHEMA")
    print("="*50)
    
    db_path = Path(__file__).parent / 'data' / 'users.db'
    
    # Backup existing database
    if db_path.exists():
        backup_path = db_path.with_suffix('.backup.db')
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"📁 Backup created: {backup_path}")
    
    # Create new database with unified schema
    print("🏗️  Creating updated database schema...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS cbc_results")
    cursor.execute("DROP TABLE IF EXISTS questionnaires") 
    cursor.execute("DROP TABLE IF EXISTS users")
    print("🗑️  Dropped old tables")
    
    # Create users table
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created users table")
    
    # Create questionnaires table
    cursor.execute("""
        CREATE TABLE questionnaires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            q1_family_history BOOLEAN,
            q2_smoking_status TEXT,
            q3_alcohol_consumption TEXT,
            q4_previous_cancer BOOLEAN,
            q5_medications TEXT,
            q6_symptoms TEXT,
            q7_recent_infections BOOLEAN,
            q8_chronic_conditions TEXT,
            q9_exercise_frequency TEXT,
            q10_stress_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    print("✅ Created questionnaires table")
    
    # Create cbc_results table with unified schema
    cursor.execute("""
        CREATE TABLE cbc_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            questionnaire_id INTEGER,
            test_date DATE,
            file_format TEXT,
            extraction_method TEXT,
            
            -- Individual CBC biomarkers
            wbc REAL,
            rbc REAL,
            hgb REAL,
            hct REAL,
            mcv REAL,
            mch REAL,
            mchc REAL,
            rdw REAL,
            plt REAL,
            mpv REAL,
            
            -- Differential counts (absolute)
            neut_abs REAL,
            lymph_abs REAL,
            mono_abs REAL,
            eos_abs REAL,
            baso_abs REAL,
            
            -- Differential counts (percentage)
            neut_pct REAL,
            lymph_pct REAL,
            mono_pct REAL,
            eos_pct REAL,
            baso_pct REAL,
            
            -- Calculated ratios
            nlr REAL,
            
            -- Additional fields
            nrbc_abs REAL,
            nrbc_pct REAL,
            
            -- ML prediction results
            cancer_probability REAL,
            prediction_label TEXT,
            risk_level TEXT,
            confidence_score REAL,
            
            -- Metadata
            missing_biomarkers TEXT,
            imputed_count INTEGER DEFAULT 0,
            imputation_warning TEXT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (questionnaire_id) REFERENCES questionnaires (id)
        )
    """)
    print("✅ Created cbc_results table with unified schema")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Database schema updated successfully!")
    print(f"📊 Ready for both local development and production deployment")

if __name__ == "__main__":
    update_local_database()