"""
Check the latest CBC record to see actual risk score values
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database import get_db_manager
import json

db = get_db_manager()

query = """
    SELECT id, user_id, risk_score, cancer_probability_pct, 
           cancer_probability, risk_interpretation, created_at
    FROM cbc_results
    ORDER BY created_at DESC
    LIMIT 3
"""

results = db.execute_query(query, fetch='all')

print("\n" + "="*70)
print("RECENT CBC RECORDS - RISK SCORE VALUES")
print("="*70)

for result in results:
    if not isinstance(result, dict):
        columns = ['id', 'user_id', 'risk_score', 'cancer_probability_pct', 
                   'cancer_probability', 'risk_interpretation', 'created_at']
        result = dict(zip(columns, result))
    
    print(f"\nRecord ID: {result['id']}")
    print(f"Created: {result['created_at']}")
    print(f"risk_score (DB field): {result['risk_score']}")
    print(f"cancer_probability_pct (DB field): {result['cancer_probability_pct']}")
    print(f"cancer_probability (DB field): {result['cancer_probability']}")
    
    # Parse risk_interpretation
    if result['risk_interpretation']:
        try:
            interp = json.loads(result['risk_interpretation'])
            print(f"cancer_probability (in JSON): {interp.get('cancer_probability')}")
            print(f"cancer_probability_pct (in JSON): {interp.get('cancer_probability_pct')}")
        except:
            pass
    
    print("-" * 70)
