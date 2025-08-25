#!/usr/bin/env python3
"""
Direct Supabase Connection Test
Tests PostgreSQL connection directly without Streamlit context
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import toml
from pathlib import Path

def load_secrets():
    """Load secrets from .streamlit/secrets.toml"""
    secrets_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'
    
    if not secrets_path.exists():
        print(f"❌ Secrets file not found: {secrets_path}")
        return None
    
    try:
        secrets = toml.load(secrets_path)
        return secrets.get('supabase', {})
    except Exception as e:
        print(f"❌ Error loading secrets: {e}")
        return None

def test_direct_connection():
    """Test direct PostgreSQL connection to Supabase"""
    
    print("🐘 DIRECT SUPABASE CONNECTION TEST")
    print("="*50)
    
    # Load credentials
    print("📁 Loading secrets from .streamlit/secrets.toml...")
    config = load_secrets()
    
    if not config:
        return False
    
    print(f"✅ Loaded config for host: {config.get('host', 'unknown')}")
    
    # Build connection string
    conn_string = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    print(f"🔗 Connecting to: {config['host']}...")
    
    try:
        # Test connection
        conn = psycopg2.connect(conn_string, cursor_factory=RealDictCursor)
        print("✅ Connection successful!")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"📈 PostgreSQL Version: {version[0][:80]}...")
        
        # Test table creation
        print("\n🏗️  Testing table creation...")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Users table created")
        
        # Create questionnaires table
        cursor.execute("""
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
        """)
        print("✅ Questionnaires table created")
        
        # Create CBC results table
        cursor.execute("""
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
        print("✅ CBC results table created")
        
        # Commit changes
        conn.commit()
        
        # Test data queries
        print("\n🧪 Testing data operations...")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"📊 Current users: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM cbc_results")  
        cbc_count = cursor.fetchone()[0]
        print(f"📊 Current CBC results: {cbc_count}")
        
        # List all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"\n📋 Database tables:")
        for table in tables:
            print(f"   • {table[0]}")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 Supabase setup completed successfully!")
        print(f"📝 Database ready at: {config['host']}")
        print(f"🔗 View your data at: https://supabase.com/dashboard")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL Error: {e}")
        print(f"\n🔧 Troubleshooting:")
        print(f"   1. Check password in .streamlit/secrets.toml")
        print(f"   2. Verify Supabase project is active")
        print(f"   3. Check network connectivity")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_direct_connection()
    
    if success:
        print(f"\n🚀 Next steps:")
        print(f"   1. Add same secrets to Streamlit Community Cloud")
        print(f"   2. Deploy your app - it will use PostgreSQL automatically")
        print(f"   3. Test CBC PDF uploads in production")
    else:
        print(f"\n❌ Please check your credentials and try again.")