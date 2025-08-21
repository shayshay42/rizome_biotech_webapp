#!/usr/bin/env python3
"""
Test Quebec Health Booklet to ML Prediction Pipeline
Test the complete flow from PDF extraction to cancer risk prediction with imputation
"""

import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from quebec_health_booklet_extractor import QuebecHealthBookletExtractor
from utils.cancer_classifier import predict_cancer_risk

def test_quebec_ml_pipeline():
    """Test the complete pipeline from Quebec PDF to ML prediction"""
    
    print("🔬 TESTING QUEBEC HEALTH BOOKLET → ML PREDICTION PIPELINE")
    print("="*80)
    
    # Initialize extractor
    extractor = QuebecHealthBookletExtractor()
    
    # Test file
    pdf_path = "/Users/shayanhajhashemi/Documents/Rhizome/assets/carnetsante/shayan_carnetsante_type2.pdf"
    
    print(f"📄 Extracting from: {Path(pdf_path).name}")
    
    # Step 1: Extract CBC data from PDF
    extraction_result = extractor.extract_from_pdf(pdf_path)
    
    if 'error' in extraction_result:
        print(f"❌ Extraction failed: {extraction_result['error']}")
        return
    
    print(f"✅ Extraction successful!")
    print(f"   - Format: {extraction_result['extraction_metadata']['format']}")
    print(f"   - CBC tests found: {extraction_result['extraction_metadata']['cbc_tests_found']}")
    print(f"   - ML features extracted: {extraction_result['extraction_metadata']['ml_ready_features']}")
    
    # Display extracted patient info
    if extraction_result['patient_info']:
        print(f"\n👤 Patient Info:")
        for key, value in extraction_result['patient_info'].items():
            print(f"   {key}: {value}")
    
    # Display CBC data
    print(f"\n🧪 CBC Data:")
    for test, data in extraction_result['cbc_data'].items():
        flag_str = f" [{data['flag']}]" if data['flag'] else ""
        print(f"   {test}: {data['value']} {data['unit']}{flag_str}")
    
    # Display ML features
    print(f"\n🤖 ML Features (for cancer prediction):")
    for biomarker, value in extraction_result['ml_features'].items():
        value_str = f"{value:.2f}" if value == value else "NaN (will be imputed)"  # NaN check
        print(f"   {biomarker}: {value_str}")
    
    # Step 2: Predict cancer risk using ML model
    print(f"\n🎯 CANCER RISK PREDICTION")
    print("-" * 40)
    
    prediction_result = predict_cancer_risk(extraction_result['ml_features'])
    
    if 'error' in prediction_result:
        print(f"❌ Prediction failed: {prediction_result['error']}")
        return
    
    # Display prediction results
    print(f"🎯 Prediction: {prediction_result['prediction_label']}")
    print(f"📊 Cancer Probability: {prediction_result['cancer_probability_pct']:.1f}%")
    print(f"🔒 Confidence: {prediction_result['confidence_pct']:.1f}%")
    print(f"⚠️  Risk Level: {prediction_result['risk_level']}")
    
    # Display imputation information
    if prediction_result.get('imputed_count', 0) > 0:
        print(f"\n⚠️  IMPUTATION NOTICE:")
        print(f"   Missing biomarkers: {prediction_result['missing_features']}")
        print(f"   Number imputed: {prediction_result['imputed_count']}")
        if prediction_result.get('imputation_warning'):
            print(f"   Warning: {prediction_result['imputation_warning']}")
    
    # Display interpretation
    if 'interpretation' in prediction_result:
        interpretation = prediction_result['interpretation']
        print(f"\n📋 CLINICAL INTERPRETATION:")
        print(f"   Level: {interpretation['level']}")
        print(f"   Message: {interpretation['message']}")
        print(f"   Recommendations:")
        for rec in interpretation['recommendations']:
            print(f"     • {rec}")
    
    # Display feature values used
    print(f"\n🔍 MODEL INPUT FEATURES:")
    for feature, value in prediction_result['model_features'].items():
        if feature.startswith('_'):
            continue
        status = ""
        if feature in prediction_result.get('missing_features', []):
            status = " (imputed)"
        print(f"   {feature}: {value:.2f}{status}")
    
    print(f"\n✅ Pipeline test completed successfully!")

if __name__ == "__main__":
    test_quebec_ml_pipeline()