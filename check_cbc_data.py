"""
Check all recent CBC results to find ones with actual values
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database import get_db_manager

db = get_db_manager()

# Get recent CBC results
query = """
    SELECT id, wbc, nlr, hgb, mcv, plt, rdw, mono_abs, risk_score, created_at
    FROM cbc_results
    ORDER BY created_at DESC
    LIMIT 10
"""

results = db.execute_query(query, fetch='all')

print("\n" + "="*70)
print("RECENT CBC RESULTS")
print("="*70)

for i, row in enumerate(results, 1):
    if not isinstance(row, dict):
        columns = ['id', 'wbc', 'nlr', 'hgb', 'mcv', 'plt', 'rdw', 'mono_abs', 'risk_score', 'created_at']
        row = dict(zip(columns, row))
    
    print(f"\n{i}. CBC Result ID: {row['id']} (Created: {row['created_at']})")
    print(f"   WBC: {row['wbc']}, NLR: {row['nlr']}, HGB: {row['hgb']}")
    print(f"   MCV: {row['mcv']}, PLT: {row['plt']}, RDW: {row['rdw']}")
    print(f"   MONO: {row['mono_abs']}, Risk: {row['risk_score']}%")
    
    # Check if has values
    has_values = any([
        row['wbc'] is not None,
        row['nlr'] is not None,
        row['hgb'] is not None,
        row['mono_abs'] is not None
    ])
    
    if has_values:
        print(f"   ✅ HAS VALUES")
    else:
        print(f"   ⚠️  ALL NULL")
