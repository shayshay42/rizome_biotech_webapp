-- Add missing columns to cbc_results table for ML model tracking

-- Add model_used column to track which model made the prediction
ALTER TABLE cbc_results 
ADD COLUMN IF NOT EXISTS model_used VARCHAR(255);

-- Add cancer_probability_pct for storing percentage (0-100)
ALTER TABLE cbc_results 
ADD COLUMN IF NOT EXISTS cancer_probability_pct REAL;

-- Add other useful ML prediction columns
ALTER TABLE cbc_results 
ADD COLUMN IF NOT EXISTS cancer_probability DOUBLE PRECISION;

ALTER TABLE cbc_results 
ADD COLUMN IF NOT EXISTS healthy_probability DOUBLE PRECISION;

ALTER TABLE cbc_results 
ADD COLUMN IF NOT EXISTS confidence_score DOUBLE PRECISION;

ALTER TABLE cbc_results 
ADD COLUMN IF NOT EXISTS confidence_pct REAL;

ALTER TABLE cbc_results 
ADD COLUMN IF NOT EXISTS risk_level VARCHAR(50);

ALTER TABLE cbc_results 
ADD COLUMN IF NOT EXISTS risk_color VARCHAR(50);

ALTER TABLE cbc_results 
ADD COLUMN IF NOT EXISTS prediction INTEGER;

ALTER TABLE cbc_results 
ADD COLUMN IF NOT EXISTS prediction_label VARCHAR(100);

ALTER TABLE cbc_results 
ADD COLUMN IF NOT EXISTS model_loaded BOOLEAN;

ALTER TABLE cbc_results 
ADD COLUMN IF NOT EXISTS model_load_error TEXT;

-- Add comments for documentation
COMMENT ON COLUMN cbc_results.model_used IS 'Name of the ML model used for prediction (e.g., CatBoost, XGBoost)';
COMMENT ON COLUMN cbc_results.cancer_probability_pct IS 'Cancer probability as percentage (0-100)';
COMMENT ON COLUMN cbc_results.cancer_probability IS 'Cancer probability as decimal (0-1)';
COMMENT ON COLUMN cbc_results.healthy_probability IS 'Healthy probability as decimal (0-1)';
COMMENT ON COLUMN cbc_results.confidence_score IS 'Model confidence score (0-1)';
COMMENT ON COLUMN cbc_results.risk_level IS 'Risk level category (Very Low, Low, Moderate, High, Very High)';
COMMENT ON COLUMN cbc_results.risk_color IS 'Color for UI display (green, yellow, orange, red)';
