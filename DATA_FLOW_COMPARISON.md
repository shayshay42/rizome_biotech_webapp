# Complete Data Flow - Before vs After

## 🔴 OLD ARCHITECTURE (In-Memory Processing)

```
┌─────────────────────────────────────────────────────────────────────┐
│                          STREAMLIT FORM                              │
│  - User uploads PDF or enters manual values                         │
│  - User fills questionnaire                                          │
└──────────────────────────────┬──────────────────────────────────────┘
                                │
                                ↓
        ┌───────────────────────────────────────┐
        │   IF UPLOAD:                          │
        │   extract_cbc_from_pdf(file)          │
        │   → Returns dict in memory            │
        │                                       │
        │   IF MANUAL:                          │
        │   Collect form values → dict          │
        │   → Stays in memory                   │
        └───────────────┬───────────────────────┘
                        │
                        ↓
        ┌───────────────────────────────────────┐
        │   predict_cancer_risk(cbc_data)       │
        │   → Runs ML on in-memory dict         │
        │   → Returns prediction dict           │
        │   → Also stays in memory              │
        └───────────────┬───────────────────────┘
                        │
                        ↓
        ┌───────────────────────────────────────┐
        │   save_cbc_results()                  │
        │   → Saves BOTH CBC data AND           │
        │     predictions together              │
        │   → Single INSERT with all fields     │
        └───────────────┬───────────────────────┘
                        │
                        ↓
        ┌───────────────────────────────────────┐
        │         DATABASE (SQLite/Postgres)    │
        │                                       │
        │   cbc_results table:                  │
        │   - wbc: 7.2                          │
        │   - nlr: 2.5                          │
        │   - cancer_probability: 15.3          │
        │   - risk_level: "Low"                 │
        │   (all saved together)                │
        └───────────────────────────────────────┘

PROBLEMS:
❌ If ML crashes, CBC data is lost
❌ Can't reprocess existing data with new model
❌ Tightly coupled: data collection + ML
❌ No way to separate raw data from predictions
```

---

## 🟢 NEW ARCHITECTURE (Database-First)

```
┌─────────────────────────────────────────────────────────────────────┐
│                          STREAMLIT FORM                              │
│  - User uploads PDF or enters manual values                         │
│  - User fills questionnaire                                          │
└──────────────────────────────┬──────────────────────────────────────┘
                                │
                                ↓
        ┌───────────────────────────────────────┐
        │   STEP 1: EXTRACT/COLLECT             │
        │                                       │
        │   IF UPLOAD:                          │
        │   extract_cbc_from_pdf(file)          │
        │   → Returns dict in memory            │
        │                                       │
        │   IF MANUAL:                          │
        │   Collect form values → dict          │
        │   → Stays in memory                   │
        └───────────────┬───────────────────────┘
                        │
                        ↓
        ┌───────────────────────────────────────┐
        │   STEP 2: SAVE TO DATABASE            │
        │                                       │
        │   save_cbc_data(                      │
        │     user_id, questionnaire_id,        │
        │     cbc_data, test_date, format       │
        │   )                                   │
        │   → Returns: cbc_result_id            │
        └───────────────┬───────────────────────┘
                        │
                        ↓
        ┌───────────────────────────────────────┐
        │         DATABASE (SQLite/Postgres)    │
        │                                       │
        │   cbc_results table:                  │
        │   - id: 123 ✅                        │
        │   - wbc: 7.2 ✅                       │
        │   - nlr: 2.5 ✅                       │
        │   - test_date: 2025-10-08 ✅         │
        │   - cancer_probability: NULL ⏳       │
        │   - risk_level: NULL ⏳               │
        │   (raw data saved, predictions NULL)  │
        └───────────────┬───────────────────────┘
                        │
                        ↓
        ┌───────────────────────────────────────┐
        │   STEP 3: READ FROM DATABASE          │
        │                                       │
        │   get_cbc_data_for_prediction(        │
        │     cbc_result_id=123                 │
        │   )                                   │
        │   → Returns: dict with all biomarkers │
        │   → Read from persistent storage      │
        └───────────────┬───────────────────────┘
                        │
                        ↓
        ┌───────────────────────────────────────┐
        │   STEP 4: RUN ML PREDICTION           │
        │                                       │
        │   predict_cancer_risk(cbc_data)       │
        │   → Uses data FROM database           │
        │   → Runs ML on database data          │
        │   → Returns prediction dict           │
        │   → Stays in memory                   │
        └───────────────┬───────────────────────┘
                        │
                        ↓
        ┌───────────────────────────────────────┐
        │   STEP 5: UPDATE DATABASE             │
        │                                       │
        │   update_cbc_predictions(             │
        │     cbc_result_id=123,                │
        │     prediction_results={...}          │
        │   )                                   │
        │   → UPDATE existing row               │
        └───────────────┬───────────────────────┘
                        │
                        ↓
        ┌───────────────────────────────────────┐
        │         DATABASE (SQLite/Postgres)    │
        │                                       │
        │   cbc_results table:                  │
        │   - id: 123 ✅                        │
        │   - wbc: 7.2 ✅ (unchanged)           │
        │   - nlr: 2.5 ✅ (unchanged)           │
        │   - test_date: 2025-10-08 ✅         │
        │   - cancer_probability: 15.3 ✅ (NEW) │
        │   - risk_level: "Low" ✅ (NEW)        │
        │   (predictions added, raw data intact)│
        └───────────────────────────────────────┘

BENEFITS:
✅ CBC data saved BEFORE ML runs (data safety)
✅ Can reprocess: read → predict → update
✅ Decoupled: data storage vs ML inference
✅ Clear separation: raw biomarkers vs predictions
✅ Audit trail: know when data added vs when analyzed
```

