"""
Test the merged table display logic
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database import get_db_manager
import json
import pandas as pd

db = get_db_manager()

# Get record 74
query = """
    SELECT id, wbc, hgb, mcv, plt, rdw, nlr, mono_abs, risk_interpretation
    FROM cbc_results
    WHERE id = 74
"""

result = db.execute_query(query, fetch='one')

if not result:
    print("❌ Record not found")
    sys.exit(1)

if not isinstance(result, dict):
    columns = ['id', 'wbc', 'hgb', 'mcv', 'plt', 'rdw', 'nlr', 'mono_abs', 'risk_interpretation']
    result = dict(zip(columns, result))

# Parse risk_interpretation
try:
    detailed_prediction = json.loads(result.get('risk_interpretation', '{}'))
    has_detailed_prediction = bool(detailed_prediction)
except:
    detailed_prediction = {}
    has_detailed_prediction = False

model_features = detailed_prediction.get('model_features', {})
missing_features = detailed_prediction.get('missing_features', [])
imputed_count = detailed_prediction.get('imputed_count', 0)

print("\n" + "="*80)
print("MERGED TABLE DISPLAY TEST")
print("="*80)

# Build table
feature_metadata = {
    'WBC': ('K/uL', 'White Blood Cells'),
    'HGB': ('g/L', 'Hemoglobin'),
    'MCV': ('fL', 'Mean Corpuscular Volume'),
    'PLT': ('K/uL', 'Platelets'),
    'RDW': ('%', 'Red Cell Distribution Width'),
    'NLR': ('ratio', 'Neutrophil-to-Lymphocyte Ratio'),
    'MONO': ('K/uL', 'Monocytes Absolute')
}

db_field_map = {
    'WBC': 'wbc',
    'HGB': 'hgb',
    'MCV': 'mcv',
    'PLT': 'plt',
    'RDW': 'rdw',
    'NLR': 'nlr',
    'MONO': 'mono_abs'
}

table_data = []
for feature_key in ['WBC', 'HGB', 'MCV', 'PLT', 'RDW', 'NLR', 'MONO']:
    unit, full_name = feature_metadata[feature_key]
    
    # Get extracted value from database
    db_field = db_field_map[feature_key]
    extracted_value = result.get(db_field)
    
    # Get model input value
    model_value = model_features.get(feature_key) if model_features else None
    
    # Determine source
    is_imputed = feature_key.upper() in [f.upper() for f in missing_features]
    
    if extracted_value is not None:
        extracted_display = f"{extracted_value:.2f}"
        source = "🔸 Imputed" if is_imputed else "✅ Extracted"
    else:
        extracted_display = "—"
        source = "🔸 Imputed" if is_imputed else "—"
    
    # Model input
    if model_value is not None:
        model_display = f"{model_value:.2f}"
    else:
        model_display = "—"
    
    table_data.append({
        'Feature': f"{feature_key}",
        'Name': full_name,
        'Extracted Value': extracted_display,
        'Model Input': model_display,
        'Unit': unit,
        'Source': source
    })

# Display table
df = pd.DataFrame(table_data)
print("\n📊 CBC Data & Model Input Table:")
print("="*80)
print(df.to_string(index=False))
print("="*80)

print(f"\n📌 Summary:")
print(f"   Missing Features: {missing_features}")
print(f"   Imputed Count: {imputed_count}")

if imputed_count > 0:
    print(f"\nℹ️ {imputed_count} feature(s) were imputed (marked with 🔸)")
else:
    print(f"\n✅ All features extracted - no imputation needed")

print("="*80)
