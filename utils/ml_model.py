"""
Mock ML Model for CBC Analysis
This module provides a placeholder ML model that simulates the CBC processing pipeline
until the real model from the main repository is integrated.
"""

import numpy as np
import pandas as pd
import json
from typing import Dict, List, Tuple
import random
from datetime import datetime

def extract_cbc_from_pdf(uploaded_file) -> Dict:
    """
    Mock function to extract CBC values from uploaded PDF/image
    In production, this would use OCR and the existing extraction pipeline
    """
    # Simulate processing time
    np.random.seed(hash(uploaded_file.name) % 1000)
    
    # Mock extracted CBC values with some realistic ranges
    cbc_data = {
        'WBC': np.random.uniform(4.0, 11.0),
        'RBC': np.random.uniform(4.0, 5.5),
        'Hemoglobin': np.random.uniform(11.0, 17.0),
        'Hematocrit': np.random.uniform(35.0, 50.0),
        'MCV': np.random.uniform(80.0, 100.0),
        'MCH': np.random.uniform(26.0, 34.0),
        'MCHC': np.random.uniform(32.0, 36.0),
        'RDW': np.random.uniform(11.0, 16.0),
        'Platelets': np.random.uniform(150, 450),
        'Neutrophils': np.random.uniform(40.0, 70.0),
        'Lymphocytes': np.random.uniform(20.0, 45.0),
        'Monocytes': np.random.uniform(2.0, 10.0),
        'Eosinophils': np.random.uniform(1.0, 4.0),
        'Basophils': np.random.uniform(0.0, 2.0)
    }
    
    # Calculate derived ratios (like NLR)
    if cbc_data['Lymphocytes'] > 0:
        cbc_data['NLR'] = cbc_data['Neutrophils'] / cbc_data['Lymphocytes']
    else:
        cbc_data['NLR'] = np.random.uniform(1.0, 5.0)
    
    return cbc_data

def engineer_temporal_features(cbc_data: Dict) -> np.ndarray:
    """
    Mock function to create temporal features from CBC data
    In production, this would apply the 25-feature engineering pipeline
    from the main repository
    """
    features = []
    
    # For each biomarker, create mock temporal features
    biomarkers = ['WBC', 'RBC', 'Hemoglobin', 'Hematocrit', 'MCV', 'Platelets', 'NLR']
    
    for biomarker in biomarkers:
        if biomarker in cbc_data:
            value = cbc_data[biomarker]
            
            # Mock 25 temporal features per biomarker
            # Descriptive Statistics (8 features)
            features.extend([
                value,  # mean
                value * 0.95,  # median
                value * 0.1,  # std
                value * 0.8,  # min
                value * 1.2,  # max
                value * 0.4,  # range
                value * 0.15,  # IQR
                1.0  # count
            ])
            
            # Temporal Patterns (5 features)
            features.extend([
                np.random.uniform(-0.1, 0.1),  # linear slope
                np.random.choice([-1, 0, 1]),  # trend direction
                np.random.uniform(0.0, 1.0),   # R-squared
                np.random.uniform(0.05, 0.3),  # volatility
                np.random.uniform(30, 365)     # time span (days)
            ])
            
            # Advanced Signal Processing (12 features)
            features.extend([
                np.random.uniform(0.1, 2.0),   # dominant frequency
                np.random.uniform(0.1, 1.0),   # peak power
                np.random.uniform(0.5, 2.0),   # spectral entropy
                np.random.uniform(-0.5, 0.5),  # lyapunov exponent
                np.random.uniform(0.1, 2.0),   # sine amplitude
                np.random.uniform(0.1, 1.0),   # sine frequency
                np.random.uniform(0, 2*np.pi), # sine phase
                value * 0.9,                   # sine offset
                np.random.uniform(0.3, 0.9),   # sine R-squared
                np.random.uniform(-0.3, 0.3),  # lag-1 correlation
                np.random.uniform(0.2, 0.8),   # peak correlation
                np.random.uniform(0.1, 0.5)    # decay rate
            ])
    
    return np.array(features)

def calculate_risk_score(cbc_vector: np.ndarray, questionnaire_data: Dict, cbc_data: Dict) -> float:
    """
    Calculate cancer risk score using the production-trained XGBoost model
    Returns probability as percentage (0-100)
    """
    try:
        from .cancer_classifier import predict_cancer_risk
        
        # Use the production cancer classifier
        prediction_result = predict_cancer_risk(cbc_data)
        
        if 'error' in prediction_result:
            # Fallback to questionnaire-based risk if model fails
            return _calculate_questionnaire_risk(questionnaire_data)
        
        # Return cancer probability as percentage (0-100)
        return prediction_result['cancer_probability_pct']
        
    except Exception as e:
        print(f"Cancer classifier failed: {e}, using fallback")
        return _calculate_questionnaire_risk(questionnaire_data)

