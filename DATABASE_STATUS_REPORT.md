# Database Status & Schema Analysis Report

**Date:** 2025-10-08
**Status:** ⚠️ Schema Mismatch Identified

## Executive Summary

✅ **Supabase Connection:** WORKING (Transaction Pooler, IPv4 compatible)
⚠️ **Schema Status:** Mismatch between app expectations and Supabase schema
📊 **Tables Present:** users, questionnaires, cbc_results (all exist)
🔧 **Action Required:** Schema alignment needed for production use

---

## Connection Configuration ✅

### Working Configuration
```toml
[supabase]
host = "aws-1-ca-central-1.pooler.supabase.com"  # Transaction Pooler
port = "6543"                                     # IPv4 compatible
user = "postgres.kqzmwzosluljckadthup"           # Correct format
password = "ZnJJSIChnpkAmtcS"
database = "postgres"
```

### Key Findings
- ✅ Transaction Pooler connection successful (Canada Central region)
- ✅ PostgreSQL 17.4 running
- ❌ Direct connection (`db.[project].supabase.co:5432`) does NOT work (IPv6 issue)
- ✅ App correctly falls back to SQLite when Supabase unavailable

---

## Schema Comparison

### 1. Users Table

**App Expects (SQLite schema in `auth.py`):**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
```

**Supabase Has (40 columns - MIXED SCHEMA):**
```sql
-- App columns (CORRECT):
id INTEGER PRIMARY KEY
username VARCHAR(50) UNIQUE NOT NULL
password_hash VARCHAR(255) NOT NULL
email VARCHAR(100)
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

-- Supabase Auth columns (EXTRA - not used by app):
instance_id, aud, role, encrypted_password, email_confirmed_at,
invited_at, confirmation_token, recovery_token, phone, is_super_admin,
is_sso_user, deleted_at, is_anonymous, etc. (35+ extra columns)
```

**Issue:** Supabase has both app schema AND Supabase Auth schema merged. App only uses 5 columns.

### 2. Questionnaires Table

**App Expects:**
```sql
CREATE TABLE questionnaires (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    age INTEGER,
    weight REAL,
    height REAL,
    sex TEXT,
    activity_level TEXT,
    smoking TEXT,
    chronic_conditions TEXT,
    medications TEXT,
    family_history TEXT,
    symptoms TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

**Supabase Has:**
```sql
CREATE TABLE questionnaires (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    q1_family_history BOOLEAN,
    q2_smoking_status VARCHAR(20),
    q3_alcohol_consumption VARCHAR(20),
    q4_previous_cancer BOOLEAN,
    q5_medications TEXT,
    q6_symptoms TEXT,
    q7_recent_infections BOOLEAN,
    q8_chronic_conditions TEXT,
    q9_exercise_frequency VARCHAR(20),
    q10_stress_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Issue:** Column names completely different! App uses `age`, `weight`, `sex` but Supabase has `q1_family_history`, `q2_smoking_status`, etc.

### 3. CBC Results Table

**App Expects:**
```sql
CREATE TABLE cbc_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    questionnaire_id INTEGER,
    filename TEXT,
    file_format TEXT,
    extraction_success BOOLEAN DEFAULT TRUE,

    -- Raw extraction data
    raw_extraction_data TEXT,  -- JSON
    patient_info TEXT,  -- JSON

    -- Biomarkers (wbc, rbc, hgb, etc.)
    wbc REAL, rbc REAL, hgb REAL, hct REAL, mcv REAL, mch REAL,
    mchc REAL, rdw REAL, plt REAL, mpv REAL,
    neut_abs REAL, neut_pct REAL, lymph_abs REAL, lymph_pct REAL,
    mono_abs REAL, mono_pct REAL, eos_abs REAL, eos_pct REAL,
    baso_abs REAL, baso_pct REAL, nlr REAL,

    -- Additional
    additional_tests TEXT,  -- JSON
    cbc_vector TEXT,  -- JSON of 175 features
    risk_score REAL,
    risk_interpretation TEXT,  -- JSON

    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (questionnaire_id) REFERENCES questionnaires (id)
)
```

**Supabase Has:**
```sql
CREATE TABLE cbc_results (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    questionnaire_id INTEGER REFERENCES questionnaires(id),
    test_date DATE,  -- NOT filename
    file_format VARCHAR(50),
    extraction_method VARCHAR(50),  -- NOT extraction_success

    -- Biomarkers (SAME)
    wbc REAL, rbc REAL, hgb REAL, ... (all biomarkers match)

    -- ML results (DIFFERENT column names)
    cancer_probability REAL,  -- NOT risk_score
    prediction_label VARCHAR(50),
    risk_level VARCHAR(20),
    confidence_score REAL,

    -- Quebec-specific (NEW - not in app)
    missing_biomarkers TEXT[],
    imputed_count INTEGER DEFAULT 0,
    imputation_warning TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- NOT processed_at
)
```

**Issue:** Some columns missing (filename, raw_extraction_data, cbc_vector), some different names (risk_score vs cancer_probability), some extra Quebec-specific columns.

---

## App Database Operations

### Write Operations in `auth.py`:

1. **User Registration** (Line 154-156):
```python
cursor.execute(
    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
    (username, email, password_hash)
)
```
✅ **Status:** Will work with Supabase (columns exist)

2. **User Authentication** (Line 183-185):
```python
cursor.execute(
    "UPDATE users SET last_login = ? WHERE id = ?",
    (datetime.now(), user_id)
)
```
⚠️ **Status:** `last_login` column MISSING in Supabase schema

3. **Questionnaire Save** (Line 229-244):
```python
INSERT INTO questionnaires
(user_id, age, weight, height, sex, activity_level,
 smoking, chronic_conditions, medications, family_history, symptoms)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
