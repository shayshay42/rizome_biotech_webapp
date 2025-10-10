
# Rhizome CBC Analysis - Streamlit Web Application

This application is designed to complement the main Rhizome CBC analysis research platform and provides a user-friendly interface for the underlying machine learning capabilities.

## Bundled CatBoost Ensemble

The production cancer-risk scorer now ships as a compact CatBoost ensemble in
`streamlit_app/models/catboost_cbc.pkl`. The artifact is distilled from the
AutoGluon training run and is small enough to commit directly—no runtime
download required.

To regenerate the bundle from the existing AutoGluon predictor, run:

```bash
python scripts/export_autogluon_model.py
```

This utility loads `models/ag_model_smote`, extracts the bagged CatBoost fold
models (`CatBoost_BAG_L1`), and serializes them into the new joblib bundle.
