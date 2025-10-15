"""
Check if model_used column exists in cbc_results table
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database import get_db_manager

db = get_db_manager()

# Check table schema
query = """
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'cbc_results'
    ORDER BY ordinal_position
"""

try:
    results = db.execute_query(query, fetch='all')
    
    print("\n" + "="*70)
    print("CBC_RESULTS TABLE SCHEMA")
    print("="*70)
    
    model_used_exists = False
    cancer_probability_pct_exists = False
    
    for row in results:
        if not isinstance(row, dict):
            columns = ['column_name', 'data_type']
            row = dict(zip(columns, row))
        
        print(f"  {row['column_name']:30s} {row['data_type']}")
        
        if row['column_name'] == 'model_used':
            model_used_exists = True
        if row['column_name'] == 'cancer_probability_pct':
            cancer_probability_pct_exists = True
    
    print("\n" + "="*70)
    print("COLUMN CHECK:")
    print("="*70)
    print(f"  model_used exists: {'✅ YES' if model_used_exists else '❌ NO'}")
    print(f"  cancer_probability_pct exists: {'✅ YES' if cancer_probability_pct_exists else '❌ NO'}")
    
except Exception as e:
    print(f"❌ Error: {e}")
