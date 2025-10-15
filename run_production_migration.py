"""
PRODUCTION DEPLOYMENT SCRIPT
Run this after deploying the code to update the database schema
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database import get_db_manager

def run_production_migration():
    """
    Apply all necessary migrations for the deployed version
    """
    
    print("\n" + "="*70)
    print("PRODUCTION DEPLOYMENT MIGRATION")
    print("="*70)
    
    db = get_db_manager()
    
    # Step 1: Add ML prediction columns
    print("\n📝 Step 1: Adding ML prediction columns to cbc_results table...")
    
    migration_sql = """
    -- Add model_used column to track which model made the prediction
    ALTER TABLE cbc_results 
    ADD COLUMN IF NOT EXISTS model_used VARCHAR(255);

    -- Add cancer_probability_pct for storing percentage (0-100)
    ALTER TABLE cbc_results 
    ADD COLUMN IF NOT EXISTS cancer_probability_pct REAL;

    -- Add other useful ML prediction columns
    ALTER TABLE cbc_results 
    ADD COLUMN IF NOT EXISTS cancer_probability DOUBLE PRECISION;

    ALTER TABLE cbc_results 
    ADD COLUMN IF NOT EXISTS healthy_probability DOUBLE PRECISION;

    ALTER TABLE cbc_results 
    ADD COLUMN IF NOT EXISTS confidence_score DOUBLE PRECISION;

    ALTER TABLE cbc_results 
    ADD COLUMN IF NOT EXISTS confidence_pct REAL;

    ALTER TABLE cbc_results 
    ADD COLUMN IF NOT EXISTS risk_level VARCHAR(50);

    ALTER TABLE cbc_results 
    ADD COLUMN IF NOT EXISTS risk_color VARCHAR(50);

    ALTER TABLE cbc_results 
    ADD COLUMN IF NOT EXISTS prediction INTEGER;

    ALTER TABLE cbc_results 
    ADD COLUMN IF NOT EXISTS prediction_label VARCHAR(100);

    ALTER TABLE cbc_results 
    ADD COLUMN IF NOT EXISTS model_loaded BOOLEAN;

    ALTER TABLE cbc_results 
    ADD COLUMN IF NOT EXISTS model_load_error TEXT;
    """
    
    try:
        db.execute_query(migration_sql, fetch=None)
        print("   ✅ Columns added successfully")
    except Exception as e:
        print(f"   ❌ Error adding columns: {e}")
        print("   Note: This is OK if columns already exist")
    
    # Step 2: Re-process existing records
    print("\n📝 Step 2: Re-processing recent CBC records with CatBoost model...")
    
    query = """
        SELECT id, wbc, nlr, hgb, mcv, plt, rdw, mono_abs
        FROM cbc_results
        WHERE model_used IS NULL
        ORDER BY created_at DESC
        LIMIT 10
    """
    
    records = db.execute_query(query, fetch='all')
    
    if not records:
        print("   ✅ No records need updating")
    else:
        from utils.cancer_classifier import predict_cancer_risk
        from utils.database import update_cbc_predictions
        
        updated_count = 0
        for record in records:
            if not isinstance(record, dict):
                columns = ['id', 'wbc', 'nlr', 'hgb', 'mcv', 'plt', 'rdw', 'mono_abs']
                record = dict(zip(columns, record))
            
            record_id = record['id']
            
            # Build CBC data
            cbc_data = {
                'WBC': record.get('wbc'),
                'NLR': record.get('nlr'),
                'HGB': record.get('hgb'),
                'MCV': record.get('mcv'),
                'PLT': record.get('plt'),
                'RDW': record.get('rdw'),
                'MONO': record.get('mono_abs')
            }
            
            # Remove None values - let model impute
            cbc_data = {k: v for k, v in cbc_data.items() if v is not None}
            
            if len(cbc_data) >= 3:  # Need at least 3 values
                try:
                    # Run prediction
                    prediction = predict_cancer_risk(cbc_data)
                    
                    # Update database
                    success = update_cbc_predictions(record_id, prediction)
                    
                    if success:
                        updated_count += 1
                        print(f"   ✅ Updated record {record_id}: {prediction.get('cancer_probability_pct')}% risk")
                    else:
                        print(f"   ⚠️  Failed to update record {record_id}")
                except Exception as e:
                    print(f"   ❌ Error processing record {record_id}: {e}")
        
        print(f"\n   ✅ Updated {updated_count} records")
    
    print("\n" + "="*70)
    print("✅ PRODUCTION MIGRATION COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. Restart the Streamlit app")
    print("2. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)")
    print("3. Check dashboard - should now show CatBoost model")
    print("="*70)

if __name__ == '__main__':
    try:
        run_production_migration()
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
