"""
Apply migration to add ML prediction columns to cbc_results table
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database import get_db_manager

def apply_migration():
    """Apply the migration to add ML prediction columns"""
    
    print("\n" + "="*70)
    print("APPLYING MIGRATION: Add ML Prediction Columns")
    print("="*70)
    
    db = get_db_manager()
    
    # Read migration SQL
    migration_file = Path(__file__).parent / 'migrations' / 'add_ml_prediction_columns.sql'
    
    with open(migration_file, 'r') as f:
        migration_sql = f.read()
    
    try:
        # Execute migration
        print("\n📝 Executing migration SQL...")
        db.execute_query(migration_sql, fetch=None)
        
        print("✅ Migration executed successfully!")
        
        # Verify columns were added
        print("\n🔍 Verifying columns were added...")
        
        query = """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'cbc_results'
            AND column_name IN (
                'model_used', 
                'cancer_probability_pct', 
                'cancer_probability',
                'healthy_probability',
                'confidence_score',
                'confidence_pct',
                'risk_level',
                'risk_color',
                'prediction',
                'prediction_label',
                'model_loaded',
                'model_load_error'
            )
            ORDER BY column_name
        """
        
        results = db.execute_query(query, fetch='all')
        
        print("\n✅ New columns added:")
        for row in results:
            if not isinstance(row, dict):
                columns = ['column_name', 'data_type']
                row = dict(zip(columns, row))
            print(f"  • {row['column_name']:30s} {row['data_type']}")
        
        print("\n" + "="*70)
        print("✅ MIGRATION COMPLETE!")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error applying migration: {e}")
        return False

if __name__ == '__main__':
    success = apply_migration()
    sys.exit(0 if success else 1)
