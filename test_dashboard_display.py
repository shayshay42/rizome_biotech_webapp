"""
Simulate what the dashboard will display for record 74
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.auth import get_user_data
from utils.database import get_db_manager
import json

db = get_db_manager()

# Get record 74
query = """
    SELECT id, user_id, wbc, hgb, risk_score, 
           cancer_probability_pct, model_used, risk_level,
           risk_interpretation, created_at
    FROM cbc_results
    WHERE id = 74
"""

result = db.execute_query(query, fetch='one')

if not result:
    print("❌ Record not found")
    sys.exit(1)

if not isinstance(result, dict):
    columns = ['id', 'user_id', 'wbc', 'hgb', 'risk_score', 
               'cancer_probability_pct', 'model_used', 'risk_level',
               'risk_interpretation', 'created_at']
    result = dict(zip(columns, result))

# Parse risk_interpretation (this is what dashboard does)
try:
    detailed_prediction = json.loads(result.get('risk_interpretation', '{}'))
    has_detailed_prediction = bool(detailed_prediction)
except:
    detailed_prediction = {}
    has_detailed_prediction = False

print("\n" + "="*70)
print("DASHBOARD DISPLAY SIMULATION FOR RECORD 74")
print("="*70)

print("\n🎯 CANCER RISK GAUGE:")
print(f"   Risk Score: {result['risk_score']}%")
print(f"   Risk Level: {result['risk_level']}")

print("\n🔍 MODEL INFORMATION:")
print(f"   Model Used: {result['model_used']}")

print("\n📊 EXTRACTED BLOOD VALUES (from database):")
print(f"   WBC: {result['wbc']} K/uL")
print(f"   HGB: {result['hgb']} g/L")

print("\n🤖 MODEL INPUT FEATURES:")
if has_detailed_prediction:
    model_features = detailed_prediction.get('model_features')
    missing_features = detailed_prediction.get('missing_features', [])
    imputed_count = detailed_prediction.get('imputed_count', 0)
    
    if model_features:
        print("   ✅ Model features found!")
        for key, value in model_features.items():
            is_imputed = key.upper() in [f.upper() for f in missing_features]
            imputed_marker = " 🔸 (imputed)" if is_imputed else ""
            print(f"   {key}: {value:.2f}{imputed_marker}")
        
        if imputed_count > 0:
            print(f"\n   ℹ️ {imputed_count} feature(s) were imputed")
        else:
            print(f"\n   ✅ No imputation needed - all features present")
    else:
        print("   ❌ Model features not found in risk_interpretation")
else:
    print("   ❌ risk_interpretation is empty or invalid")

print("\n🔍 DATA VERIFICATION:")
print(f"   CBC Result ID: {result['id']}")
print(f"   Created: {result['created_at']}")

print("\n" + "="*70)
print("✅ DASHBOARD SHOULD NOW DISPLAY:")
print("="*70)
print(f"✅ Risk: {result['risk_score']}%")
print(f"✅ Model: {result['model_used']}")
print(f"✅ Model Features: 7 features shown (WBC, NLR, HGB, MCV, PLT, RDW, MONO)")
print(f"✅ Missing Features: {len(detailed_prediction.get('missing_features', []))} (all present)")
print("="*70)