```
❌ **Status:** Will FAIL - column names don't match Supabase

4. **CBC Results Save** (Line 284-310):
```python
INSERT INTO cbc_results
(user_id, questionnaire_id, filename, file_format, extraction_success,
 raw_extraction_data, patient_info, wbc, rbc, hgb, ..., risk_score, ...)
VALUES (?, ?, ?, ...)
```
❌ **Status:** Will FAIL - several column mismatches

---

## Impact Assessment

### Critical Issues (App Won't Work):
1. ❌ **Questionnaire table:** Completely different column structure
2. ❌ **CBC results:** Missing columns (filename, raw_extraction_data, cbc_vector, risk_score)
3. ❌ **Users table:** Missing last_login column

### Minor Issues (Can Work Around):
1. ⚠️ **Extra Supabase Auth columns in users:** Ignored by app, no impact
2. ⚠️ **Quebec-specific columns:** App doesn't use them but they don't break anything

---

## Recommended Solutions

### Option 1: Use SQLite Locally (IMMEDIATE - WORKING NOW)
```bash
# App already works with SQLite - no changes needed
cd streamlit_app
streamlit run streamlit_app.py
# Uses data/users.db automatically
```
**Pros:** Works immediately, no schema issues
**Cons:** Not suitable for production deployment, data not persistent across Streamlit Cloud restarts

### Option 2: Fix Supabase Schema (PRODUCTION READY)

**Step 1: Add Missing Columns to Users**
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;
```

**Step 2: Recreate Questionnaires Table**
```sql
DROP TABLE IF EXISTS questionnaires CASCADE;
CREATE TABLE questionnaires (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    age INTEGER,
    weight REAL,
    height REAL,
    sex VARCHAR(20),
    activity_level VARCHAR(50),
    smoking VARCHAR(50),
    chronic_conditions TEXT,
    medications TEXT,
    family_history TEXT,
    symptoms TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Step 3: Add Missing Columns to CBC Results**
```sql
ALTER TABLE cbc_results
  ADD COLUMN IF NOT EXISTS filename VARCHAR(255),
  ADD COLUMN IF NOT EXISTS extraction_success BOOLEAN DEFAULT TRUE,
  ADD COLUMN IF NOT EXISTS raw_extraction_data TEXT,
  ADD COLUMN IF NOT EXISTS patient_info TEXT,
  ADD COLUMN IF NOT EXISTS additional_tests TEXT,
  ADD COLUMN IF NOT EXISTS cbc_vector TEXT,
  ADD COLUMN IF NOT EXISTS risk_score REAL,
  ADD COLUMN IF NOT EXISTS risk_interpretation TEXT,
  ADD COLUMN IF NOT EXISTS processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Rename columns to match app
ALTER TABLE cbc_results RENAME COLUMN cancer_probability TO risk_score;
-- OR keep both and map in app code
```

### Option 3: Update App to Match Supabase Schema (LEAST INVASIVE)

Modify `auth.py` to use Supabase column names:
- Replace questionnaire INSERT to use `q1_`, `q2_`, etc.
- Map `risk_score` → `cancer_probability` in CBC results
- Remove `last_login` update or add column to Supabase

---

## Next Steps - Priority Order

### 🔴 HIGH PRIORITY
1. **Decide on approach:** SQLite (local only) vs Supabase (production)
2. **If Supabase:** Run migration SQL to fix schema mismatches
3. **Test user registration** with corrected schema
4. **Test questionnaire submission** with corrected schema

### 🟡 MEDIUM PRIORITY
5. **Update app database methods** to handle both SQLite and PostgreSQL schemas
6. **Add database version detection** to use correct column names
7. **Document Quebec PDF features** in schema

### 🟢 LOW PRIORITY
8. Clean up Supabase Auth extra columns (if desired)
9. Add database migration scripts for future schema changes
10. Set up automatic backups

---

## Testing Checklist

- [ ] User registration works
- [ ] User login works
- [ ] Questionnaire saves correctly
- [ ] CBC PDF upload and extraction works
- [ ] CBC results save to database
- [ ] User can view their history
- [ ] ML predictions saved correctly
- [ ] Quebec Health Booklet PDFs handled correctly

---

## Files to Review/Modify

1. **`utils/auth.py`** - All database write operations
2. **`utils/database.py`** - Database connection and schema
3. **`streamlit_app.py`** - Main app using database functions
4. **`.streamlit/secrets.toml`** - Already updated ✅
5. **Migration SQL** - Need to create based on chosen approach

---

## Current Working State

✅ **What Works Now:**
- Local SQLite database (fully functional)
- Supabase connection (tested and working)
- PDF extraction (Quebec Health Booklet support)
- ML pipeline (cancer risk prediction)

❌ **What Needs Fixing:**
- Schema alignment between app and Supabase
- Database write operations for production
- Table structure standardization

**Recommendation:** Start with Option 1 (SQLite) for immediate testing, then implement Option 2 (Fix Supabase schema) for production deployment.
