"""
Test updating an existing CBC record with model predictions
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database import get_db_manager, update_cbc_predictions
from utils.cancer_classifier import predict_cancer_risk

def test_update_existing_record():
    """Test updating record 74 with model predictions"""
    
    print("\n" + "="*70)
    print("TEST: Update Existing CBC Record with Model Predictions")
    print("="*70)
    
    cbc_result_id = 74
    
    # Get current record
    db = get_db_manager()
    
    query = """
        SELECT id, wbc, nlr, hgb, mcv, plt, rdw, mono_abs,
               risk_score, cancer_probability_pct, model_used
        FROM cbc_results
        WHERE id = %s
    """
    
    record = db.execute_query(query, (cbc_result_id,), fetch='one')
    
    if not record:
        print(f"❌ Record {cbc_result_id} not found")
        return False
    
    if not isinstance(record, dict):
        columns = ['id', 'wbc', 'nlr', 'hgb', 'mcv', 'plt', 'rdw', 'mono_abs',
                   'risk_score', 'cancer_probability_pct', 'model_used']
        record = dict(zip(columns, record))
    
    print(f"\n1. CURRENT RECORD (ID {cbc_result_id}):")
    print(f"   WBC: {record['wbc']}")
    print(f"   HGB: {record['hgb']}")
    print(f"   Risk Score: {record['risk_score']}")
    print(f"   Cancer Probability Pct: {record['cancer_probability_pct']}")
    print(f"   Model Used: {record['model_used']}")
    
    # Create CBC data from record
    cbc_data = {
        'WBC': record['wbc'] or 7.2,
        'NLR': record['nlr'] or 2.5,
        'HGB': record['hgb'] or 145.0,
        'MCV': record['mcv'] or 88.0,
        'PLT': record['plt'] or 250.0,
        'RDW': record['rdw'] or 13.2,
        'MONO': record['mono_abs'] or 0.6
    }
    
    print(f"\n2. RUNNING PREDICTION ON THIS DATA...")
    prediction_result = predict_cancer_risk(cbc_data)
    
    print(f"\n3. PREDICTION RESULT:")
    print(f"   Cancer Probability: {prediction_result.get('cancer_probability_pct')}%")
    print(f"   Model Used: {prediction_result.get('model_used')}")
    print(f"   Risk Level: {prediction_result.get('risk_level')}")
    
    print(f"\n4. UPDATING DATABASE RECORD {cbc_result_id}...")
    success = update_cbc_predictions(cbc_result_id, prediction_result)
    
    if success:
        print(f"   ✅ Update successful!")
    else:
        print(f"   ❌ Update failed!")
        return False
    
    # Verify the update
    print(f"\n5. VERIFYING UPDATE...")
    updated_record = db.execute_query(query, (cbc_result_id,), fetch='one')
    
    if not isinstance(updated_record, dict):
        updated_record = dict(zip(columns, updated_record))
    
    print(f"   Risk Score: {updated_record['risk_score']}")
    print(f"   Cancer Probability Pct: {updated_record['cancer_probability_pct']}")
    print(f"   Model Used: {updated_record['model_used']}")
    
    print("\n" + "="*70)
    if updated_record['model_used']:
        print("✅ SUCCESS: model_used is now saved in database!")
        print(f"   Model: {updated_record['model_used']}")
    else:
        print("❌ FAILED: model_used is still NULL")
    print("="*70)
    
    return updated_record['model_used'] is not None

if __name__ == '__main__':
    success = test_update_existing_record()
    sys.exit(0 if success else 1)
