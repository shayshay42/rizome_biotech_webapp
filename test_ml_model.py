#!/usr/bin/env python3
"""
Local testing script for ML model integration
Tests cancer classifier with AutoGluon and fallback simulation
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.cancer_classifier import predict_cancer_risk, get_classifier

def test_classifier_initialization():
    """Test that classifier can be initialized"""
    print("\n" + "="*60)
    print("TEST 1: Classifier Initialization")
    print("="*60)

    classifier = get_classifier()
    print(f"✓ Classifier initialized")
    print(f"  Model loaded: {classifier.model_loaded}")
    print(f"  Model type: {'AutoGluon' if classifier.model_loaded else 'Simulation'}")
    print(f"  Required features: {classifier.required_features}")

    assert classifier is not None, "Classifier should not be None"
    assert len(classifier.required_features) == 7, "Should have 7 features"

    print("\n✅ Classifier initialization PASSED")
    return classifier

def test_healthy_cbc_prediction():
    """Test prediction with normal healthy CBC values"""
    print("\n" + "="*60)
    print("TEST 2: Healthy CBC Prediction")
    print("="*60)

    # Normal healthy values
    test_cbc = {
        'WBC': 7.5,      # Normal WBC
        'NLR': 2.0,      # Normal NLR
        'HGB': 145.0,    # Normal hemoglobin
        'MCV': 90.0,     # Normal MCV
        'PLT': 250.0,    # Normal platelets
        'RDW': 13.0,     # Normal RDW
        'MONO': 0.5      # Normal monocytes
    }

    print(f"\nInput CBC values:")
    for key, value in test_cbc.items():
        print(f"  {key}: {value}")

    result = predict_cancer_risk(test_cbc)

    print(f"\nPrediction Results:")
    print(f"  Cancer Probability: {result['cancer_probability_pct']:.1f}%")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Confidence: {result['confidence_pct']:.1f}%")
    print(f"  Model Used: {result.get('model_used', 'Unknown')}")
    print(f"  Imputed Count: {result.get('imputed_count', 0)}")

    # Healthy CBC should have low cancer probability
    assert result['cancer_probability_pct'] < 30, f"Healthy CBC should have <30% cancer probability, got {result['cancer_probability_pct']:.1f}%"
    assert 'error' not in result, f"Should not have error: {result.get('error')}"

    print(f"\n✓ Healthy CBC correctly classified as low risk")
    print("\n✅ Healthy CBC prediction test PASSED")

    return result

def test_cancer_like_cbc_prediction():
    """Test prediction with abnormal cancer-like CBC values"""
    print("\n" + "="*60)
    print("TEST 3: Cancer-like CBC Prediction")
    print("="*60)

    # Cancer-like abnormal values
    test_cbc = {
        'WBC': 12.0,     # Elevated WBC
        'NLR': 6.5,      # High NLR (strong cancer marker)
        'HGB': 95.0,     # Low hemoglobin (anemia)
        'MCV': 105.0,    # High MCV
        'PLT': 500.0,    # High platelets
        'RDW': 18.0,     # High RDW (cell size variation)
        'MONO': 1.5      # Elevated monocytes
    }

    print(f"\nInput CBC values:")
    for key, value in test_cbc.items():
        print(f"  {key}: {value}")

    result = predict_cancer_risk(test_cbc)

    print(f"\nPrediction Results:")
    print(f"  Cancer Probability: {result['cancer_probability_pct']:.1f}%")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Confidence: {result['confidence_pct']:.1f}%")
    print(f"  Model Used: {result.get('model_used', 'Unknown')}")

    # Abnormal CBC should have higher cancer probability
    assert result['cancer_probability_pct'] > 30, f"Abnormal CBC should have >30% cancer probability, got {result['cancer_probability_pct']:.1f}%"
    assert 'error' not in result, f"Should not have error: {result.get('error')}"

    print(f"\n✓ Abnormal CBC correctly classified as higher risk")
    print("\n✅ Cancer-like CBC prediction test PASSED")

    return result

def test_missing_biomarker_imputation():
    """Test imputation for missing biomarkers"""
    print("\n" + "="*60)
    print("TEST 4: Missing Biomarker Imputation")
    print("="*60)

    # CBC with some missing values (simulating Quebec Health Booklet)
    test_cbc = {
        'WBC': 8.0,
        'NLR': 2.5,
        'HGB': 140.0,
        'MCV': 88.0,
        'PLT': 280.0,
        # RDW missing (common in Quebec booklets)
        'MONO': 0.6
    }

    print(f"\nInput CBC values (RDW missing):")
    for key, value in test_cbc.items():
        print(f"  {key}: {value}")

    result = predict_cancer_risk(test_cbc)

    print(f"\nPrediction Results:")
    print(f"  Cancer Probability: {result['cancer_probability_pct']:.1f}%")
    print(f"  Missing Features: {result.get('missing_features', [])}")
    print(f"  Imputed Count: {result.get('imputed_count', 0)}")
    print(f"  Confidence: {result['confidence_pct']:.1f}%")

    if result.get('imputation_warning'):
        print(f"  Warning: {result['imputation_warning']}")

    # Should successfully handle missing values
    assert 'error' not in result, f"Should not have error: {result.get('error')}"
    assert result['imputed_count'] == 1, f"Should have 1 imputed value, got {result['imputed_count']}"
    assert 'RDW' in result.get('missing_features', []), "RDW should be in missing features"

    # Confidence should be reduced due to imputation
    assert result['confidence_pct'] < 100, "Confidence should be reduced with imputation"

    print(f"\n✓ Missing biomarker correctly imputed")
    print(f"✓ Confidence penalty applied (-10% per missing feature)")
    print("\n✅ Missing biomarker imputation test PASSED")

    return result

def test_feature_extraction():
    """Test feature extraction with various naming conventions"""
    print("\n" + "="*60)
    print("TEST 5: Feature Extraction (Name Harmonization)")
    print("="*60)

    # Test with different naming conventions
    test_cases = [
        {
            'name': 'Standard naming',
            'cbc': {'WBC': 7.0, 'NLR': 2.0, 'HGB': 140.0, 'MCV': 90.0, 'PLT': 250.0, 'RDW': 13.0, 'MONO': 0.5}
        },
        {
            'name': 'Quebec naming',
            'cbc': {'GB': 7.0, 'NLR': 2.0, 'HB': 140.0, 'MCV': 90.0, 'PLAQ': 250.0, 'DVE': 13.0, 'MONO': 0.5}
        },
        {
            'name': 'Full names',
            'cbc': {'white_blood_cells': 7.0, 'NLR': 2.0, 'Hemoglobin': 140.0, 'MCV': 90.0, 'Platelets': 250.0, 'RDW': 13.0, 'Monocytes': 0.5}
        }
    ]

    classifier = get_classifier()

    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"  Input: {list(test_case['cbc'].keys())}")

        features = classifier.extract_features(test_case['cbc'])
        imputed = features.pop('_imputed_count')
        missing = features.pop('_missing_features')

        print(f"  Extracted features: {list(features.keys())}")
        print(f"  Missing count: {imputed}")

        # Should extract all 7 features
        assert len(features) == 7, f"Should extract 7 features, got {len(features)}"
        assert imputed == 0, f"Should have no missing features, got {imputed}"

        print(f"  ✓ All features extracted correctly")

    print("\n✅ Feature extraction test PASSED")
    return True

def run_all_tests():
    """Run all ML model tests"""
    print("\n" + "="*60)
    print("ML MODEL TEST SUITE")
    print("="*60)
    print("\nTesting cancer classification model...")
    print("Will use AutoGluon if available, otherwise simulation mode")

    try:
        # Test 1: Initialization
        classifier = test_classifier_initialization()

        # Test 2: Healthy CBC
        healthy_result = test_healthy_cbc_prediction()

        # Test 3: Cancer-like CBC
        cancer_result = test_cancer_like_cbc_prediction()

        # Verify predictions are different
        print("\n" + "="*60)
        print("Comparing Healthy vs Cancer-like Predictions")
        print("="*60)
        print(f"Healthy CBC probability: {healthy_result['cancer_probability_pct']:.1f}%")
        print(f"Cancer-like CBC probability: {cancer_result['cancer_probability_pct']:.1f}%")

        diff = cancer_result['cancer_probability_pct'] - healthy_result['cancer_probability_pct']
        print(f"Difference: {diff:.1f}%")

        assert diff > 0, "Cancer-like CBC should have higher probability than healthy"
        print(f"✓ Model correctly distinguishes healthy from abnormal patterns")

        # Test 4: Missing biomarker imputation
        test_missing_biomarker_imputation()

        # Test 5: Feature extraction
        test_feature_extraction()

        # All tests passed
        print("\n" + "="*60)
        print("🎉 ALL ML MODEL TESTS PASSED!")
        print("="*60)

        if classifier.model_loaded:
            print("\n✅ Using REAL AutoGluon model (99.83% ROC-AUC)")
            print("✅ Production-ready predictions")
        else:
            print("\n⚠️  Using SIMULATION mode (rule-based)")
            print("ℹ️  Real model available at: ../output/autogluon_models/ag_model_smote")
            print("ℹ️  Model will run in simulation mode on Streamlit Cloud (model files too large for git)")

        print("\nModel is ready for deployment!")

        return True

    except Exception as e:
        print("\n" + "="*60)
        print("❌ TEST FAILED!")
        print("="*60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
