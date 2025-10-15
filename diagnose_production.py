"""
Quick diagnostic script to check production database status
Run this to see what needs to be fixed
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database import get_db_manager

def diagnose_production():
    """Check what's wrong with the production database"""
    
    print("\n" + "="*70)
    print("PRODUCTION DIAGNOSTIC")
    print("="*70)
    
    db = get_db_manager()
    
    # Check 1: Do ML columns exist?
    print("\n1️⃣ CHECKING DATABASE SCHEMA...")
    
    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'cbc_results'
        AND column_name IN ('model_used', 'cancer_probability_pct')
    """
    
    try:
        results = db.execute_query(query, fetch='all')
        columns_found = [r[0] if isinstance(r, tuple) else r['column_name'] for r in results]
        
        if 'model_used' in columns_found:
            print("   ✅ model_used column exists")
        else:
            print("   ❌ model_used column MISSING - need to run migration")
        
        if 'cancer_probability_pct' in columns_found:
            print("   ✅ cancer_probability_pct column exists")
        else:
            print("   ❌ cancer_probability_pct column MISSING - need to run migration")
        
        if len(columns_found) < 2:
            print("\n   ⚠️  ACTION REQUIRED: Run 'python run_production_migration.py'")
    except Exception as e:
        print(f"   ❌ Error checking schema: {e}")
    
    # Check 2: Are recent records using the model?
    print("\n2️⃣ CHECKING RECENT CBC RECORDS...")
    
    query2 = """
        SELECT id, risk_score, cancer_probability_pct, model_used, created_at
        FROM cbc_results
        ORDER BY created_at DESC
        LIMIT 5
    """
    
    try:
        records = db.execute_query(query2, fetch='all')
        
        if not records:
            print("   ℹ️  No records found")
        else:
            records_without_model = 0
            records_with_null_pct = 0
            
            for record in records:
                if not isinstance(record, dict):
                    columns = ['id', 'risk_score', 'cancer_probability_pct', 'model_used', 'created_at']
                    record = dict(zip(columns, record))
                
                print(f"\n   Record {record['id']}:")
                print(f"      Created: {record['created_at']}")
                print(f"      risk_score: {record['risk_score']}")
                print(f"      cancer_probability_pct: {record['cancer_probability_pct']}")
                print(f"      model_used: {record['model_used']}")
                
                if record['model_used'] is None:
                    records_without_model += 1
                    print(f"      ❌ model_used is NULL")
                else:
                    print(f"      ✅ model_used populated")
                
                if record['cancer_probability_pct'] is None:
                    records_with_null_pct += 1
                    print(f"      ❌ cancer_probability_pct is NULL")
                else:
                    print(f"      ✅ cancer_probability_pct populated")
            
            print(f"\n   Summary:")
            print(f"      {records_without_model} records without model")
            print(f"      {records_with_null_pct} records with NULL pct")
            
            if records_without_model > 0 or records_with_null_pct > 0:
                print(f"\n   ⚠️  ACTION REQUIRED: Run 'python run_production_migration.py'")
    except Exception as e:
        print(f"   ❌ Error checking records: {e}")
    
    # Check 3: Can we load the model?
    print("\n3️⃣ CHECKING MODEL FILE...")
    
    try:
        from utils.cancer_classifier import get_classifier
        classifier = get_classifier()
        if classifier:
            print("   ✅ CatBoost model loads successfully")
        else:
            print("   ❌ CatBoost model failed to load")
    except Exception as e:
        print(f"   ❌ Error loading model: {e}")
    
    # Check 4: Test prediction
    print("\n4️⃣ TESTING MODEL PREDICTION...")
    
    try:
        from utils.cancer_classifier import predict_cancer_risk
        test_cbc = {
            'WBC': 7.2,
            'NLR': 2.5,
            'HGB': 145.0,
            'MCV': 88.0,
            'PLT': 250.0,
            'RDW': 13.2,
            'MONO': 0.6
        }
        
        result = predict_cancer_risk(test_cbc)
        
        if result.get('model_used'):
            print(f"   ✅ Prediction works")
            print(f"      Model: {result.get('model_used')}")
            print(f"      Risk: {result.get('cancer_probability_pct')}%")
        else:
            print(f"   ⚠️  Prediction fallback used")
            print(f"      Risk: {result.get('cancer_probability_pct')}%")
    except Exception as e:
        print(f"   ❌ Error testing prediction: {e}")
    
    print("\n" + "="*70)
    print("DIAGNOSTIC COMPLETE")
    print("="*70)

if __name__ == '__main__':
    diagnose_production()
