-- Check the data types for risk_score and related fields in cbc_results table
SELECT 
    column_name,
    data_type,
    numeric_precision,
    numeric_scale,
    character_maximum_length
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'cbc_results'
  AND column_name IN ('risk_score', 'cancer_probability', 'confidence')
ORDER BY ordinal_position;

-- Also check what values are actually stored
SELECT 
    id,
    risk_score,
    cancer_probability,
    confidence,
    created_at
FROM public.cbc_results
ORDER BY created_at DESC
LIMIT 5;
