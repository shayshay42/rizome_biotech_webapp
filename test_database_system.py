#!/usr/bin/env python3
"""
Test Database System (Local + Production Ready)
Tests the unified database system that works both locally and in production
"""

import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

def test_local_database():
    """Test the local SQLite database system"""
    
    print("🔬 TESTING LOCAL DATABASE SYSTEM")
    print("="*50)
    
    try:
        from utils.database import get_db_manager, create_user, authenticate_user, init_database
        
        # Initialize database
        print("📊 Initializing database...")
        db_type = init_database()
        print(f"✅ Database type: {db_type}")
        
        # Test user creation
        print("\n👤 Testing user management...")
        test_user = "test_cbc_user"
        test_password = "secure_password123"
        test_email = "test@example.com"
        
        # Create user
        success = create_user(test_user, test_password, test_email)
        if success:
            print(f"✅ User '{test_user}' created successfully")
        else:
            print(f"ℹ️  User '{test_user}' already exists (that's okay)")
        
        # Test authentication
        user_data = authenticate_user(test_user, test_password)
        if user_data:
            print(f"✅ User authentication successful: {user_data['username']}")
        else:
            print(f"❌ User authentication failed")
            return False
        
        # Test CBC data storage (simulate Quebec Health Booklet results)
        print("\n🧪 Testing CBC data storage...")
        
        # Simulate CBC data from Quebec Health Booklet
        mock_cbc_data = {
            'WBC': {'value': 5.87, 'unit': '10*9/L'},
            'HGB': {'value': 137.0, 'unit': 'g/L'},
            'PLT': {'value': 191.0, 'unit': '10*9/L'},
            'MCV': {'value': 88.9, 'unit': 'fL'},
            'MONO': {'value': 0.38, 'unit': '10*9/L'},
            'NLR': {'value': 2.59, 'unit': 'ratio'},
            'NEUT_PCT': {'value': 63.31, 'unit': '%'},
            'LYMPH_PCT': {'value': 24.44, 'unit': '%'}
        }
        
        # Simulate ML prediction results with imputation
        mock_prediction_results = {
            'cancer_probability': 0.016,
            'prediction_label': 'Low Cancer Risk',
            'risk_level': 'Very Low',
            'confidence': 0.884,
            'missing_features': ['RDW'],
            'imputed_count': 1,
            'imputation_warning': 'Note: 1 biomarker(s) were missing and estimated using population averages: RDW. This may affect prediction accuracy.'
        }
        
        from utils.database import save_cbc_results
        
        success = save_cbc_results(
            user_id=user_data['id'],
            cbc_data=mock_cbc_data,
            prediction_results=mock_prediction_results,
            file_format="quebec_health_booklet"
        )
        
        if success:
            print("✅ CBC results saved successfully")
        else:
            print("❌ Failed to save CBC results")
            return False
        
        # Test data retrieval
        print("\n📊 Testing data retrieval...")
        from utils.database import get_user_cbc_history
        
        history = get_user_cbc_history(user_data['id'])
        if history:
            latest = history[0]
            print(f"✅ Retrieved {len(history)} CBC record(s)")
            print(f"   Latest test: {latest['file_format']}")
            print(f"   HGB: {latest['hgb']} g/L")
            print(f"   Cancer probability: {latest['cancer_probability']:.1%}")
            print(f"   Imputed biomarkers: {latest['imputed_count']}")
        else:
            print("❌ No CBC history found")
            return False
        
        print(f"\n🎉 Local database system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_production_setup():
    """Show how to set up for production"""
    
    print(f"\n🚀 PRODUCTION DEPLOYMENT SETUP")
    print("="*50)
    
    print(f"📝 To deploy with Supabase PostgreSQL:")
    print(f"")
    print(f"1. Go to Streamlit Community Cloud app settings")
    print(f"2. Add these secrets:")
    print(f"")
    print(f"   [supabase]")
    print(f"   host = \"your-correct-supabase-host.supabase.co\"")
    print(f"   port = \"5432\"")
    print(f"   database = \"postgres\"")
    print(f"   user = \"postgres\"")
    print(f"   password = \"your-password\"")
    print(f"")
    print(f"3. Push your code to GitHub")
    print(f"4. App will automatically use PostgreSQL in production")
    print(f"")
    print(f"✨ The app automatically detects the environment:")
    print(f"   • Local development → SQLite")
    print(f"   • Streamlit Cloud with secrets → PostgreSQL")
    print(f"   • Fallback → SQLite (safe mode)")

if __name__ == "__main__":
    success = test_local_database()
    
    if success:
        show_production_setup()
        print(f"\n✅ Your database system is ready for both local development and production!")
    else:
        print(f"\n❌ Please fix the database issues above.")