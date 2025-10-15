"""
Test the risk score display logic with different values
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database import get_db_manager
import json

def test_risk_score_logic(cbc_results):
    """Simulate the dashboard risk score logic"""
    
    # Get risk score - try cancer_probability_pct first (already a percentage 0-100)
    risk_score = None
    
    # Try to get detailed prediction results
    try:
        detailed_prediction = json.loads(cbc_results.get('risk_interpretation', '{}'))
        has_detailed_prediction = bool(detailed_prediction)
    except Exception:
        detailed_prediction = {}
        has_detailed_prediction = False
    
    # Priority order: cancer_probability_pct (already %) > cancer_probability (decimal 0-1)
    if cbc_results.get('cancer_probability_pct') is not None:
        risk_score = float(cbc_results.get('cancer_probability_pct'))
    elif cbc_results.get('risk_score') is not None:
        risk_score = float(cbc_results.get('risk_score'))
    elif detailed_prediction.get('cancer_probability_pct') is not None:
        risk_score = float(detailed_prediction.get('cancer_probability_pct'))
    elif cbc_results.get('cancer_probability') is not None:
        # This is a decimal (0-1), convert to percentage
        risk_score = float(cbc_results.get('cancer_probability')) * 100
    elif detailed_prediction.get('cancer_probability') is not None:
        # This is a decimal (0-1), convert to percentage
        risk_score = float(detailed_prediction.get('cancer_probability')) * 100
    else:
        risk_score = 0.0

    risk_score = max(0.0, min(100.0, risk_score))
    
    return risk_score

# Test with actual database records
db = get_db_manager()

query = """
    SELECT id, risk_score, cancer_probability_pct, 
           cancer_probability, risk_interpretation, created_at
    FROM cbc_results
    ORDER BY created_at DESC
    LIMIT 3
"""

results = db.execute_query(query, fetch='all')

print("\n" + "="*70)
print("TESTING RISK SCORE DISPLAY LOGIC")
print("="*70)

for result in results:
    if not isinstance(result, dict):
        columns = ['id', 'risk_score', 'cancer_probability_pct', 
                   'cancer_probability', 'risk_interpretation', 'created_at']
        result = dict(zip(columns, result))
    
    print(f"\n📊 Record ID: {result['id']}")
    print(f"   Created: {result['created_at']}")
    print(f"\n   Database Values:")
    print(f"     risk_score: {result['risk_score']}")
    print(f"     cancer_probability_pct: {result['cancer_probability_pct']}")
    print(f"     cancer_probability: {result['cancer_probability']}")
    
    calculated_risk = test_risk_score_logic(result)
    
    print(f"\n   ✅ Dashboard Display: {calculated_risk:.2f}%")
    print("-" * 70)

print("\n" + "="*70)
print("EXPECTED RESULTS:")
print("="*70)
print("Record 76: Should show 0.7% (not 70%)")
print("Record 74: Should show 0.6% (not 60%)")
print("Record 75: Should show 99.0% (correct)")
print("="*70)
