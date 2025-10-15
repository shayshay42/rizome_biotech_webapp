-- Check and fix data types for cbc_results table in Supabase
-- This ensures decimal precision is preserved

-- First, check current data types
SELECT 
    column_name,
    data_type,
    numeric_precision,
    numeric_scale
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'cbc_results'
  AND column_name IN ('risk_score', 'cancer_probability', 'cancer_probability_pct', 'confidence_score', 'confidence_pct')
ORDER BY ordinal_position;

-- If any are INTEGER, convert them to NUMERIC or DOUBLE PRECISION
-- ALTER TABLE commands to fix data types (run only if needed)

-- Uncomment these lines if the columns are showing as INTEGER:
-- ALTER TABLE public.cbc_results ALTER COLUMN risk_score TYPE DOUBLE PRECISION;
-- ALTER TABLE public.cbc_results ALTER COLUMN cancer_probability TYPE DOUBLE PRECISION;
-- ALTER TABLE public.cbc_results ALTER COLUMN cancer_probability_pct TYPE DOUBLE PRECISION;
-- ALTER TABLE public.cbc_results ALTER COLUMN confidence_score TYPE DOUBLE PRECISION;
-- ALTER TABLE public.cbc_results ALTER COLUMN confidence_pct TYPE DOUBLE PRECISION;

-- Check actual data stored
SELECT 
    id,
    risk_score,
    cancer_probability,
    cancer_probability_pct,
    confidence_score,
    model_used,
    created_at
FROM public.cbc_results
ORDER BY created_at DESC
LIMIT 5;
