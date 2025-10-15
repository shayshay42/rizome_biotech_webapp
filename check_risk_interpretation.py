"""
Check what's in risk_interpretation for record 74
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database import get_db_manager
import json

db = get_db_manager()

query = """
    SELECT id, risk_interpretation, model_used, created_at
    FROM cbc_results
    WHERE id = 74
"""

result = db.execute_query(query, fetch='one')

if result:
    if not isinstance(result, dict):
        columns = ['id', 'risk_interpretation', 'model_used', 'created_at']
        result = dict(zip(columns, result))
    
    print("\n" + "="*70)
    print(f"RECORD 74 - risk_interpretation CONTENT")
    print("="*70)
    print(f"ID: {result['id']}")
    print(f"Model Used: {result['model_used']}")
    print(f"Created: {result['created_at']}")
    print("\nrisk_interpretation type:", type(result['risk_interpretation']))
    print("\nrisk_interpretation content:")
    
    if result['risk_interpretation']:
        try:
            interp = json.loads(result['risk_interpretation'])
            print(json.dumps(interp, indent=2))
            
            print("\n" + "="*70)
            print("CHECKING FOR model_features:")
            if 'model_features' in interp:
                print(f"✅ Found model_features: {interp['model_features']}")
            else:
                print("❌ model_features NOT found in risk_interpretation")
                print("\nAvailable keys:", list(interp.keys()))
        except Exception as e:
            print(f"❌ Could not parse JSON: {e}")
            print("Raw value:", result['risk_interpretation'])
    else:
        print("❌ risk_interpretation is NULL or empty")
    print("="*70)
