-- SUPABASE DATABASE RESET SCRIPT
-- Run this in Supabase SQL Editor to clean and rebuild tables
-- WARNING: This will delete ALL user data!

-- Drop all existing tables
DROP TABLE IF EXISTS cbc_results CASCADE;
DROP TABLE IF EXISTS questionnaires CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Create questionnaires table
CREATE TABLE questionnaires (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
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

-- Create CBC results table
CREATE TABLE cbc_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    questionnaire_id INTEGER REFERENCES questionnaires(id) ON DELETE SET NULL,

    -- File metadata
    filename VARCHAR(255),
    file_format VARCHAR(50),
    extraction_success BOOLEAN DEFAULT TRUE,
    raw_extraction_data TEXT,
    patient_info TEXT,

    -- Complete Blood Count - Main Parameters
    wbc REAL,          -- White Blood Cells (10^9/L)
    rbc REAL,          -- Red Blood Cells (10^12/L)
    hgb REAL,          -- Hemoglobin (g/L)
    hct REAL,          -- Hematocrit (L)
    mcv REAL,          -- Mean Corpuscular Volume (fL)
    mch REAL,          -- Mean Corpuscular Hemoglobin (pg)
    mchc REAL,         -- Mean Corpuscular Hemoglobin Concentration (g/L)
    rdw REAL,          -- Red Cell Distribution Width (%)
    plt REAL,          -- Platelets (10^9/L)
    mpv REAL,          -- Mean Platelet Volume (fL)

    -- Differential Counts (Absolute)
    neut_abs REAL,     -- Neutrophils Absolute (10^9/L)
    lymph_abs REAL,    -- Lymphocytes Absolute (10^9/L)
    mono_abs REAL,     -- Monocytes Absolute (10^9/L)
    eos_abs REAL,      -- Eosinophils Absolute (10^9/L)
    baso_abs REAL,     -- Basophils Absolute (10^9/L)

    -- Differential Counts (Percentage)
    neut_pct REAL,     -- Neutrophils Percentage (%)
    lymph_pct REAL,    -- Lymphocytes Percentage (%)
    mono_pct REAL,     -- Monocytes Percentage (%)
    eos_pct REAL,      -- Eosinophils Percentage (%)
    baso_pct REAL,     -- Basophils Percentage (%)

    -- Calculated Ratios
    nlr REAL,          -- Neutrophil-to-Lymphocyte Ratio

    -- Additional fields
    additional_tests TEXT,

    -- ML Prediction Results
    cbc_vector TEXT,           -- Feature vector as JSON
    risk_score REAL,           -- Overall risk score (0-100)
    risk_interpretation TEXT,  -- JSON with detailed prediction results

    -- Missing/Imputed Data Tracking
    missing_biomarkers TEXT[], -- Array of missing biomarker names
    imputed_count INTEGER DEFAULT 0,
    imputation_warning TEXT,

    -- Timestamps
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_questionnaires_user_id ON questionnaires(user_id);
CREATE INDEX idx_cbc_results_user_id ON cbc_results(user_id);
CREATE INDEX idx_cbc_results_questionnaire_id ON cbc_results(questionnaire_id);
CREATE INDEX idx_cbc_results_created_at ON cbc_results(created_at);

-- Grant permissions (if needed)
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE questionnaires ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE cbc_results ENABLE ROW LEVEL SECURITY;

-- Verify tables created
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_name IN ('users', 'questionnaires', 'cbc_results')
ORDER BY table_name, ordinal_position;
