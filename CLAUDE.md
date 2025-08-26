# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Start the web application locally
streamlit run streamlit_app.py

# Test Quebec Health Booklet PDF extraction pipeline
python test_quebec_ml_pipeline.py

# Test complete database system with ML integration
python test_database_system.py
```

### Dependencies
```bash
# Install all required dependencies
pip install -r requirements.txt
```

### Testing Key Components
```bash
# Test universal PDF extraction (supports both formats)
python universal_carnetsante_extractor.py

# Test Quebec-specific PDF extraction
python quebec_health_booklet_extractor.py

# View current database contents
python view_database.py

# Update local database schema
python update_local_database.py
```

## Architecture Overview

### Core Application Structure
- **Main App**: `streamlit_app.py` - Primary Streamlit web interface with authentication
- **Database Layer**: `utils/database.py` - Unified SQLite/PostgreSQL manager with auto-detection
- **ML Pipeline**: `utils/cancer_classifier.py` - Cancer classification with missing value imputation
- **PDF Extraction**: `universal_carnetsante_extractor.py` - Auto-detects and processes both PDF formats

### Key Features
1. **Multi-Format PDF Support**: Handles traditional lab reports (23 biomarkers) and Quebec Health Booklet PDFs (8 biomarkers)
2. **Intelligent Missing Value Handling**: Uses numpy.nan for missing biomarkers with population-based imputation
3. **Environment-Aware Database**: Automatically switches between SQLite (local) and PostgreSQL (production)
4. **ML Confidence Adjustment**: Reduces confidence by 10% per missing biomarker with transparency warnings

### PDF Processing Pipeline
- **Quebec Health Booklets**: Extracts 6/7 required ML biomarkers, with RDW imputation
- **Traditional Lab Reports**: Full 23+ biomarker extraction
- **Auto-Detection**: `universal_carnetsante_extractor.py` identifies PDF format and applies appropriate extraction

### Database Architecture
- **Local Development**: SQLite database (`data/users.db`)
- **Production**: PostgreSQL via Supabase with complete schema in `supabase/migrations/`
- **Auto-Migration**: Environment detection chooses appropriate database automatically
- **Missing Value Tracking**: Stores imputed biomarkers and confidence adjustments

### ML Integration
- **Cancer Classification**: XGBoost model with 7 core biomarkers (HGB, MCV, MONO, NLR, PLT, RDW, WBC)
- **Imputation System**: Population-based missing value estimation
- **Confidence Scoring**: Transparent reduction based on missing data
- **Risk Categories**: Low/Medium/High risk classification with probability scores

## Important Files for Development

### PDF Extraction
- `quebec_health_booklet_extractor.py` - Quebec-specific PDF extraction
- `universal_carnetsante_extractor.py` - Auto-detecting universal extractor
- `utils/pdf_extraction.py` - Base PDF processing utilities

### Database & ML
- `utils/database.py` - Multi-environment database manager
- `utils/cancer_classifier.py` - ML model with imputation support
- `supabase/migrations/001_create_cbc_tables.sql` - Production schema

### Configuration
- `.streamlit/secrets.toml.template` - Database configuration template
- `supabase/config.toml` - Local Supabase development settings

## Current Status
- **Production Ready**: Quebec Health Booklet support with missing value handling
- **Database**: Complete schema supporting both SQLite and PostgreSQL
- **ML Pipeline**: Handles missing biomarkers with confidence adjustment
- **Web Interface**: Needs integration with universal extractor

## Security Notes
- Never commit `.streamlit/secrets.toml` (contains database credentials)
- Local user database `data/users.db` should not be committed with real user data
- Template files are safe to commit