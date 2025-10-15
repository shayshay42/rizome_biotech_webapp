"""
Test prediction with Shayan type2 CBC values
"""

import sys
sys.path.insert(0, '.')

from utils.cancer_classifier import predict_cancer_risk

# Shayan type2 CBC values from your carnet santé
cbc_data = {
    'WBC': 4.62,      # K/uL
    'RBC': 4.76,      # M/uL
    'HGB': 16.75,     # g/dL -> need to convert to g/L
    'HCT': 36.02,     # %
    'MCV': 84.89,     # fL
    'PLT': 332.01,    # K/uL
    'RDW': 14.52,     # %
    # NLR calculated from the ratio
    'NLR': 1.4,
}

# Convert HGB from g/dL to g/L (multiply by 10)
cbc_data['HGB'] = cbc_data['HGB'] * 10  # 16.75 g/dL = 167.5 g/L

# We also need MONO - let's check if we can calculate it
# If not provided, the model will impute it

print("="*60)
print("SHAYAN TYPE2 CBC PREDICTION TEST")
print("="*60)

print("\nInput CBC values:")
for key, value in cbc_data.items():
    print(f"  {key}: {value}")

print("\n" + "-"*60)

result = predict_cancer_risk(cbc_data)

print("\n🔬 PREDICTION RESULTS:")
print("="*60)
print(f"Cancer Risk Probability: {result.get('cancer_probability_pct', 'N/A'):.2f}%")
print(f"Risk Level: {result.get('risk_level', 'N/A')}")
print(f"Confidence: {result.get('confidence', 'N/A'):.2f}")
print(f"Model Used: {result.get('model_used', 'N/A')}")

if result.get('imputation_warning'):
    print(f"\n⚠️  {result['imputation_warning']}")

if result.get('missing_features'):
    print(f"\nMissing features (imputed): {', '.join(result['missing_features'])}")

print("\n" + "="*60)

# Expected result based on the test we ran earlier:
# With normal/healthy values, CatBoost should predict very low risk (~0.5-2%)
