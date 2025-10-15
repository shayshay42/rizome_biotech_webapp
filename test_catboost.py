"""
Quick test to verify CatBoost model loads and predicts correctly
"""

import sys
sys.path.insert(0, '.')

from utils.cancer_classifier import get_classifier, predict_cancer_risk

# Test data - similar to what comes from a CBC report
test_cbc_data = {
    'WBC': 7.2,
    'NLR': 2.5,
    'HGB': 140,
    'MCV': 88,
    'PLT': 250,
    'RDW': 13.5,
    'MONO': 0.5
}

print("="*60)
print("CATBOOST MODEL TEST")
print("="*60)

# Get classifier (will use cache if Streamlit is running)
clf = get_classifier()

print(f"\n1. Classifier initialized")
print(f"   Model loaded: {clf.model_loaded}")
print(f"   Model type: {type(clf.model).__name__ if clf.model else 'None'}")
print(f"   Load error: {clf.model_load_error or 'None'}")

# Make prediction
print(f"\n2. Making prediction with test CBC data:")
for k, v in test_cbc_data.items():
    print(f"   {k}: {v}")

result = predict_cancer_risk(test_cbc_data)

print(f"\n3. Prediction result:")
print(f"   Cancer probability: {result.get('cancer_probability_pct', 'N/A'):.1f}%")
print(f"   Risk level: {result.get('risk_level', 'N/A')}")
print(f"   Model used: {result.get('model_used', 'N/A')}")
print(f"   Confidence: {result.get('confidence', 'N/A'):.2f}")

if result.get('model_load_error'):
    print(f"   ❌ ERROR: {result['model_load_error']}")
elif 'CatBoost' in str(result.get('model_used', '')):
    print(f"   ✅ CatBoost model working correctly!")
else:
    print(f"   ⚠️ WARNING: Not using CatBoost model")

print("\n" + "="*60)
