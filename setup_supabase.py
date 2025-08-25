#!/usr/bin/env python3
"""
Supabase Database Setup Script
Creates all necessary tables in your Supabase PostgreSQL database
"""

import sys
from pathlib import Path
import os

# Add utils to path
sys.path.append(str(Path(__file__).parent))

def setup_supabase_database():
    """Set up Supabase database with proper tables"""
    
    print("🐘 SUPABASE DATABASE SETUP")
    print("="*50)
    
    # Set environment variable to force PostgreSQL usage
    os.environ['SUPABASE_URL'] = 'force_postgresql'
    
    try:
        from utils.database import get_db_manager, init_database
        
        print("📊 Connecting to Supabase PostgreSQL...")
        db_type = init_database()
        
        if db_type != 'postgresql':
            print("❌ Failed to connect to PostgreSQL. Check your secrets.toml file.")
            print("   Make sure you've updated the password in .streamlit/secrets.toml")
            return False
        
        print("✅ Connected to Supabase PostgreSQL!")
        
        # Test connection with a simple query
        db = get_db_manager()
        result = db.execute_query("SELECT version()", fetch='one')
        print(f"📈 PostgreSQL Version: {result[0][:50]}...")
        
        # Test table creation
        print("\n🏗️  Creating database tables...")
        
        # Test each table individually
        tables = [
            ("users", """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    email VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """),
            ("questionnaires", """
                CREATE TABLE IF NOT EXISTS questionnaires (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    q1_family_history BOOLEAN,
                    q2_smoking_status VARCHAR(20),
                    q3_alcohol_consumption VARCHAR(20),
                    q4_previous_cancer BOOLEAN,
                    q5_medications TEXT,
                    q6_symptoms TEXT,
                    q7_recent_infections BOOLEAN,
                    q8_chronic_conditions TEXT,
                    q9_exercise_frequency VARCHAR(20),
                    q10_stress_level VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """),
            ("cbc_results", """
                CREATE TABLE IF NOT EXISTS cbc_results (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    questionnaire_id INTEGER REFERENCES questionnaires(id),
                    test_date DATE,
                    file_format VARCHAR(50),
                    extraction_method VARCHAR(50),
                    
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
                    prediction_label VARCHAR(50),
                    risk_level VARCHAR(20),
                    confidence_score REAL,
                    
                    -- Metadata
                    missing_biomarkers TEXT[],
                    imputed_count INTEGER DEFAULT 0,
                    imputation_warning TEXT,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        ]
        
        for table_name, query in tables:
            try:
                db.execute_query(query)
                print(f"✅ Table '{table_name}' created successfully")
            except Exception as e:
                print(f"❌ Error creating table '{table_name}': {e}")
                return False
        
        # Test basic operations
        print("\n🧪 Testing basic database operations...")
        
        # Test inserting and querying
        try:
            # Count existing users
            result = db.execute_query("SELECT COUNT(*) FROM users", fetch='one')
            user_count = result[0]
            print(f"📊 Current users in database: {user_count}")
            
            # Count existing CBC results
            result = db.execute_query("SELECT COUNT(*) FROM cbc_results", fetch='one')
            cbc_count = result[0]
            print(f"📊 Current CBC results in database: {cbc_count}")
            
        except Exception as e:
            print(f"❌ Error testing database operations: {e}")
            return False
        
        print(f"\n🎉 Supabase database setup completed successfully!")
        print(f"📝 Your database is ready at: db.kqzmwzosluljckadthup.supabase.co")
        print(f"🔗 You can view your data in the Supabase dashboard")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print(f"\n🔧 Troubleshooting:")
        print(f"   1. Check that your password is correct in .streamlit/secrets.toml")
        print(f"   2. Verify your Supabase project is active")
        print(f"   3. Make sure psycopg2-binary is installed: pip install psycopg2-binary")
        return False

if __name__ == "__main__":
    success = setup_supabase_database()
    
    if success:
        print(f"\n🚀 Next steps:")
        print(f"   1. Your database is ready for production")
        print(f"   2. Add the same secrets to Streamlit Community Cloud")
        print(f"   3. Deploy your app - it will automatically use PostgreSQL")
    else:
        print(f"\n❌ Setup failed. Please check the troubleshooting steps above.")