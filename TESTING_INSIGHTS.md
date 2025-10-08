# Testing & Development Insights

**Context:** This document captures key knowledge from testing scripts before cleanup.
**Date:** 2025-10-08

---

## Supabase Connection Lessons Learned

### What Works ✅
**Connection Method:** Transaction Pooler (IPv4 compatible)
- Host: `aws-1-ca-central-1.pooler.supabase.com`
- Port: `6543` (NOT 5432)
- Username format: `postgres.{project-ref}` (e.g., `postgres.kqzmwzosluljckadthup`)
- Region: Canada Central

**Why This Matters:**
- Direct connection (`db.{project}.supabase.co:5432`) requires IPv6
- Many networks don't support IPv6
- Transaction Pooler works on ALL networks (IPv4)

### What Doesn't Work ❌
- Direct connection via `db.kqzmwzosluljckadthup.supabase.co:5432` → DNS fails
- Username just `postgres` → "Tenant or user not found" error
- Using port 5432 with pooler → Connection refused

---

## Quebec Health Booklet PDF Extraction

### Key Finding: Missing RDW Biomarker
**Pattern:** Quebec Health Booklet PDFs consistently missing RDW (Red Cell Distribution Width)

**Solution Implemented:**
- Extract available biomarkers: WBC, HGB, PLT, MCV, MONO, NLR (6 of 7)
- Use `numpy.nan` for missing RDW
- Impute using population average (13.5%)
- Reduce confidence score by 10% per missing biomarker
- Display warning to user

**From:** `test_quebec_ml_pipeline.py`, `quebec_health_booklet_extractor.py`

**Example Test Result:**
```python
{
    'HGB': 137.0,    # Present
    'WBC': 5.87,     # Present  
    'PLT': 191.0,    # Present
    'MCV': 88.9,     # Present
    'MONO': 0.38,    # Present
    'NLR': 2.59,     # Calculated from NEUT%/LYMPH%
    'RDW': np.nan    # Missing → imputed as 13.5
}

# ML Prediction:
cancer_probability: 1.6%
confidence: 88.4%  # Reduced from 98.4% due to 1 missing biomarker
```

---

## Database Schema Evolution

### Initial Problem
**From:** `fix_database_schema.py`, `check_supabase_connection.py`

The Supabase database had **mixed schema**:
- App schema: users (id, username, email, password_hash)
- Supabase Auth schema: 35+ extra columns (instance_id, aud, role, etc.)
- Questionnaires: Wrong column names (q1_, q2_ instead of age, weight, sex)
- CBC results: Missing columns (filename, raw_extraction_data, cbc_vector)

### Solution Applied
**From:** Database rebuild in this session

1. **Dropped all tables** - Clean slate
2. **Created app-compatible schema:**
   - users: 6 columns (id, username, email, password_hash, created_at, last_login)
   - questionnaires: 13 columns (age, weight, height, sex, activity_level, etc.)
   - cbc_results: 38 columns (all biomarkers + ML results + Quebec support)
3. **Added performance indexes** - 22 total for fast queries

### Key Schema Decisions
- Used TEXT for JSON storage (raw_extraction_data, cbc_vector, risk_interpretation)
- Added Quebec-specific columns: missing_biomarkers (TEXT[]), imputed_count (INTEGER), imputation_warning (TEXT)
- Foreign keys with CASCADE delete for data integrity
- Both processed_at and created_at timestamps for audit trail

---

## PDF Format Detection

### CarnetSanté Format Variations
**From:** `analyze_carnetsante_formats.py`, `universal_carnetsante_extractor.py`

**Two Main Formats Identified:**

1. **Traditional Lab Report:**
   - Has 23+ biomarkers
   - French/English pairs: GB/WBC, HB/HGB, PLAQ/PLT
   - Complete differential counts
   - Usually has RDW

2. **Quebec Health Booklet (Type 2):**
   - Has 8 biomarkers only
   - French names: Leucocytes, Hémoglobine, Plaquettes
   - Missing: RDW, often missing MPV
   - Neutrophil/Lymphocyte percentages → calculate NLR

**Auto-Detection Strategy:**
```python
def detect_format(pdf_text):
    if 'CarnetSanté' in pdf_text and 'Leucocytes' in pdf_text:
        return 'quebec_health_booklet'
    elif 'GB' in pdf_text or 'PLAQ' in pdf_text:
        return 'traditional_lab'
    else:
        return 'unknown'
```

---

## Database Connection Testing

### Testing Sequence
**From:** `test_database_system.py`, `final_supabase_test.py`

**Proper test order:**
1. Test Supabase connection (psycopg2)
2. Test table existence
3. Test user INSERT
4. Test questionnaire INSERT with foreign key
5. Test CBC result INSERT with all columns
6. Test JOIN queries (users → questionnaires → cbc_results)
7. Test CASCADE delete
8. Clean up test data

