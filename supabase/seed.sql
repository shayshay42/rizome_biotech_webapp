-- Seed data for CBC Analysis Application
-- This creates sample data for testing the application

-- Insert sample users (using bcrypt-style hashes for passwords)
INSERT INTO users (username, password_hash, email) VALUES 
('demo_user', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'demo@example.com'),
('test_quebec', '2cf24dda004d0e1f80f847430c49b3e8e2422b77e14b3a3d6e7c1b6cb5b4cb1f', 'quebec@example.com');

-- Insert sample questionnaire
INSERT INTO questionnaires (
    user_id, 
    q1_family_history, 
    q2_smoking_status, 
    q3_alcohol_consumption,
    q4_previous_cancer, 
    q5_medications, 
    q6_symptoms,
    q7_recent_infections, 
    q8_chronic_conditions, 
    q9_exercise_frequency,
    q10_stress_level
) VALUES 
(1, false, 'never', 'moderate', false, 'None', 'None', false, 'None', 'regular', 'low'),
(2, false, 'never', 'none', false, 'Vitamins', 'Fatigue', false, 'None', 'moderate', 'moderate');

-- Insert sample CBC results (Quebec Health Booklet format)
INSERT INTO cbc_results (
    user_id,
    questionnaire_id, 
    test_date,
    file_format,
    extraction_method,
    -- Core biomarkers (Quebec Health Booklet extraction)
    wbc, hgb, plt, mcv, mono_abs, nlr,
    neut_pct, lymph_pct,
    -- ML prediction results  
    cancer_probability,
    prediction_label,
    risk_level,
    confidence_score,
    -- Quebec-specific metadata
    missing_biomarkers,
    imputed_count,
    imputation_warning
) VALUES 
(
    2, -- test_quebec user
    2, -- second questionnaire 
    '2024-01-23',
    'quebec_health_booklet',
    'quebec_extractor',
    -- CBC values from Quebec PDF
    5.87,  -- WBC
    137.0, -- HGB
    191.0, -- PLT
    88.9,  -- MCV
    0.38,  -- MONO
    2.59,  -- NLR
    63.31, -- NEUT_PCT
    24.44, -- LYMPH_PCT
    -- ML prediction
    0.016, -- 1.6% cancer probability
    'Low Cancer Risk',
    'Very Low',
    0.884, -- 88.4% confidence
    -- Missing data handling
    ARRAY['RDW'], -- RDW was missing
    1, -- 1 biomarker imputed
    'Note: 1 biomarker(s) were missing and estimated using population averages: RDW. This may affect prediction accuracy.'
);

-- Insert sample traditional lab result for comparison
INSERT INTO cbc_results (
    user_id,
    questionnaire_id,
    test_date, 
    file_format,
    extraction_method,
    -- Complete biomarker panel
    wbc, rbc, hgb, hct, mcv, mch, mchc, rdw, plt, mpv,
    neut_abs, lymph_abs, mono_abs, eos_abs, baso_abs,
    neut_pct, lymph_pct, mono_pct, eos_pct, baso_pct,
    nlr, nrbc_abs, nrbc_pct,
    -- ML prediction
    cancer_probability,
    prediction_label, 
    risk_level,
    confidence_score,
    -- No missing data
    missing_biomarkers,
    imputed_count,
    imputation_warning
) VALUES 
(
    1, -- demo_user
    1, -- first questionnaire
    '2024-01-23',
    'traditional_lab',
    'universal_extractor',
    -- Complete CBC panel
    5.87, 4.63, 137.0, 0.41, 88.9, 29.6, 333.0, 13.3, 191.0, 10.1,
    3.72, 1.44, 0.38, 0.32, 0.02,
    63.31, 24.44, 6.42, 5.5, 0.33,
    2.59, 0.0, 0.07,
    -- ML prediction
    0.023, -- 2.3% cancer probability
    'Low Cancer Risk',
    'Very Low', 
    0.956, -- 95.6% confidence (higher due to complete data)
    -- No missing biomarkers
    ARRAY[]::TEXT[],
    0,
    NULL
);

-- Verify the data was inserted
SELECT 
    u.username,
    c.test_date,
    c.file_format,
    c.hgb,
    c.wbc,
    c.cancer_probability * 100 as cancer_risk_percent,
    c.risk_level,
    c.imputed_count,
    array_length(c.missing_biomarkers, 1) as missing_count
FROM cbc_results c 
JOIN users u ON c.user_id = u.id 
ORDER BY c.created_at;