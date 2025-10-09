# New Architecture: Database-First ML Pipeline

## Overview

We've refactored the application to follow a **database-first** approach where:
1. CBC data is saved to database FIRST
2. ML pipeline reads FROM database
3. Predictions are written BACK to database

## Old Flow vs New Flow

### ❌ Old Flow (In-Memory Processing)
```
User Input → Extract/Collect CBC → ML Prediction → Save Everything to DB
                  ↓                      ↓
            (in memory dict)      (in memory prediction)
```

**Problems:**
- Data lost if ML fails
- Can't reprocess existing data
- Tightly coupled: data collection + ML inference
- No audit trail of raw vs predicted data

### ✅ New Flow (Database-First)
```
User Input → Extract/Collect CBC → Save to DB → Read from DB → ML Prediction → Update DB
                  ↓                      ↓            ↓              ↓               ↓
            (in memory dict)      (persistent)  (from DB)   (in memory)    (persistent)
```

**Benefits:**
- ✅ Data persisted immediately, even if ML fails
- ✅ Can reprocess existing data (e.g., model updates)
- ✅ Decoupled: data storage vs ML inference
- ✅ Clear audit trail (raw data + predictions separated)
- ✅ Can run batch predictions on historical data
- ✅ Supports "analyze later" workflows

## New Database Functions

### 1. `save_cbc_data()` - Save Raw CBC Values
```python
cbc_result_id = save_cbc_data(
    user_id=user_id,
    questionnaire_id=questionnaire_id,
    cbc_data={
        'WBC': 7.2,
        'NLR': 2.5,
        'HGB': 145,
        'MCV': 88,
        'PLT': 250,
        'RDW': 13.2,
        'MONO': 0.6
    },
    test_date=date(2025, 10, 8),
    file_format='manual_entry'
)

# Returns: cbc_result_id (integer)
```

**What it does:**
- Inserts CBC biomarker values into `cbc_results` table
- Stores test_date, file_format, extraction_method
- **Does NOT include predictions** (cancer_probability, risk_level, etc. are NULL)
- Returns the inserted row ID for later updates

### 2. `get_cbc_data_for_prediction()` - Retrieve for ML
```python
cbc_data = get_cbc_data_for_prediction(cbc_result_id=123)

# Returns:
{
    'WBC': 7.2,
    'NLR': 2.5,
    'HGB': 145,
    'MCV': 88,
    'PLT': 250,
    'RDW': 13.2,
    'MONO': 0.6,
    'RBC': 4.5,
    'HCT': 42.0,
    ...  # All available biomarkers
}
```

**What it does:**
- Queries the `cbc_results` table by ID
- Returns a dictionary with all CBC values
- Ready to pass to `predict_cancer_risk()`
- Maps database columns to expected feature names (e.g., `mono_abs` → `MONO`)

### 3. `update_cbc_predictions()` - Store ML Results
```python
update_cbc_predictions(
    cbc_result_id=123,
    prediction_results={
        'cancer_probability_pct': 15.3,
        'risk_level': 'Low',
        'confidence': 0.92,
        'prediction_label': 'Healthy',
        'missing_features': ['RBC', 'HCT'],
        'imputed_count': 2,
        'imputation_warning': 'Some values were estimated'
    }
)

# Returns: True if successful
```

**What it does:**
- Updates the `cbc_results` table with ML predictions
- Sets `cancer_probability`, `risk_level`, `confidence_score`
- Stores `missing_biomarkers`, `imputed_count`, `imputation_warning`
- **Preserves original CBC data** (no overwrites)

## Streamlit App Flow

### Form Submission (streamlit_app.py)

```python
if submit_button:
    # Save questionnaire
    questionnaire_id = save_questionnaire(user_id, questionnaire_data)
    
    # STEP 1: Extract/Collect CBC data
    if uploaded_file:
        cbc_data = extract_cbc_from_pdf(uploaded_file)
        file_format = 'pdf'
        test_date = None  # Use current date
    else:
        cbc_data = {
            'WBC': manual_wbc,
            'NLR': manual_nlr,
            ...
        }
        file_format = 'manual_entry'
        test_date = user_selected_date
    
    # STEP 2: Save to database FIRST
    cbc_result_id = save_cbc_data(
        user_id, questionnaire_id, cbc_data, test_date, file_format
    )
    
    if not cbc_result_id:
        st.error("Failed to save CBC data")
        st.stop()
    
    st.success("✅ CBC data saved!")
    
    # STEP 3: Read FROM database for ML
    cbc_data_from_db = get_cbc_data_for_prediction(cbc_result_id)
    
    # STEP 4: Run ML prediction
    prediction = predict_cancer_risk(cbc_data_from_db)
    
    # STEP 5: Update database with predictions
    update_cbc_predictions(cbc_result_id, prediction)
    
    st.success("✅ Analysis complete!")
```

