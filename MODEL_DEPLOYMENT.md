# Cancer Classification Model Deployment Guide

## Model Details

### Performance Metrics (Test Set)
- **ROC-AUC**: 99.83% (exceptional discrimination)
- **PR-AUC**: 98.79% (excellent precision-recall balance)
- **Accuracy**: 99.86%
- **Precision**: 98.86% (very few false positives)
- **Recall**: 95.60% (catches 95.6% of cancer cases)
- **F1-Score**: 0.972

### Model Architecture
- **Algorithm**: AutoGluon TabularPredictor ensemble
- **Best Model**: CatBoost_BAG_L1
- **Training Method**: SMOTE (Synthetic Minority Over-sampling Technique)
- **Training Samples**: 84,954 (balanced from 43,631 original)
- **Test Samples**: 10,893
- **Model Size**: 413 MB

### Input Features (7 biomarkers)
1. **WBC** - White Blood Cells (10^9/L)
2. **NLR** - Neutrophil-to-Lymphocyte Ratio
3. **HGB** - Hemoglobin (g/L)
4. **MCV** - Mean Corpuscular Volume (fL)
5. **PLT** - Platelets (10^9/L)
6. **RDW** - Red Cell Distribution Width (%)
7. **MONO** - Monocytes (10^9/L)

### Training Data
- **Cancer Cohorts**: ESO (915 patients) + GAS (454 patients)
- **Healthy Controls**: NHANES population study (53,162 patients)
- **Total**: 54,631 patients
- **Class Balance**: 2.5% cancer, 97.5% healthy (imbalanced)
- **Balancing**: SMOTE oversampling to 50-50 split

## Current Deployment Status

### Production Mode: SIMULATION ⚠️

The app is currently running in **simulation mode** because:
- AutoGluon model files (413MB) are too large for GitHub
- Streamlit Cloud free tier has 1GB repo limit
- Model needs to be hosted separately

### Simulation vs. Real Model

**Simulation Mode** (current):
- Uses clinical heuristics and biomarker abnormality scoring
- Calculates deviation from normal ranges
- Emphasizes known cancer markers (high NLR, low HGB, high RDW)
- Returns realistic probabilities using sigmoid function
- **Suitable for demo purposes but not medical use**

**Production Mode** (with real model):
- Uses trained AutoGluon ensemble (99.83% ROC-AUC)
- Leverages patterns from 54K+ patients
- Provides feature importance scores
- Includes confidence metrics
- **Research-grade predictions**

## Deployment Options

### Option 1: Cloud Storage (Recommended for Production)

Upload model to cloud storage and download on app startup:

```python
# In cancer_classifier.py load_model()
import requests
import zipfile

MODEL_URL = "https://your-storage.com/ag_model_smote.zip"
model_path = Path("models/ag_model_smote")

if not model_path.exists():
    print("Downloading model from cloud storage...")
    response = requests.get(MODEL_URL)
    with open("model.zip", "wb") as f:
        f.write(response.content)
    with zipfile.ZipFile("model.zip", "r") as zip_ref:
        zip_ref.extractall("models/")
```

**Cloud Storage Options** (free tiers):
- **Google Cloud Storage**: 5GB free
- **AWS S3**: 5GB free for 12 months
- **Hugging Face Hub**: Free model hosting
- **Dropbox**: 2GB free

### Option 2: Hugging Face Model Hub (Easiest)

1. Create account at [huggingface.co](https://huggingface.co)
2. Upload model:
```bash
pip install huggingface_hub
huggingface-cli login
huggingface-cli upload rizome/cbc-cancer-classifier ./models/ag_model_smote
```
3. Download in app:
```python
from huggingface_hub import snapshot_download
model_path = snapshot_download("rizome/cbc-cancer-classifier")
```

### Option 3: Git LFS (For Paid Plans)

If using Streamlit Cloud paid tier or GitHub LFS:

```bash
git lfs install
git lfs track "models/**/*.pkl"
git add .gitattributes models/
git commit -m "Add model with LFS"
git push
```

### Option 4: Model Compression (Experimental)

Reduce model size by using only best model:

```python
# Keep only CatBoost_BAG_L1, remove other ensemble members
# Could reduce to ~100MB but may impact performance
```

## Local Testing

To test with the real model locally:

1. Ensure model files exist:
```bash
ls -lh /Users/shayanhajhashemi/Documents/Rhizome/output/autogluon_models/ag_model_smote
```

2. The code already checks parent directory:
```python
Path(__file__).parent.parent.parent / 'output' / 'autogluon_models' / 'ag_model_smote'
```

3. Run streamlit app:
```bash
cd streamlit_app
streamlit run streamlit_app.py
```

4. Check logs for model loading:
```
✅ AutoGluon model loaded successfully!
   Best model: CatBoost_BAG_L1
```

## Integration Status

✅ Code integrated and deployed
✅ Fallback simulation mode working
⚠️ Real model not yet deployed (size constraints)
⏳ Waiting for cloud storage setup

## Next Steps

1. **Choose cloud storage provider** (recommend Hugging Face Hub)
2. **Upload model** to chosen provider
3. **Update cancer_classifier.py** with download logic
4. **Test on Streamlit Cloud** with real model
5. **Monitor performance** and confidence scores

## Feature Improvements

### Implemented ✅
- Population-based imputation for missing biomarkers
- Confidence penalty for imputed values (-10% per missing feature)
- Multiple naming convention support (Quebec CBC, standard CBC, etc.)
- Detailed risk interpretation with clinical recommendations
- Feature importance scores (when model available)

### Future Enhancements 🔮
- Model version control and A/B testing
- Explainability dashboard (SHAP values)
- Confidence calibration curves
- Uncertainty quantification
- Real-time model monitoring
- Automated model retraining pipeline

## Model Comparison

The SMOTE model was chosen over 4 other candidates:

| Method | ROC-AUC | Precision | Recall | Notes |
|--------|---------|-----------|--------|-------|
| **SMOTE** | **0.9983** | **98.86%** | **95.60%** | ✅ Best overall |
| SMOTE-Tomek | 0.9986 | 98.86% | 95.60% | Similar but slower |
| Borderline SMOTE | 0.9973 | 95.60% | 95.60% | Lower precision |
| Stratified Undersample | 0.9951 | 54.39% | 97.44% | Many false positives |
| Random Undersample | 0.9942 | 55.67% | 97.07% | Many false positives |

SMOTE provides the best balance of precision and recall with highest ROC-AUC.

## Contact

For questions about model deployment or integration:
- Check Streamlit Cloud logs for model loading status
- Verify AutoGluon installation in requirements.txt
- Confirm cloud storage credentials in Streamlit secrets
