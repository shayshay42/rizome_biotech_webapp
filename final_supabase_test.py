#!/usr/bin/env python3
"""
Final Supabase Connection Test
Test with the official connection string format
"""

import psycopg2
import time

def test_supabase_final():
    """Test with official Supabase connection string"""
    
    print("🚀 FINAL SUPABASE CONNECTION TEST")
    print("="*50)
    
    # Your exact credentials from the dashboard
    HOST = "db.kqzmwzosluljckadthup.supabase.co"
    PORT = "5432"
    DATABASE = "postgres"
    USER = "postgres"
    PASSWORD = "ZnJJSIChnpkAmtcS"  # Your password
    
    # Full connection string (as per Supabase format)
    conn_string = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    
    print(f"📝 Connection details:")
    print(f"   Host: {HOST}")
    print(f"   Port: {PORT}")
    print(f"   Database: {DATABASE}")
    print(f"   User: {USER}")
    print(f"   Connection String: postgresql://postgres:***@{HOST}:5432/postgres")
    
    print(f"\n🔗 Testing connection...")
    
    try:
        # Try with longer timeout
        connection = psycopg2.connect(
            host=HOST,
            port=PORT,
            database=DATABASE,
            user=USER,
            password=PASSWORD,
            connect_timeout=30,  # 30 second timeout
            sslmode='require'    # Force SSL
        )
        
        print("✅ Connection successful!")
        
        # Test basic operations
        cursor = connection.cursor()
        
        # Get current time
        cursor.execute("SELECT NOW();")
        current_time = cursor.fetchone()[0]
        print(f"📅 Database time: {current_time}")
        
        # Get PostgreSQL version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"📊 PostgreSQL: {version[:80]}...")
        
        # Test creating our production tables
        print(f"\n🏗️  Setting up production tables...")
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Users table ready")
        
        # Questionnaires table  
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
        print("✅ Questionnaires table ready")
        
        # CBC results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cbc_results (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                questionnaire_id INTEGER REFERENCES questionnaires(id),
                test_date DATE,
                file_format VARCHAR(50),
                extraction_method VARCHAR(50),
                
                -- Individual CBC biomarkers
                wbc REAL, rbc REAL, hgb REAL, hct REAL,
                mcv REAL, mch REAL, mchc REAL, rdw REAL,
                plt REAL, mpv REAL,
                
                -- Differential counts
                neut_abs REAL, lymph_abs REAL, mono_abs REAL,
                eos_abs REAL, baso_abs REAL,
                neut_pct REAL, lymph_pct REAL, mono_pct REAL,
                eos_pct REAL, baso_pct REAL,
                
                -- Calculated ratios
                nlr REAL, nrbc_abs REAL, nrbc_pct REAL,
                
                -- ML prediction results
                cancer_probability REAL,
                prediction_label VARCHAR(50),
                risk_level VARCHAR(20),
                confidence_score REAL,
                
                -- Metadata for Quebec Health Booklet support
                missing_biomarkers TEXT[],
                imputed_count INTEGER DEFAULT 0,
                imputation_warning TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ CBC results table ready")
        
        connection.commit()
        
        # Test data operations
        print(f"\n🧪 Testing data operations...")
        
        # Check existing data
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"📊 Users in database: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM cbc_results")
        cbc_count = cursor.fetchone()[0]
        print(f"📊 CBC results in database: {cbc_count}")
        
        # List all tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Database tables: {', '.join(tables)}")
        
        cursor.close()
        connection.close()
        
        print(f"\n🎉 SUPABASE DATABASE SETUP COMPLETE!")
        print(f"✅ Your production database is ready")
        print(f"🔗 Database URL: {HOST}")
        
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e).lower()
        print(f"❌ Connection failed: {e}")
        
        if "timeout expired" in error_msg:
            print(f"\n🔧 TIMEOUT ISSUE - Possible causes:")
            print(f"   • Supabase project is PAUSED (most likely)")
            print(f"   • Network/firewall blocking connection")
            print(f"   • Supabase having connectivity issues")
            print(f"\n💡 To check if project is paused:")
            print(f"   1. Go to: https://supabase.com/dashboard/project/kqzmwzosluljckadthup")
            print(f"   2. Look for 'Paused' status or 'Resume' button")
            print(f"   3. If paused, click 'Resume' to activate")
            
        elif "authentication failed" in error_msg:
            print(f"\n🔧 AUTHENTICATION ISSUE:")
            print(f"   • Check password is correct")
            print(f"   • Verify user 'postgres' exists")
            
        elif "could not translate host name" in error_msg:
            print(f"\n🔧 DNS ISSUE:")
            print(f"   • Hostname might be incorrect")
            print(f"   • Check connection string in dashboard")
            
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_next_steps():
    """Show what to do next"""
    
    print(f"\n🚀 NEXT STEPS FOR DEPLOYMENT:")
    print(f"="*50)
    print(f"")
    print(f"1. 📊 If Supabase connection works:")
    print(f"   • Your production database is ready!")
    print(f"   • Add these secrets to Streamlit Cloud")
    print(f"   • Deploy your app")
    print(f"")
    print(f"2. ⏸️  If project is paused:")
    print(f"   • Go to Supabase dashboard")
    print(f"   • Click 'Resume' to activate project")
    print(f"   • Wait 1-2 minutes for activation")
    print(f"   • Run this test again")
    print(f"")
    print(f"3. 🚀 For Streamlit Cloud deployment:")
    print(f"   • App Settings → Secrets")
    print(f"   • Add the same [supabase] config")
    print(f"   • App will automatically use PostgreSQL")
    print(f"")
    print(f"✨ Your app has these features ready:")
    print(f"   • Quebec Health Booklet PDF extraction")
    print(f"   • Missing value imputation (NaN handling)")
    print(f"   • Universal CarnetSante format support")
    print(f"   • ML cancer risk prediction")
    print(f"   • Persistent database storage")

if __name__ == "__main__":
    success = test_supabase_final()
    show_next_steps()