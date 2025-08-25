-- Create tables for CBC Analysis Application
-- This migration creates the necessary tables for storing user data, 
-- questionnaires, and CBC test results with Quebec Health Booklet support

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Questionnaires table
CREATE TABLE IF NOT EXISTS questionnaires (
    id SERIAL PRIMARY KEY,
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
);

-- CBC results table with Quebec Health Booklet support
CREATE TABLE IF NOT EXISTS cbc_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    questionnaire_id INTEGER REFERENCES questionnaires(id),
    test_date DATE,
    file_format VARCHAR(50), -- 'traditional_lab', 'quebec_health_booklet', etc.
    extraction_method VARCHAR(50), -- 'universal_extractor', 'quebec_extractor', etc.
    
    -- Individual CBC biomarkers
    wbc REAL,           -- White Blood Cells (10^9/L)
    rbc REAL,           -- Red Blood Cells (10^12/L)
    hgb REAL,           -- Hemoglobin (g/L)
    hct REAL,           -- Hematocrit (L/L)
    mcv REAL,           -- Mean Corpuscular Volume (fL)
    mch REAL,           -- Mean Corpuscular Hemoglobin (pg)
    mchc REAL,          -- Mean Corpuscular Hemoglobin Concentration (g/L)
    rdw REAL,           -- Red Cell Distribution Width (%)
    plt REAL,           -- Platelets (10^9/L)
    mpv REAL,           -- Mean Platelet Volume (fL)
    
    -- Differential counts (absolute)
    neut_abs REAL,      -- Neutrophils Absolute (10^9/L)
    lymph_abs REAL,     -- Lymphocytes Absolute (10^9/L)
    mono_abs REAL,      -- Monocytes Absolute (10^9/L)
    eos_abs REAL,       -- Eosinophils Absolute (10^9/L)
    baso_abs REAL,      -- Basophils Absolute (10^9/L)
    
    -- Differential counts (percentage)
    neut_pct REAL,      -- Neutrophils Percentage (%)
    lymph_pct REAL,     -- Lymphocytes Percentage (%)
    mono_pct REAL,      -- Monocytes Percentage (%)
    eos_pct REAL,       -- Eosinophils Percentage (%)
    baso_pct REAL,      -- Basophils Percentage (%)
    
    -- Calculated ratios
    nlr REAL,           -- Neutrophil-to-Lymphocyte Ratio
    
    -- Additional fields
    nrbc_abs REAL,      -- Nucleated RBC Absolute (10^9/L)
    nrbc_pct REAL,      -- Nucleated RBC Percentage (%)
    
    -- ML prediction results
    cancer_probability REAL,      -- Cancer probability (0.0-1.0)
    prediction_label VARCHAR(50), -- 'Low Cancer Risk', 'Cancer Risk Detected', etc.
    risk_level VARCHAR(20),       -- 'Very Low', 'Low', 'Moderate', 'High', 'Very High'
    confidence_score REAL,       -- Model confidence (0.0-1.0)
    
    -- Quebec Health Booklet specific metadata
    missing_biomarkers TEXT[],    -- Array of missing biomarker names
    imputed_count INTEGER DEFAULT 0, -- Number of biomarkers imputed
    imputation_warning TEXT,      -- Warning message about imputed values
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_cbc_results_user_id ON cbc_results(user_id);
CREATE INDEX IF NOT EXISTS idx_cbc_results_created_at ON cbc_results(created_at);
CREATE INDEX IF NOT EXISTS idx_cbc_results_file_format ON cbc_results(file_format);

-- Add comments for documentation
COMMENT ON TABLE users IS 'Application users with authentication credentials';
COMMENT ON TABLE questionnaires IS 'Health questionnaires completed by users';
COMMENT ON TABLE cbc_results IS 'CBC test results with Quebec Health Booklet support and ML predictions';

COMMENT ON COLUMN cbc_results.file_format IS 'Source PDF format: traditional_lab, quebec_health_booklet, etc.';
COMMENT ON COLUMN cbc_results.missing_biomarkers IS 'Array of biomarker names that were missing and imputed';
COMMENT ON COLUMN cbc_results.imputed_count IS 'Number of biomarkers estimated using population averages';
COMMENT ON COLUMN cbc_results.imputation_warning IS 'User-friendly warning about prediction accuracy impact';