"""
Production Cancer Classification Model Integration
Uses a compact CatBoost ensemble exported from the AutoGluon training run.
Features: WBC, NLR, HGB, MCV, PLT, RDW, MONO
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from joblib import load

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "catboost_cbc.pkl"


class _BaggedCatBoostEnsemble:
    """Simple bagged ensemble wrapper for CatBoost base models."""

    def __init__(self, models, feature_names):
        self.models = models
        self.feature_names = feature_names

        try:
            importances = [np.array(model.get_feature_importance()) for model in models]
            if importances:
                self.feature_importances_ = np.mean(importances, axis=0)
            else:
                self.feature_importances_ = None
        except Exception:  # pragma: no cover - defensive safeguard
            self.feature_importances_ = None

    def predict_proba(self, X: pd.DataFrame):
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X, columns=self.feature_names)
        X = X[self.feature_names]

        proba_stack = []
        for model in self.models:
            preds = model.predict_proba(X)
            preds = np.asarray(preds)
            if preds.ndim == 1:
                preds = np.vstack([1 - preds, preds]).T
            proba_stack.append(preds)

        avg_proba = np.mean(proba_stack, axis=0)
        return avg_proba


class CancerClassifier:
    """Production cancer classification using a compact CatBoost ensemble."""

    def __init__(self):
        self.required_features = ['WBC', 'NLR', 'HGB', 'MCV', 'PLT', 'RDW', 'MONO']

        self.feature_ranges = {
            'WBC': (1, 50),
            'NLR': (0.5, 50),
            'HGB': (50, 200),
            'MCV': (60, 120),
            'PLT': (50, 800),
            'RDW': (10, 30),
            'MONO': (0, 5)
        }

        self.imputation_values = {
            'WBC': 7.2,
            'NLR': 2.8,
            'HGB': 140.5,
            'MCV': 88.2,
            'PLT': 285.0,
            'RDW': 13.5,
            'MONO': 0.6
        }

        self.model = None
        self.model_version = "autogluon_catboost_v1"
        self.model_loaded = False
        self.model_load_error = None
        self.model_path = MODEL_PATH

    def load_model(self) -> bool:
        self.model_load_error = None

        if not MODEL_PATH.exists():
            message = (
                "CatBoost model artifact not found. "
                f"Expected at {MODEL_PATH}. Falling back to simulation mode."
            )
            print(f"❌ {message}")
            self.model_loaded = False
            self.model_load_error = message
            return False

        try:
            bundle = load(MODEL_PATH)
            bundle_features = bundle.get("features") or self.required_features
            self.required_features = bundle_features
            self.model_version = bundle.get("version", self.model_version)

            if bundle.get("model_type") == "catboost_bagged":
                models = bundle.get("models", [])
                if not models:
                    raise ValueError("CatBoost bundle missing base models")
                self.model = _BaggedCatBoostEnsemble(models, bundle_features)
            else:
                self.model = bundle.get("model")

            self.model_loaded = self.model is not None
            if self.model_loaded:
                print(f"✅ CatBoost model loaded from {MODEL_PATH}")
            else:
                warning = "Model bundle did not contain an estimator. Using simulation mode."
                print(f"⚠️ {warning}")
                self.model_load_error = warning
            return self.model_loaded
        except Exception as exc:  # pragma: no cover - defensive logging
            print(f"❌ Failed to load CatBoost model: {exc}")
            print("   Using fallback simulation mode")
            self.model_loaded = False
            self.model = None
            self.model_load_error = str(exc)
            return False

    def validate_input(self, data: Dict) -> Tuple[bool, str]:
        for field in self.required_features:
            if field not in data:
                return False, f"Missing required field: {field}"

        for field, (min_val, max_val) in self.feature_ranges.items():
            try:
                value = float(data[field])
                if value < min_val or value > max_val:
                    return False, f"{field} value {value} outside safe range ({min_val}-{max_val})"
            except (ValueError, TypeError):
                return False, f"{field} must be a valid number"

        return True, "Valid input"

    def extract_features(self, cbc_data: Dict) -> Dict:
        import math

        feature_mapping = {
            'WBC': ['WBC', 'GB', 'white_blood_cells'],
            'NLR': ['NLR', 'neutrophil_lymphocyte_ratio'],
            'HGB': ['HGB', 'Hemoglobin', 'HB', 'hemoglobin'],
            'MCV': ['MCV', 'mcv'],
            'PLT': ['PLT', 'Platelets', 'PLAT', 'PLAQ', 'platelets'],
            'RDW': ['RDW', 'DVE', 'rdw'],
            'MONO': ['MONO', 'Monocytes', 'MONO_ABS', 'monocytes']
        }

        extracted_features = {}
        missing_features = []

        for model_feature, possible_names in feature_mapping.items():
            value = None
            for name in possible_names:
                if name in cbc_data:
                    if isinstance(cbc_data[name], dict):
                        value = cbc_data[name].get('value', cbc_data[name])
                    else:
                        value = cbc_data[name]
                    break

            if value is not None and not (isinstance(value, float) and math.isnan(value)):
                try:
                    extracted_features[model_feature] = float(value)
                except (ValueError, TypeError):
                    extracted_features[model_feature] = self.imputation_values[model_feature]
                    missing_features.append(model_feature)
            else:
                extracted_features[model_feature] = self.imputation_values[model_feature]
                missing_features.append(model_feature)

        extracted_features['_missing_features'] = missing_features
        extracted_features['_imputed_count'] = len(missing_features)

        return extracted_features

    def predict(self, features: Dict) -> Dict:
        missing_features = features.pop('_missing_features', [])
        imputed_count = features.pop('_imputed_count', 0)

        is_valid, message = self.validate_input(features)
        if not is_valid:
            return {
                'error': message,
                'prediction': 0,
                'cancer_probability': 0.0,
                'confidence': 0.0,
                'missing_features': missing_features,
                'imputed_count': imputed_count
            }

        try:
            feature_importance = None

            if self.model_loaded and self.model is not None:
                input_df = pd.DataFrame([features])[self.required_features]
                prediction_proba = self.model.predict_proba(input_df)[0]
                cancer_probability = float(prediction_proba[1])

                try:
                    importances = getattr(self.model, "feature_importances_", None)
                    if importances is not None:
                        feature_importance = {
                            feat: float(imp)
                            for feat, imp in zip(self.required_features, importances.tolist())
                        }
                except Exception:
                    feature_importance = None

                model_used = f"CatBoost ({self.model_version})"

            else:
                cancer_probability = self._simulate_prediction(features)
                model_used = "Simulation (rule-based)"

            base_confidence = max(cancer_probability, 1 - cancer_probability)
            confidence_penalty = imputed_count * 0.10
            adjusted_confidence = max(0.5, base_confidence - confidence_penalty)

            cancer_probability_pct = cancer_probability * 100

            if cancer_probability < 0.10:
                risk_level, risk_color = "Very Low", "green"
            elif cancer_probability < 0.30:
                risk_level, risk_color = "Low", "lightgreen"
            elif cancer_probability < 0.60:
                risk_level, risk_color = "Moderate", "orange"
            elif cancer_probability < 0.80:
                risk_level, risk_color = "High", "red"
            else:
                risk_level, risk_color = "Very High", "darkred"

            imputation_warning = None
            if imputed_count > 0:
                imputation_warning = (
                    f"Note: {imputed_count} biomarker(s) were missing and estimated using "
                    f"population averages: {', '.join(missing_features)}. "
                    f"This may affect prediction accuracy (-{confidence_penalty*100:.0f}% confidence)."
                )

            result = {
                'prediction': 1 if cancer_probability > 0.5 else 0,
                'prediction_label': 'Cancer Risk Detected' if cancer_probability > 0.5 else 'Low Cancer Risk',
                'cancer_probability': cancer_probability,
                'cancer_probability_pct': round(cancer_probability_pct, 1),
                'healthy_probability': 1 - cancer_probability,
                'confidence': adjusted_confidence,
                'confidence_pct': round(adjusted_confidence * 100, 1),
                'risk_level': risk_level,
                'risk_color': risk_color,
                'model_used': model_used,
                'model_loaded': self.model_loaded,
                'model_load_error': self.model_load_error,
                'model_path': str(self.model_path),
                'model_features': features,
                'missing_features': missing_features,
                'imputed_count': imputed_count,
                'imputation_warning': imputation_warning
            }

            if feature_importance is not None:
                result['feature_importance'] = feature_importance

            return result

        except Exception as e:  # pragma: no cover - defensive logging
            return {
                'error': f"Prediction failed: {str(e)}",
                'prediction': 0,
                'cancer_probability': 0.0,
                'confidence': 0.0,
                'missing_features': missing_features,
                'imputed_count': imputed_count,
                'model_used': 'Simulation (error)',
                'model_loaded': self.model_loaded,
                'model_load_error': self.model_load_error,
                'model_path': str(self.model_path)
            }

    def _simulate_prediction(self, features: Dict) -> float:
        normal_ranges = {
            'HGB': (120, 170),
            'MCV': (80, 100),
            'MONO': (0.2, 1.0),
            'NLR': (1.0, 4.0),
            'PLT': (150, 450),
            'RDW': (11.5, 14.5),
            'WBC': (4.0, 11.0)
        }

        abnormality_score = 0

        for feature, value in features.items():
            if feature in normal_ranges:
                min_normal, max_normal = normal_ranges[feature]

                if value < min_normal:
                    deviation = (min_normal - value) / min_normal
                    abnormality_score += deviation
                elif value > max_normal:
                    deviation = (value - max_normal) / max_normal
                    abnormality_score += deviation

        if features['NLR'] > 5.0:
            abnormality_score += 2.0
        elif features['NLR'] > 3.5:
            abnormality_score += 1.0

        if features['HGB'] < 100:
            abnormality_score += 1.5
        elif features['HGB'] < 120:
            abnormality_score += 0.5

        if features['RDW'] > 16:
            abnormality_score += 1.0
        elif features['RDW'] > 15:
            abnormality_score += 0.5

        if features['MONO'] > 1.0:
            abnormality_score += 0.8

        cancer_probability = 1 / (1 + np.exp(-2 * (abnormality_score - 2.0)))

        noise = np.random.normal(0, 0.03)
        cancer_probability = np.clip(cancer_probability + noise, 0.01, 0.99)

        return cancer_probability


def get_cancer_risk_interpretation(cancer_probability: float) -> Dict:
    prob_pct = cancer_probability * 100

    if cancer_probability < 0.10:
        return {
            'level': 'Very Low Risk',
            'color': 'green',
            'message': f'Your CBC values indicate very low cancer risk ({prob_pct:.1f}%). Continue regular health monitoring.',
            'recommendations': [
                'Maintain regular annual check-ups',
                'Continue healthy lifestyle practices',
                'No immediate additional testing needed'
            ]
        }
    elif cancer_probability < 0.30:
        return {
            'level': 'Low Risk',
            'color': 'lightgreen',
            'message': f'Your CBC values show low cancer risk ({prob_pct:.1f}%). Some values may warrant monitoring.',
            'recommendations': [
                'Discuss results with your healthcare provider',
                'Consider follow-up testing in 6 months',
                'Monitor any symptoms that develop'
            ]
        }
    elif cancer_probability < 0.60:
        return {
            'level': 'Moderate Risk',
            'color': 'orange',
            'message': f'Your CBC values indicate moderate cancer risk ({prob_pct:.1f}%). Further evaluation is recommended.',
            'recommendations': [
                'Schedule prompt consultation with physician',
                'Additional diagnostic testing may be needed',
                'Do not delay seeking medical advice'
            ]
        }
    elif cancer_probability < 0.80:
        return {
            'level': 'High Risk',
            'color': 'red',
            'message': f'Your CBC values suggest high cancer risk ({prob_pct:.1f}%). Immediate medical evaluation is recommended.',
            'recommendations': [
                'Contact your healthcare provider immediately',
                'Prepare for comprehensive diagnostic workup',
                'Consider oncology referral if indicated'
            ]
        }
    else:
        return {
            'level': 'Very High Risk',
            'color': 'darkred',
            'message': f'Your CBC values indicate very high cancer risk ({prob_pct:.1f}%). Urgent medical attention is required.',
            'recommendations': [
                'Seek immediate medical attention',
                'Do not delay - contact healthcare provider today',
                'Prepare for urgent diagnostic evaluation'
            ]
        }


_classifier = None


def get_classifier():
    """
    Return singleton CancerClassifier instance.
    Uses @st.cache_resource when Streamlit is available for instant reuse.
    """
    global _classifier
    if _classifier is None:
        _classifier = CancerClassifier()
        _classifier.load_model()
    return _classifier


if HAS_STREAMLIT:
    # Wrap in Streamlit cache for production deployment
    get_classifier = st.cache_resource(get_classifier)


def predict_cancer_risk(cbc_data: Dict) -> Dict:
    classifier = get_classifier()
    features = classifier.extract_features(cbc_data)
    prediction_result = classifier.predict(features)

    if 'error' not in prediction_result:
        interpretation = get_cancer_risk_interpretation(prediction_result['cancer_probability'])
        prediction_result['interpretation'] = interpretation

    return prediction_result