**Critical Test Case:**
```python
# This pattern validates entire data flow:
user_id = insert_user(username, email, password_hash)
quest_id = insert_questionnaire(user_id, age, weight, ...)
cbc_id = insert_cbc_result(user_id, quest_id, biomarkers, ...)

# Verify with JOIN:
SELECT u.username, q.age, c.hgb 
FROM users u
JOIN questionnaires q ON u.id = q.user_id  
JOIN cbc_results c ON u.id = c.user_id
WHERE u.id = user_id
```

---

## Migration & Setup Scripts

### Database Migration Pattern
**From:** `migrate_database.py`, `recreate_database.py`

**Pattern Used:**
1. Check if tables exist
2. If yes: backup data → drop tables → recreate → restore data
3. If no: create fresh tables
4. Add indexes after table creation (faster)
5. Verify with sample insert

**Key Lesson:** Always use CASCADE when dropping tables with foreign keys:
```sql
DROP TABLE IF EXISTS cbc_results CASCADE;
DROP TABLE IF EXISTS questionnaires CASCADE;  
DROP TABLE IF EXISTS users CASCADE;
```

### Supabase Setup Insights
**From:** `setup_supabase.py`, `find_supabase_host.py`

**Discovery Process:**
1. Tried direct connection → Failed (IPv6 issue)
2. Searched for pooler endpoint formats
3. Found regional patterns: `aws-{region-number}-{region-name}.pooler.supabase.com`
4. Tested multiple regions (us-east-1, us-west-1, eu-west-1, etc.)
5. Found project in Canada Central region
6. Learned username must be `postgres.{project_ref}` for pooler

---

## ML Pipeline Integration

### Test Pipeline Flow
**From:** `test_quebec_ml_pipeline.py`

**Complete Flow Validated:**
```
Quebec PDF Upload
    ↓
quebec_health_booklet_extractor.py (extract 6/7 biomarkers)
    ↓
Add np.nan for missing RDW
    ↓
utils/cancer_classifier.py (impute missing values)
    ↓
XGBoost prediction (with confidence adjustment)
    ↓
Display results with imputation warning
```

**Key Metrics from Testing:**
- Extraction success rate: 100% for Quebec PDFs
- Biomarker coverage: 6/7 (86%)
- Imputation accuracy: Population-based (RDW mean=13.5, std=1.8)
- Confidence reduction: -10% per missing biomarker
- Processing time: <2 seconds per PDF

---

## Production Deployment Insights

### Pre-Deployment Checklist
**From:** Testing experience

**Must Verify:**
1. ✅ Supabase connection works (Transaction Pooler)
2. ✅ All table schemas match app expectations
3. ✅ Foreign keys configured with CASCADE
4. ✅ Indexes created for performance
5. ✅ secrets.toml in .gitignore
6. ✅ No .db files in git
7. ✅ requirements.txt has psycopg2-binary (NOT psycopg2)
8. ✅ Test with Quebec PDF before going live

### Common Pitfalls Avoided
1. ❌ Using direct connection (IPv6) instead of pooler (IPv4)
2. ❌ Wrong username format (just "postgres" vs "postgres.{project}")
3. ❌ Schema mismatch between SQLite (dev) and PostgreSQL (prod)
4. ❌ Missing CASCADE on foreign keys (orphaned records)
5. ❌ Not handling missing biomarkers gracefully
6. ❌ Committing secrets.toml or .db files to git

---

## Key Takeaways for Future Development

### What Worked Well ✅
- Transaction Pooler for universal compatibility
- Mixed SQLite (dev) + PostgreSQL (prod) architecture
- Quebec Health Booklet specific handling with imputation
- Comprehensive testing scripts caught all issues early
- Foreign keys with CASCADE prevent orphaned data

### What to Remember 🧠
- Always use pooler connection for Supabase (IPv4 compatible)
- Quebec PDFs will always miss RDW - this is expected
- Test full data flow: user → questionnaire → CBC result → JOIN
- Keep schema identical between SQLite and PostgreSQL
- Document unusual patterns (like Quebec missing biomarkers)

### Next Steps for Production 🚀
1. Deploy to Streamlit Community Cloud
2. Add secrets via Cloud dashboard (use pooler connection)
3. Test with real Quebec Health Booklet PDF
4. Monitor Supabase dashboard for query performance
5. Set up connection pooling alerts (if usage grows)

---

**Files This Knowledge Came From:**
- test_quebec_ml_pipeline.py
- check_supabase_connection.py
- find_supabase_host.py
- final_supabase_test.py
- test_database_system.py
- fix_database_schema.py
- migrate_database.py
- setup_supabase.py
- analyze_carnetsante_formats.py
- universal_carnetsante_extractor.py

**Total Testing Scripts:** 18 files → Knowledge distilled to this single reference document.

---

**When in doubt during deployment, refer back to:**
- Connection: Use Transaction Pooler (aws-1-ca-central-1.pooler.supabase.com:6543)
- Username: postgres.{project_ref}
- Schema: 3 tables (users 6 cols, questionnaires 13 cols, cbc_results 38 cols)
- Quebec PDFs: Missing RDW is normal, impute with 13.5
