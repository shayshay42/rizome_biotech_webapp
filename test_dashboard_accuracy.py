"""
Test to verify dashboard displays correct values from database
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database import get_db_manager
from utils.cancer_classifier import predict_cancer_risk
import json

def test_dashboard_data_accuracy():
    """Test that values shown in dashboard match what's stored in database"""
    
    print("\n" + "="*70)
    print("DASHBOARD DATA ACCURACY TEST")
    print("="*70)
    
    db = get_db_manager()
    
    # Get the most recent CBC result that has actual values
    query = """
        SELECT id, user_id, wbc, nlr, hgb, mcv, plt, rdw, mono_abs,
               risk_score, risk_interpretation, created_at
        FROM cbc_results
        WHERE wbc IS NOT NULL OR hgb IS NOT NULL OR mono_abs IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 1
    """
    
    result = db.execute_query(query, fetch='one')
    
    if not result:
        print("❌ No CBC results found in database")
        return False
    
    # Convert to dict if needed
    if not isinstance(result, dict):
        columns = ['id', 'user_id', 'wbc', 'nlr', 'hgb', 'mcv', 'plt', 'rdw', 'mono_abs',
                   'risk_score', 'risk_interpretation', 'created_at']
        result = dict(zip(columns, result))
    
    print(f"\n📊 Latest CBC Result (ID: {result['id']})")
    print(f"   Created: {result['created_at']}")
    print("\n1. CBC VALUES IN DATABASE:")
    print(f"   WBC: {result['wbc']} K/uL")
    print(f"   NLR: {result['nlr']} ratio")
    print(f"   HGB: {result['hgb']} g/L")
    print(f"   MCV: {result['mcv']} fL")
    print(f"   PLT: {result['plt']} K/uL")
    print(f"   RDW: {result['rdw']} %")
    print(f"   MONO: {result['mono_abs']} K/uL")
    
    print("\n2. PREDICTION RESULTS IN DATABASE:")
    print(f"   Risk Score: {result['risk_score']}%")
    
    # Parse risk interpretation if it exists
    model_used = "N/A"
    cancer_probability_pct = result['risk_score']  # Fallback to risk_score
    
    if result['risk_interpretation']:
        try:
            interpretation = json.loads(result['risk_interpretation'])
            print(f"\n3. STORED INTERPRETATION:")
            model_used = interpretation.get('model_used', 'N/A')
            cancer_probability_pct = interpretation.get('cancer_probability_pct', result['risk_score'])
            
            print(f"   Model Used: {model_used}")
            print(f"   Cancer Probability: {cancer_probability_pct}%")
            print(f"   Risk Level: {interpretation.get('risk_level', 'N/A')}")
            print(f"   Missing Features: {interpretation.get('missing_features', [])}")
            print(f"   Imputed Count: {interpretation.get('imputed_count', 0)}")
            
            if interpretation.get('model_features'):
                print(f"\n4. MODEL INPUT FEATURES (what the model actually used):")
                for key, value in interpretation['model_features'].items():
                    print(f"   {key}: {value}")
        except Exception as e:
            print(f"   (Could not parse interpretation: {e})")
    
    # Now re-run prediction with same data to verify consistency
    print("\n" + "-"*70)
    print("5. RE-RUNNING PREDICTION TO VERIFY CONSISTENCY:")
    
    cbc_data = {
        'WBC': result['wbc'],
        'NLR': result['nlr'],
        'HGB': result['hgb'],
        'MCV': result['mcv'],
        'PLT': result['plt'],
        'RDW': result['rdw'],
        'MONO': result['mono_abs']
    }
    
    fresh_prediction = predict_cancer_risk(cbc_data)
    
    print(f"   Fresh Prediction: {fresh_prediction.get('cancer_probability_pct')}%")
    print(f"   Model Used: {fresh_prediction.get('model_used')}")
    print(f"   Missing Features: {fresh_prediction.get('missing_features', [])}")
    
    # Compare stored vs fresh prediction
    stored_pct = cancer_probability_pct
    fresh_pct = fresh_prediction.get('cancer_probability_pct')
    
    print("\n" + "="*70)
    print("VALIDATION:")
    print("="*70)
    
    if stored_pct is not None and fresh_pct is not None:
        diff = abs(float(stored_pct) - float(fresh_pct))
        if diff < 0.1:
            print(f"✅ PASS: Predictions match (diff: {diff:.4f}%)")
            print(f"   Stored: {stored_pct}%")
            print(f"   Fresh:  {fresh_pct}%")
            return True
        else:
            print(f"❌ FAIL: Predictions differ by {diff:.2f}%")
            print(f"   Stored: {stored_pct}%")
            print(f"   Fresh:  {fresh_pct}%")
            return False
    else:
        print(f"⚠️  WARNING: Cannot compare (stored={stored_pct}, fresh={fresh_pct})")
        return False

if __name__ == '__main__':
    success = test_dashboard_data_accuracy()
    sys.exit(0 if success else 1)
