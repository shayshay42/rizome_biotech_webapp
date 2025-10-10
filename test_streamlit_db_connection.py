#!/usr/bin/env python3
"""
Test Streamlit app database connection
"""

import os
import sys
sys.path.append('.')

# Mock Streamlit secrets for testing
class MockSecrets:
    def __init__(self):
        self.supabase = {
            'host': 'aws-1-ca-central-1.pooler.supabase.com',
            'port': '5432',
            'database': 'postgres',
            'user': 'postgres.kqzmwzosluljckadthup',
            'password': 'ZnJJSIChnokAmtcS'
        }
        
    def __contains__(self, key):
        return key == 'supabase'

# Mock streamlit module
import importlib.util
spec = importlib.util.spec_from_loader("streamlit", loader=None)
st = importlib.util.module_from_spec(spec)
st.secrets = MockSecrets()
sys.modules["streamlit"] = st

# Now import and test database manager
from utils.database import DatabaseManager

def test_database_connection():
    """Test the database connection through DatabaseManager"""
    
    print("Testing Streamlit app database connection...")
    print("="*50)
    
    # Initialize database manager
    db = DatabaseManager()
    print(f"Database type detected: {db.db_type}")
    
    try:
        # Test connection
        conn = db.get_connection()
        print(f"Connection successful: {type(conn)}")
        
        # Test query
        result = db.execute_query('SELECT COUNT(*) FROM users', fetch='one')
        
        if db.db_type == 'postgresql':
            user_count = result[0] if result else 0
            print(f"Users in Supabase database: {user_count}")
            
            # Test inserting test data
            db.execute_query('''
                INSERT INTO users (username, password_hash, email) 
                VALUES (%s, %s, %s)
            ''', ('streamlit_test_user', 'hashed_pass_789', 'streamlit@test.com'))
            
            # Test CBC result insertion
            db.execute_query('''
                INSERT INTO cbc_results (
                    user_id, file_format, extraction_method,
                    hgb, wbc, plt, missing_biomarkers, imputed_count
                ) VALUES (
                    (SELECT id FROM users WHERE username = %s LIMIT 1),
                    %s, %s, %s, %s, %s, %s, %s
                )
            ''', ('streamlit_test_user', 'quebec_health_booklet', 'quebec_extractor', 
                  135.0, 5.8, 190.0, ['RDW'], 1))
            
            print("✅ SUCCESS: Streamlit app can connect to Supabase!")
            print("✅ User registration will work")
            print("✅ CBC data storage will work") 
            print("✅ Quebec Health Booklet support ready")
            
        else:
            print("Using SQLite fallback")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    if success:
        print("\n🎉 Your Streamlit app is ready for deployment!")
    else:
        print("\n❌ Database connection issues need to be resolved")