---

## 🔄 Reprocessing Flow (NEW CAPABILITY)

```
┌────────────────────────────────────────────┐
│   MODEL UPDATE OR BATCH REPROCESSING       │
└────────────────┬───────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────┐
│  for cbc_id in get_all_cbc_result_ids():                │
│                                                          │
│      # STEP 1: Read existing CBC data from DB           │
│      cbc_data = get_cbc_data_for_prediction(cbc_id)     │
│                                                          │
│      # STEP 2: Run new/updated model                    │
│      new_prediction = predict_cancer_risk_v2(cbc_data)  │
│                                                          │
│      # STEP 3: Update predictions                       │
│      update_cbc_predictions(cbc_id, new_prediction)     │
│                                                          │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ↓
        ┌─────────────────────────────┐
        │  ALL HISTORICAL DATA        │
        │  REPROCESSED WITH           │
        │  NEW MODEL                  │
        │  ✅ Complete!               │
        └─────────────────────────────┘

THIS WAS IMPOSSIBLE WITH OLD ARCHITECTURE!
```

---

## 📊 Database Schema Evolution

### OLD: Single Transaction
```sql
INSERT INTO cbc_results (
    wbc, nlr, hgb, mcv, plt, rdw, mono,
    cancer_probability,  -- ⚠️ Saved together
    risk_level           -- ⚠️ Saved together
) VALUES (
    7.2, 2.5, 145, 88, 250, 13.2, 0.6,
    15.3,  -- Prediction
    'Low'  -- Prediction
);
```

### NEW: Separate Transactions
```sql
-- Transaction 1: Save raw data
INSERT INTO cbc_results (
    wbc, nlr, hgb, mcv, plt, rdw, mono,
    test_date, file_format
) VALUES (
    7.2, 2.5, 145, 88, 250, 13.2, 0.6,
    '2025-10-08', 'manual_entry'
)
RETURNING id;  -- Returns: 123

-- Transaction 2: Update with predictions (later)
UPDATE cbc_results
SET 
    cancer_probability = 15.3,
    risk_level = 'Low',
    confidence_score = 0.92
WHERE id = 123;
```

---

## 🎯 Real-World Scenarios

### Scenario 1: ML Service Down
**OLD:**
```
User submits → Extract CBC → ML FAILS ❌ → Nothing saved → Data lost 😢
```

**NEW:**
```
User submits → Extract CBC → Save to DB ✅ → ML FAILS ❌
→ CBC data preserved! ✅
→ Can retry ML later when service is up
```

### Scenario 2: Model Update
**OLD:**
```
New model deployed → Historical data stuck with old predictions
→ Would need to ask users to re-upload everything 😢
```

**NEW:**
```
New model deployed → Read all CBC data from DB
→ Rerun predictions with new model
→ Update all records with improved predictions ✅
```

### Scenario 3: Multi-Timepoint Tracking
**OLD & NEW:** Same capability
```
User uploads CBC #1 (Jan) → Saved
User uploads CBC #2 (Feb) → Saved
User uploads CBC #3 (Mar) → Saved

All three entries stored independently
Can track trends over time ✅
```

---

## 🧪 Testing Examples

### Test 1: Data Persistence
```python
# Submit CBC data
cbc_id = save_cbc_data(user_id, q_id, cbc_data)

# Simulate ML crash (don't run prediction)
# Check database - CBC data should be there! ✅

result = query("SELECT * FROM cbc_results WHERE id = ?", cbc_id)
assert result['wbc'] == 7.2  # ✅ Data saved
assert result['cancer_probability'] is None  # ⏳ Prediction not yet
```

### Test 2: Reprocessing
```python
# Save CBC without prediction
cbc_id = save_cbc_data(user_id, q_id, cbc_data)

# Later: run prediction
cbc_data = get_cbc_data_for_prediction(cbc_id)
prediction = predict_cancer_risk(cbc_data)
update_cbc_predictions(cbc_id, prediction)

# Verify
result = query("SELECT * FROM cbc_results WHERE id = ?", cbc_id)
assert result['cancer_probability'] == 15.3  # ✅ Updated
assert result['wbc'] == 7.2  # ✅ Unchanged
```

---

## 📈 Performance Considerations

### Database Reads
- **Old:** 0 reads (everything in memory)
- **New:** 1 read (get_cbc_data_for_prediction)
- **Impact:** Minimal (~1ms for single row SELECT)

### Database Writes
- **Old:** 1 write (INSERT with all fields)
- **New:** 2 writes (INSERT + UPDATE)
- **Impact:** Minimal (~2ms total)

### Trade-off
```
Slight performance cost (1 extra DB operation)
    vs.
Massive flexibility gain (reprocessing, data safety, decoupling)

VERDICT: Worth it! 🎉
```

---

## 🎊 Conclusion

The refactoring transforms the system from:
- ❌ Fragile (data lost on ML failure)
- ❌ Inflexible (can't reprocess)
- ❌ Coupled (data + ML together)

To:
- ✅ Robust (data always saved)
- ✅ Flexible (reprocess anytime)
- ✅ Decoupled (data ≠ predictions)

**Total time investment:** ~30 minutes  
**Value gained:** Infinite 🚀