def _calculate_questionnaire_risk(questionnaire_data: Dict) -> float:
    """Fallback risk calculation based on questionnaire data"""
    risk_factors = 0
    
    # Age factor
    age = questionnaire_data.get('age', 30)
    if age > 65:
        risk_factors += 20
    elif age > 45:
        risk_factors += 10
    
    # Smoking factor
    smoking = questionnaire_data.get('smoking', 'Never')
    if smoking == 'Current':
        risk_factors += 25
    elif smoking == 'Former':
        risk_factors += 10
    
    # Chronic conditions factor
    chronic_conditions = questionnaire_data.get('chronic_conditions', [])
    if chronic_conditions and 'None' not in chronic_conditions:
        risk_factors += len(chronic_conditions) * 15
    
    # Add some variation
    risk_variation = np.random.uniform(-5, 5)
    final_risk = max(0, min(100, risk_factors + risk_variation))
    
    return round(final_risk, 1)

def get_biomarker_analysis(cbc_data: Dict) -> Dict:
    """
    Analyze biomarkers against normal ranges
    """
    normal_ranges = {
        'WBC': (4.0, 11.0, 'K/uL'),
        'RBC': (4.0, 5.5, 'M/uL'),
        'Hemoglobin': (12.0, 16.0, 'g/dL'),
        'Hematocrit': (36.0, 48.0, '%'),
        'MCV': (82.0, 98.0, 'fL'),
        'MCH': (26.0, 34.0, 'pg'),
        'MCHC': (32.0, 36.0, 'g/dL'),
        'RDW': (11.5, 14.5, '%'),
        'Platelets': (150, 450, 'K/uL'),
        'Neutrophils': (40.0, 70.0, '%'),
        'Lymphocytes': (20.0, 45.0, '%'),
        'Monocytes': (2.0, 10.0, '%'),
        'Eosinophils': (1.0, 4.0, '%'),
        'Basophils': (0.0, 2.0, '%'),
        'NLR': (1.0, 3.0, 'ratio')
    }
    
    analysis = {}
    
    for biomarker, value in cbc_data.items():
        if biomarker in normal_ranges:
            min_val, max_val, unit = normal_ranges[biomarker]
            
            if value < min_val:
                status = 'Low'
                flag = '↓'
            elif value > max_val:
                status = 'High'
                flag = '↑'
            else:
                status = 'Normal'
                flag = '✓'
            
            analysis[biomarker] = {
                'value': round(value, 2),
                'unit': unit,
                'range': f"{min_val}-{max_val}",
                'status': status,
                'flag': flag
            }
    
    return analysis

def process_cbc_upload(uploaded_file, questionnaire_data: Dict) -> Tuple[Dict, np.ndarray, float, Dict]:
    """
    Complete CBC processing pipeline using production cancer classifier
    Returns: (cbc_data, feature_vector, risk_score, detailed_prediction)
    """
    # Step 1: Extract CBC values from file
    cbc_data = extract_cbc_from_pdf(uploaded_file)
    
    # Step 2: Engineer temporal features (for legacy compatibility)
    feature_vector = engineer_temporal_features(cbc_data)
    
    # Step 3: Use production cancer classifier
    try:
        from .cancer_classifier import predict_cancer_risk
        detailed_prediction = predict_cancer_risk(cbc_data)
        
        if 'error' in detailed_prediction:
            # Fallback calculation
            risk_score = _calculate_questionnaire_risk(questionnaire_data)
            detailed_prediction = {'cancer_probability_pct': risk_score}
        else:
            risk_score = detailed_prediction['cancer_probability_pct']
    
    except Exception as e:
        print(f"Production classifier failed: {e}")
        risk_score = _calculate_questionnaire_risk(questionnaire_data)
        detailed_prediction = {'cancer_probability_pct': risk_score}
    
    return cbc_data, feature_vector, risk_score, detailed_prediction

def get_risk_interpretation(risk_score: float) -> Dict:
    """
    Interpret risk score and provide recommendations
    """
    if risk_score < 25:
        return {
            'level': 'Low Risk',
            'color': 'green',
            'message': 'Your CBC values indicate good health status.',
            'recommendations': [
                'Continue maintaining your healthy lifestyle',
                'Regular health check-ups as recommended by your physician',
                'Monitor any changes in symptoms'
            ]
        }
    elif risk_score < 50:
        return {
            'level': 'Moderate Risk',
            'color': 'orange',
            'message': 'Some CBC values may need attention.',
            'recommendations': [
                'Schedule a consultation with your physician',
                'Discuss any symptoms or concerns',
                'Consider lifestyle modifications if recommended',
                'Follow up with additional testing if advised'
            ]
        }
    elif risk_score < 75:
        return {
            'level': 'High Risk',
            'color': 'red',
            'message': 'Several CBC values are outside normal ranges.',
            'recommendations': [
                'Consult your physician promptly',
                'Bring your CBC report to the appointment',
                'Discuss treatment options',
                'Follow prescribed treatment plan closely'
            ]
        }
    else:
        return {
            'level': 'Very High Risk',
            'color': 'darkred',
            'message': 'CBC values indicate significant abnormalities.',
            'recommendations': [
                'Seek immediate medical attention',
                'Do not delay in contacting your healthcare provider',
                'Consider emergency care if experiencing severe symptoms',
                'Follow all medical advice strictly'
            ]
        }