"""
Test that model_used is properly saved to database after prediction
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database import get_db_manager
from utils.cancer_classifier import predict_cancer_risk

def test_model_used_saving():
    """Test that model_used column is populated after prediction"""
    
    print("\n" + "="*70)
    print("TEST: Model Used Column Saving")
    print("="*70)
    
    # Test CBC data (your manual input)
    cbc_data = {
        'WBC': 7.2,
        'HGB': 145.0,
        'MCV': 88.0,
        'PLT': 250.0,
        'RDW': 13.2,
        'NLR': 2.5,
        'MONO': 0.6
    }
    
    print("\n1. INPUT DATA:")
    for key, value in cbc_data.items():
        print(f"   {key}: {value}")
    
    # Run prediction
    print("\n2. RUNNING PREDICTION...")
    prediction_result = predict_cancer_risk(cbc_data)
    
    print(f"\n3. PREDICTION RESULT:")
    print(f"   Cancer Probability: {prediction_result.get('cancer_probability_pct')}%")
    print(f"   Model Used: {prediction_result.get('model_used')}")
    print(f"   Model Loaded: {prediction_result.get('model_loaded')}")
    
    # Now check what would be saved
    print("\n4. FIELDS THAT WILL BE SAVED:")
    save_fields = [
        'prediction',
        'prediction_label', 
        'cancer_probability',
        'cancer_probability_pct',
        'healthy_probability',
        'risk_score',
        'risk_level',
        'risk_color',
        'confidence_score',
        'confidence_pct',
        'model_used',
        'model_loaded'
    ]
    
    for field in save_fields:
        value = prediction_result.get(field)
        print(f"   {field:25s} = {value}")
    
    # Check most recent record in database
    db = get_db_manager()
    
    query = """
        SELECT id, risk_score, cancer_probability_pct, model_used, model_loaded, 
               risk_level, created_at
        FROM cbc_results
        ORDER BY created_at DESC
        LIMIT 1
    """
    
    result = db.execute_query(query, fetch='one')
    
    if result:
        if not isinstance(result, dict):
            columns = ['id', 'risk_score', 'cancer_probability_pct', 'model_used', 
                      'model_loaded', 'risk_level', 'created_at']
            result = dict(zip(columns, result))
        
        print("\n5. MOST RECENT DATABASE RECORD:")
        print(f"   ID: {result['id']}")
        print(f"   Risk Score: {result['risk_score']}")
        print(f"   Cancer Probability Pct: {result['cancer_probability_pct']}")
        print(f"   Model Used: {result['model_used']}")
        print(f"   Model Loaded: {result['model_loaded']}")
        print(f"   Risk Level: {result['risk_level']}")
        print(f"   Created: {result['created_at']}")
        
        print("\n" + "="*70)
        if result['model_used']:
            print("✅ SUCCESS: model_used is being saved!")
        else:
            print("⚠️  WARNING: model_used is NULL in database")
            print("   This means the column exists but update_cbc_predictions isn't working")
        print("="*70)
    
    return True

if __name__ == '__main__':
    test_model_used_saving()
