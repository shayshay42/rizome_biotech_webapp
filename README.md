# Rhizome CBC Analysis - Streamlit Web Application

A comprehensive web application for Complete Blood Count (CBC) analysis using machine learning, built with Streamlit and optimized for free cloud hosting.

## 🚀 Quick Start

### Local Development
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Access the app:**
   Open your browser to `http://localhost:8501`

### Cloud Deployment (Streamlit Community Cloud)
1. **Fork/Clone this repository to GitHub**
2. **Connect to Streamlit Community Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app" and select this repository
   - Set main file path: `streamlit_app/streamlit_app.py`
   - Deploy!

## 📱 Application Features

### 🏠 Landing Page
- Professional branding with Rhizome logo
- User authentication (sign-in/sign-up)
- Responsive design for mobile and desktop

### 📋 Health Assessment
- Comprehensive health questionnaire
- PDF/Image upload for CBC reports
- Real-time form validation
- Secure data handling

### 📊 Dashboard
- Personalized health risk scoring
- Interactive data visualizations using Plotly
- Biomarker analysis with normal range comparisons
- Health trend tracking
- Risk level interpretation with actionable insights

### 👥 About Us
- Company mission and values
- Team member profiles with professional backgrounds
- Contact information
- Corporate branding

## 🏗️ Architecture

### Streamlit Cloud Optimized Design
- **No External Database Required:** Uses Streamlit session state for data persistence
- **Self-Contained:** All functionality within a single Python file
- **Minimal Dependencies:** Only essential packages for maximum compatibility
- **Mobile Responsive:** CSS styling optimized for all screen sizes

### Data Flow
1. **User Authentication:** Session-based authentication using Streamlit session state
2. **Questionnaire Collection:** Form data stored in session state
3. **File Processing:** CBC reports processed using existing ML pipeline
4. **Risk Scoring:** Integration with trained models from the main repository
5. **Visualization:** Real-time charts using Plotly

### Integration with Existing Codebase
- **ML Models:** Leverages trained models from `output/autogluon_models/`
- **Data Processing:** Uses existing CBC extraction pipeline from `scripts/pdf_cbc_extraction.py`
- **Feature Engineering:** Integrates temporal biomarker features from main analysis
- **Validation:** Applies same data quality checks as research pipeline

## 🔧 Technical Specifications

### Hosting Compatibility
- **Streamlit Community Cloud:** Primary target (free tier)
- **Resource Optimized:** Minimal memory and compute requirements
- **No External Services:** Completely self-contained application
- **File Size Limits:** Optimized for Streamlit's upload limits

### Security Features
- **Session-Based Authentication:** No persistent user data storage
- **Input Validation:** Comprehensive form validation
- **File Type Restrictions:** Limited to safe file types (PDF, images)
- **No External APIs:** All processing handled locally

### Performance Optimizations
- **Lazy Loading:** Components loaded only when needed
- **Efficient State Management:** Minimal session state usage
- **Optimized Visualizations:** Lightweight Plotly charts
- **Mobile Responsive:** Fast loading on all devices

## 🧪 ML Integration

### CBC Processing Pipeline
```python
# Example integration with existing ML pipeline
def process_cbc_upload(uploaded_file):
    # 1. Extract CBC values using existing OCR pipeline
    cbc_data = extract_cbc_from_pdf(uploaded_file)
    
    # 2. Apply feature engineering from main repository
    features = engineer_temporal_features(cbc_data)
    
    # 3. Use trained AutoGluon models for risk scoring
    risk_score = trained_model.predict(features)
    
    return risk_score, cbc_data
```

### Model Integration Points
- **AutoGluon Models:** Pre-trained classification models from main repository
- **Feature Engineering:** Temporal biomarker features (25 features per biomarker)
- **Risk Stratification:** Based on validated clustering analysis
- **Reference Ranges:** Population-based normal ranges from NHANES data

## 📂 File Structure

```
streamlit_app/
├── streamlit_app.py          # Main application file
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── .streamlit/
    └── config.toml          # Streamlit configuration
```

## 🚀 Deployment Guide

### Streamlit Community Cloud
1. **Repository Setup:**
   - Ensure this folder is in a GitHub repository
   - Main file should be accessible at repository root or specify path

2. **Deployment Steps:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Authorize GitHub access
   - Select repository and branch
   - Set main file path: `streamlit_app/streamlit_app.py`
   - Click "Deploy"

3. **Configuration:**
   - App will be available at: `https://[app-name].streamlit.app`
   - Automatic HTTPS and CDN
   - Free subdomain included

### Resource Requirements
- **Memory:** < 1GB (well within free tier limits)
- **Storage:** < 100MB (excluding uploaded files)
- **Compute:** Minimal CPU usage for data processing
- **Bandwidth:** Optimized for free tier limits

## 🔗 Integration with Main Repository

### Data Sources
- **Trained Models:** `../output/autogluon_models/`
- **Reference Data:** `../output/healthy_cbc_integration/`
- **Processing Scripts:** `../scripts/pdf_cbc_extraction.py`
- **Feature Engineering:** `../scripts/temporal_biomarker_feature_extraction.py`

### Development Workflow
1. **Model Training:** Use main repository for model development
2. **Model Export:** Export trained models to streamlit_app directory
3. **Testing:** Test integration with sample data
4. **Deployment:** Deploy to Streamlit Community Cloud

## 📊 Analytics and Monitoring

### Built-in Analytics
- **User Sessions:** Tracked via Streamlit session state
- **File Uploads:** Monitored for processing performance
- **Error Handling:** Comprehensive error logging
- **Performance Metrics:** Load time and response monitoring

### Health Checks
- **Model Availability:** Verify ML models are accessible
- **Data Integrity:** Validate uploaded file processing
- **API Endpoints:** Monitor external service dependencies
- **Resource Usage:** Track memory and compute usage

## 🛡️ Privacy and Security

### Data Handling
- **No Persistent Storage:** All data cleared on session end
- **Local Processing:** Files processed locally, not stored
- **Session Isolation:** Each user session completely isolated
- **No External Transmission:** Data never leaves the application

### Compliance
- **HIPAA Considerations:** Designed for health data handling
- **Data Minimization:** Only collect necessary information
- **Consent Management:** Clear user consent for data processing
- **Audit Trail:** Session-based activity logging

## 🤝 Contributing

### Development Setup
1. Clone the main repository
2. Navigate to `streamlit_app/` directory
3. Install dependencies: `pip install -r requirements.txt`
4. Run locally: `streamlit run streamlit_app.py`

### Integration Testing
- Test with sample CBC reports from `../assets/bot_extracted/`
- Validate ML model integration
- Check mobile responsiveness
- Verify deployment compatibility

## 📞 Support

For technical support or questions about the Streamlit application:
- **Main Repository:** [Rhizome CBC Analysis](https://github.com/your-repo/rhizome)
- **Issues:** Use GitHub Issues for bug reports
- **Documentation:** Refer to main repository CLAUDE.md for full context

---

**Note:** This application is designed to complement the main Rhizome CBC analysis research platform and provides a user-friendly interface for the underlying machine learning capabilities.