import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from utils import cancer_classifier as cc  # noqa: E402


@pytest.fixture()
def sample_cbc_payload() -> dict:
    return {
        "WBC": 6.2,
        "NLR": 2.4,
        "HGB": 142.0,
        "MCV": 91.5,
        "PLT": 230.0,
        "RDW": 12.7,
        "MONO": 0.48,
    }


def test_predict_cancer_risk_outputs_expected_fields(monkeypatch, sample_cbc_payload):
    classifier = cc.CancerClassifier()
    classifier.model_loaded = False
    monkeypatch.setattr(classifier, "_simulate_prediction", lambda features: 0.82)
    monkeypatch.setattr(cc, "get_classifier", lambda: classifier)

    result = cc.predict_cancer_risk(sample_cbc_payload)

    expected_keys = {
        "prediction",
        "prediction_label",
        "cancer_probability",
        "cancer_probability_pct",
        "confidence",
        "risk_level",
        "missing_features",
        "imputed_count",
        "interpretation",
    }

    assert expected_keys.issubset(result.keys())
    assert pytest.approx(result["cancer_probability"], rel=1e-6) == 0.82
    assert 0.0 <= result["cancer_probability"] <= 1.0
    assert result["interpretation"]["level"]


def test_extract_features_handles_missing_values(sample_cbc_payload):
    classifier = cc.CancerClassifier()
    partial_payload = {"WBC": sample_cbc_payload["WBC"]}

    features = classifier.extract_features(partial_payload)

    assert features["WBC"] == pytest.approx(sample_cbc_payload["WBC"], rel=1e-6)
    assert features["_imputed_count"] == len(classifier.required_features) - 1
    assert "NLR" in features
    assert "_missing_features" in features