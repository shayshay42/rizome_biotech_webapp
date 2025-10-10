from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "catboost_cbc.pkl"


def ensure_model_present() -> Path:
    """Return the path to the bundled CatBoost model artifact."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Expected CatBoost model artifact at "
            f"{MODEL_PATH}. Run scripts/export_autogluon_model.py to regenerate it."
        )

    return MODEL_PATH