## Key Benefits

### 1. Data Safety
- CBC values saved immediately
- Even if ML crashes, data is preserved
- No data loss from inference failures

### 2. Reprocessing Capability
```python
# Get all CBC results without predictions
unpredicted = get_unpredicted_cbc_results()

for cbc in unpredicted:
    cbc_data = get_cbc_data_for_prediction(cbc['id'])
    prediction = predict_cancer_risk(cbc_data)
    update_cbc_predictions(cbc['id'], prediction)
```

### 3. Model Updates
When you update your cancer classifier:
```python
# Reprocess all historical data with new model
all_cbcs = get_all_cbc_results()

for cbc in all_cbcs:
    cbc_data = get_cbc_data_for_prediction(cbc['id'])
    new_prediction = predict_cancer_risk_v2(cbc_data)  # New model
    update_cbc_predictions(cbc['id'], new_prediction)
```

### 4. Batch Processing
```python
# Process 100 CBCs at once
cbc_ids = [1, 2, 3, ..., 100]

for cbc_id in cbc_ids:
    cbc_data = get_cbc_data_for_prediction(cbc_id)
    prediction = predict_cancer_risk(cbc_data)
    update_cbc_predictions(cbc_id, prediction)
```

### 5. Audit Trail
Database now clearly separates:
- **Raw data:** `wbc`, `nlr`, `hgb`, etc. (immutable)
- **ML predictions:** `cancer_probability`, `risk_level` (updateable)
- **Metadata:** `test_date`, `file_format`, `created_at`

## Database Schema

```sql
CREATE TABLE cbc_results (
    id SERIAL PRIMARY KEY,
    user_id UUID,
    questionnaire_id INTEGER,
    
    -- Metadata
    test_date DATE,
    file_format VARCHAR(50),  -- 'pdf', 'manual_entry', 'image'
    extraction_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Raw CBC biomarkers (immutable after insert)
    wbc REAL,
    nlr REAL,
    hgb REAL,
    mcv REAL,
    plt REAL,
    rdw REAL,
    mono_abs REAL,
    rbc REAL,
    hct REAL,
    ...  -- Other biomarkers
    
    -- ML predictions (NULL initially, updated later)
    cancer_probability REAL,
    prediction_label VARCHAR(50),
    risk_level VARCHAR(50),
    confidence_score REAL,
    missing_biomarkers TEXT[],
    imputed_count INTEGER,
    imputation_warning TEXT
);
```

## Migration Path

### Backward Compatibility

The old `save_cbc_results()` function still exists for legacy code:

```python
# Old way (still works)
save_cbc_results(user_id, cbc_data, prediction_results, questionnaire_id, file_format)

# New way (recommended)
cbc_id = save_cbc_data(user_id, questionnaire_id, cbc_data, test_date, file_format)
cbc_data = get_cbc_data_for_prediction(cbc_id)
prediction = predict_cancer_risk(cbc_data)
update_cbc_predictions(cbc_id, prediction)
```

## Future Enhancements

With this architecture, you can easily add:

1. **Async ML Processing**
   - Save CBC data instantly
   - Show "Analyzing..." message
   - Run ML in background worker
   - Notify user when complete

2. **A/B Testing**
   - Run multiple models on same data
   - Compare predictions
   - Choose best model

3. **Confidence Thresholds**
   - Only save predictions above certain confidence
   - Flag low-confidence results for manual review

4. **Data Quality Checks**
   - Validate CBC data before ML
   - Flag outliers
   - Request user confirmation for unusual values

5. **Versioned Predictions**
   - Keep history of predictions from different model versions
   - Track improvement over time

## Testing

Test the new flow:

```python
# Test 1: Manual entry
cbc_id = save_cbc_data(
    user_id='123',
    questionnaire_id=1,
    cbc_data={'WBC': 7.2, 'NLR': 2.5, ...},
    test_date=date.today(),
    file_format='manual_entry'
)

assert cbc_id is not None

# Test 2: Retrieve for prediction
cbc_data = get_cbc_data_for_prediction(cbc_id)
assert cbc_data['WBC'] == 7.2

# Test 3: Update predictions
prediction = predict_cancer_risk(cbc_data)
success = update_cbc_predictions(cbc_id, prediction)
assert success == True

# Test 4: Verify predictions stored
# (read back from database and check cancer_probability is set)
```

## Summary

**Old approach:** Data and predictions tightly coupled, processed together  
**New approach:** Data saved first, predictions computed from database, updated separately

This separation of concerns makes the system more robust, flexible, and maintainable! 🎉
