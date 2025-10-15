#!/usr/bin/env python3
"""
Rizome CBC Analysis Web Application
Main Streamlit application with persistent authentication and storage
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time
from typing import Any, Optional

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from utils.auth import (
    init_auth, check_authentication, register_user, authenticate_user, 
    logout, get_user_data, save_questionnaire,
    request_password_reset, update_password, get_current_user,
    delete_user_account_and_data
)
from utils.database import (
    save_cbc_data, get_cbc_data_for_prediction, update_cbc_predictions
)
from utils.navigation import setup_navigation
from utils.ml_model import (
    extract_cbc_from_pdf, get_biomarker_analysis, get_risk_interpretation
)
from utils.cancer_classifier import predict_cancer_risk

_DATAFRAME_SUPPORTS_STRETCH: Optional[bool] = None
_PLOTLY_SUPPORTS_STRETCH: Optional[bool] = None


def _render_dataframe(data, **kwargs):
    """Render a dataframe with stretch width when supported, fallback otherwise."""
    global _DATAFRAME_SUPPORTS_STRETCH
    if _DATAFRAME_SUPPORTS_STRETCH is None:
        try:
            st.dataframe(data, width='stretch', **kwargs)
        except TypeError:
            _DATAFRAME_SUPPORTS_STRETCH = False
            st.dataframe(data, use_container_width=True, **kwargs)
        else:
            _DATAFRAME_SUPPORTS_STRETCH = True
    elif _DATAFRAME_SUPPORTS_STRETCH:
        st.dataframe(data, width='stretch', **kwargs)
    else:
        st.dataframe(data, use_container_width=True, **kwargs)


def _render_plotly_chart(fig, **kwargs):
    """Render plotly charts with stretch width when supported, fallback otherwise."""
    global _PLOTLY_SUPPORTS_STRETCH
    if _PLOTLY_SUPPORTS_STRETCH is None:
        try:
            st.plotly_chart(fig, width='stretch', **kwargs)
        except TypeError:
            _PLOTLY_SUPPORTS_STRETCH = False
            st.plotly_chart(fig, use_container_width=True, **kwargs)
        else:
            _PLOTLY_SUPPORTS_STRETCH = True
    elif _PLOTLY_SUPPORTS_STRETCH:
        st.plotly_chart(fig, width='stretch', **kwargs)
    else:
        st.plotly_chart(fig, use_container_width=True, **kwargs)

def init_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"

# Page configuration
st.set_page_config(
    page_title="Rizome CBC Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def show_landing_page():
    """Landing page with logo, sign-in, and sign-up"""
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #2E86AB; font-size: 3rem; margin-bottom: 0;'>🧬 Rizome Biotech Inc.</h1>
        <h3 style='color: #666; margin-top: 0;'>Advanced CBC Analysis Platform</h3>
        <p style='font-size: 1.2rem; color: #888; margin: 2rem 0;'>
            Transforming Complete Blood Count data into actionable health insights
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("account_deleted_notice"):
        st.success("Your account and associated data were deleted successfully.")
        del st.session_state["account_deleted_notice"]
    
    # Create two columns for sign-in and sign-up
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2, tab3, tab4 = st.tabs(["About Us", "Sign In", "Sign Up", "Forgot Password"])
        
        # ABOUT US TAB - First and most prominent
        with tab1:
            st.markdown("""
            ### 🤖 Our Technology
            
            - **AI Model**: Bagged CatBoost classifier distilled from AutoGluon (CBC biomarkers)
            - **Performance**: ROC-AUC validated via stratified train/test split
            - **Features**: 7 key biomarkers (WBC, NLR, HGB, MCV, PLT, RDW, MONO)
            - **Training Data**: Clinical datasets from Quebec health system
            - **Privacy**: End-to-end encryption, Row Level Security
            
            ### 📈 How It Works
            
            1. **Sign Up** - Create your free account (use the "Sign Up" tab)
            2. **Complete Assessment** - Answer health questionnaire
            3. **Upload or Enter CBC** - Use Carnet de Santé PDF or enter values manually
            4. **Get AI Analysis** - Receive risk assessment in seconds
            5. **Track Over Time** - Upload multiple tests to see trends
            6. **Consult Your Doctor** - Share results with your healthcare provider
            
            ---
            
            <div style='text-align: center; padding: 1rem 0;'>
                <p style='color: #888; font-size: 0.9rem;'>
                    ⚠️ <strong>Medical Disclaimer:</strong> Rizome is a scoring tool, not a diagnostic service.
                    Always consult with qualified healthcare professionals for medical advice, diagnosis, and treatment.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Legal documents
            st.markdown("---")
            st.markdown("### 📋 Legal")
            col_legal1, col_legal2 = st.columns(2)
            with col_legal1:
                if st.button("📄 Terms of Service", width='stretch'):
                    st.switch_page("pages/terms_of_service.py")
            with col_legal2:
                if st.button("🔒 Privacy Policy", width='stretch'):
                    st.switch_page("pages/privacy_policy.py")
            
            # Call to action in About Us tab
            st.markdown("---")
            st.markdown("### 🚀 Ready to Get Started?")
            col_a, col_b = st.columns(2)
            with col_a:
                st.info("👉 Click the **'Sign Up'** tab above to create your free account")
            with col_b:
                st.info("👉 Already have an account? Use the **'Sign In'** tab")
        
        # SIGN IN TAB
        with tab2:
            st.subheader("Welcome Back")
            with st.form("signin_form"):
                username = st.text_input("Email Address")
                password = st.text_input("Password", type="password")
                signin_button = st.form_submit_button("Sign In", type="primary")
                
                if signin_button:
                    if username and password:
                        success, user_id, email, error_msg = authenticate_user(username, password)
                        if success:
                            st.session_state.authentication_status = True
                            st.session_state.username = username
                            st.session_state.user_id = user_id
                            st.session_state.user_data = get_user_data(user_id)
                            st.success("✅ Login successful!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {error_msg}")
                    else:
                        st.error("Please enter both email and password")
            
            # Forgot password link
            st.markdown("---")
            st.caption("Forgot your password? Use the 'Forgot Password' tab above.")
        
        # SIGN UP TAB
        with tab3:
            st.subheader("Join Rizome")
            with st.expander("📄 Read the full legal documents", expanded=False):
                st.markdown("Select a document below to open the full text in a dedicated page.")
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    if st.button("📄 Terms of Service", key="terms_signup", width='stretch'):
                        st.switch_page("pages/terms_of_service.py")
                with col_t2:
                    if st.button("🔒 Privacy Policy", key="privacy_signup", width='stretch'):
                        st.switch_page("pages/privacy_policy.py")

            with st.form("signup_form"):
                new_username = st.text_input("Choose Username")
                email = st.text_input("Email Address")
                new_password = st.text_input("Create Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                # Password requirements
                st.caption("Password must be at least 6 characters")
                
                # Terms and Privacy acceptance
                st.markdown("---")

                st.markdown("""
                **Key Points:**
                - This is a screening tool, NOT a medical diagnosis
                - Always consult healthcare professionals
                - Your data is encrypted and secure
                - You can delete your account anytime
                - No data selling or unauthorized sharing
                """)
                
                accept_terms = st.checkbox(
                    "I have read and agree to the Terms of Service and Privacy Policy",
                    help="You must accept the terms to create an account"
                )
                
                signup_button = st.form_submit_button("Create Account", type="primary")
                
                if signup_button:
                    if not accept_terms:
                        st.error("❌ You must accept the Terms of Service and Privacy Policy to create an account")
                    elif new_username and email and new_password and confirm_password:
                        if new_password == confirm_password:
                            success, message = register_user(new_username, email, new_password)
                            if success:
                                st.success(f"✅ {message}")
                                st.info("💡 Please check your email to verify your account, then sign in.")
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.error("❌ Passwords do not match")
                    else:
                        st.error("❌ Please fill in all fields")
        
        # FORGOT PASSWORD TAB
        with tab4:
            st.subheader("Reset Your Password")
            st.markdown("Enter your email address and we'll send you a link to reset your password.")
            
            with st.form("password_reset_form"):
                reset_email = st.text_input("Email Address")
                reset_button = st.form_submit_button("Send Reset Link", type="primary")
                
                if reset_button:
                    if reset_email:
                        success, message = request_password_reset(reset_email)
                        if success:
                            st.success(f"✅ {message}")
                            st.info("💡 Click the link in the email to reset your password. The link will expire in 1 hour.")
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("❌ Please enter your email address")
            
            st.markdown("---")
            st.caption("Remember your password? Use the 'Sign In' tab above.")

def show_questionnaire_page():
    """Questionnaire and file upload page"""
    st.title("📋 Health Assessment")
    
    # Check if user already has a questionnaire
    if st.session_state.user_data.get('has_questionnaire'):
        st.info("You have already completed the health assessment. You can update it by submitting a new one.")
        
        # Show existing data
        existing_data = st.session_state.user_data.get('questionnaire')
        if existing_data:
            st.subheader("Current Assessment")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Age:** {existing_data.get('age')}")
                st.write(f"**Sex:** {existing_data.get('sex')}")
                st.write(f"**Weight:** {existing_data.get('weight')} kg")
            with col2:
                st.write(f"**Height:** {existing_data.get('height')} cm")
                st.write(f"**Activity Level:** {existing_data.get('activity_level')}")
                st.write(f"**Smoking:** {existing_data.get('smoking')}")
    
    st.markdown("Please complete the questionnaire and provide your CBC values")
    
    # Let users choose entry method outside the form so toggling reruns immediately
    # Default to manual entry (index=0 for first option)
    input_method = st.radio(
        "Choose how to provide your CBC values:",
        ["✍️ Enter 7 Key Values Manually", "📤 Upload Report (PDF/Image)"],
        index=0,
        key="cbc_input_method",
        help="You can manually enter the 7 most important biomarkers or upload a lab report"
    )

    with st.form("health_questionnaire"):
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("Age", min_value=1, max_value=120, value=30)
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0)
            sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        
        with col2:
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
            activity_level = st.selectbox("Activity Level", 
                                        ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
            smoking = st.selectbox("Smoking Status", ["Never", "Former", "Current"])
        
        st.subheader("Medical History")
        col3, col4 = st.columns(2)
        
        with col3:
            chronic_conditions = st.multiselect("Chronic Conditions", 
                                               ["Diabetes", "Hypertension", "Heart Disease", 
                                                "Cancer", "Autoimmune Disease", "None"])
            medications = st.text_area("Current Medications", 
                                     placeholder="List any medications you're currently taking")
        
        with col4:
            family_history = st.multiselect("Family History", 
                                           ["Heart Disease", "Cancer", "Diabetes", 
                                            "Autoimmune Disease", "Blood Disorders", "None"])
            symptoms = st.multiselect("Current Symptoms", 
                                    ["Fatigue", "Weakness", "Bruising", "Bleeding", 
                                     "Frequent Infections", "Weight Loss", "None"])
        
        st.subheader("📋 CBC Report Upload")

        # Instructions for obtaining CBC report
        with st.expander("ℹ️ How to Obtain Your Blood Test Report", expanded=False):
            st.markdown("""
            ### 🇨🇦 For Quebec Residents (Carnet de Santé)
            
            **Option 1: Download from Quebec Health Portal**
            1. Visit [https://carnet.santeqc.ca](https://carnet.santeqc.ca)
            2. Log in with your **Quebec Health Account** (you'll need):
               - Your health insurance number (NAM/RAMQ)
               - Date of birth
               - Email or phone number used during registration
            3. Click on **"My Results"** or **"Mes résultats"**
            4. Find your most recent blood test (CBC/Complete Blood Count)
            5. Click **"Download PDF"** or **"Télécharger le PDF"**
            
            **Option 2: Request from Your Healthcare Provider**
            1. Contact your doctor's office or clinic
            2. Request a copy of your most recent blood test results
            3. They can send it via email or print a copy for you
            
            **Option 3: Visit a CLSC or Lab**
            1. Go to the lab where you had your blood drawn
            2. Request a printed copy of your results
            3. Bring your health insurance card (Carte RAMQ)
            
            ---
            
            ### 🌍 For Other Regions
            
            **United States:**
            - Check your patient portal (MyChart, FollowMyHealth, etc.)
            - Contact your doctor's office or lab directly
            
            **International:**
            - Request from your healthcare provider
            - Check your country's health portal system
            
            ---
            
            ### 📄 What We Need
            
            Your blood test report should include these values:
            - **Complete Blood Count (CBC):** WBC, RBC, Hemoglobin, Hematocrit, Platelets
            - **Differential:** Neutrophils, Lymphocytes, Monocytes, Eosinophils, Basophils
            - **Red Cell Indices:** MCV, MCH, MCHC, RDW
            
            **Accepted formats:** PDF, JPG, PNG
            
            💡 **Tip:** If some values are missing, our system will estimate them using population averages.
            """)
        
        uploaded_file = None
        manual_inputs = None
        manual_test_date = None

        if input_method == "📤 Upload Report (PDF/Image)":
            uploaded_file = st.file_uploader(
                "Upload your CBC/Blood Test Report (PDF, JPG, or PNG)",
                type=["pdf", "jpg", "jpeg", "png"],
                help="Click 'Browse files' to select your blood test report. We support Quebec Carnet de Santé PDFs and standard lab reports."
            )
        else:
            st.markdown("**Enter the 7 key biomarkers from your blood test report:**")
            st.caption("💡 You can find these values on your lab results. If a value is missing, leave it blank and we'll estimate it.")

            col_a, col_b = st.columns(2)
            manual_inputs = {}

            col_a_fields = [
                ("WBC", "WBC (White Blood Cells)", "Normal range: 4.0-11.0 × 10⁹/L", "e.g., 7.2"),
                ("NLR", "NLR (Neutrophil/Lymphocyte Ratio)", "Normal range: 1.0-3.0 (ratio)", "e.g., 2.5"),
                ("HGB", "HGB (Hemoglobin)", "Normal range: 120-170 g/L", "e.g., 145"),
                ("MCV", "MCV (Mean Corpuscular Volume)", "Normal range: 80-100 fL", "e.g., 88")
            ]
            col_b_fields = [
                ("PLT", "PLT (Platelets)", "Normal range: 150-450 × 10⁹/L", "e.g., 250"),
                ("RDW", "RDW (Red Cell Distribution Width)", "Normal range: 11.5-14.5 %", "e.g., 13.2"),
                ("MONO", "MONO (Monocytes)", "Normal range: 0.2-1.0 × 10⁹/L", "e.g., 0.6")
            ]

            with col_a:
                for marker, label, help_text, example in col_a_fields:
                    manual_inputs[marker] = st.text_input(
                        label,
                        value="",
                        placeholder=example,
                        help=help_text,
                        key=f"manual_{marker.lower()}"
                    )

            with col_b:
                for marker, label, help_text, example in col_b_fields:
                    manual_inputs[marker] = st.text_input(
                        label,
                        value="",
                        placeholder=example,
                        help=help_text,
                        key=f"manual_{marker.lower()}"
                    )

                manual_test_date = st.date_input(
                    "Test Date (optional)",
                    value=datetime.today().date(),
                    help="When was this blood test taken?"
                )
                if st.checkbox("I don’t want to save a test date", value=False, key="skip_manual_test_date"):
                    manual_test_date = None
        
        submit_button = st.form_submit_button("Submit Assessment", type="primary")

        if submit_button:
            # Store questionnaire data
            questionnaire_data = {
                'age': age,
                'weight': weight,
                'height': height,
                'sex': sex,
                'activity_level': activity_level,
                'smoking': smoking,
                'chronic_conditions': chronic_conditions,
                'medications': medications,
                'family_history': family_history,
                'symptoms': symptoms,
                'submission_time': datetime.now().isoformat()
            }
            
            # Save to database
            questionnaire_id = save_questionnaire(st.session_state.user_id, questionnaire_data)
            
            manual_cbc_data = None
            if manual_inputs is not None:
                manual_cbc_data = {}
                manual_parse_errors = []
                for marker, raw_value in manual_inputs.items():
                    cleaned_value = (raw_value or "").strip()
                    if cleaned_value:
                        normalized = cleaned_value.replace(',', '.')
                        try:
                            manual_cbc_data[marker] = float(normalized)
                        except ValueError:
                            manual_parse_errors.append(f"{marker} → '{cleaned_value}'")

                if manual_parse_errors:
                    st.error("❌ We couldn't interpret these manual entries as numbers: " + ", ".join(manual_parse_errors))
                    st.stop()

                if not manual_cbc_data:
                    manual_cbc_data = None

            if uploaded_file or manual_cbc_data:
                with st.spinner("Processing your CBC data..."):
                    # STEP 1: Extract/Collect CBC data
                    if uploaded_file:
                        # Extract from uploaded file
                        cbc_data = extract_cbc_from_pdf(uploaded_file)
                        file_format = uploaded_file.name.split('.')[-1].lower()
                        test_date_to_save = None  # Will use current date
                        metadata = {
                            'filename': uploaded_file.name,
                            'extraction_source': 'pdf_upload',
                            'extraction_success': bool(cbc_data),
                            'raw_extraction_data': cbc_data
                        }
                    else:
                        # Use manually entered values
                        cbc_data = {
                            'WBC': manual_cbc_data.get('WBC'),
                            'NLR': manual_cbc_data.get('NLR'),
                            'HGB': manual_cbc_data.get('HGB'),
                            'MCV': manual_cbc_data.get('MCV'),
                            'PLT': manual_cbc_data.get('PLT'),
                            'RDW': manual_cbc_data.get('RDW'),
                            'MONO': manual_cbc_data.get('MONO')
                        }
                        file_format = 'manual_entry'
                        test_date_to_save = manual_test_date  # User-specified date
                        metadata = {
                            'filename': 'manual-entry',
                            'extraction_source': 'manual_input',
                            'extraction_success': True,
                            'raw_extraction_data': cbc_data
                        }
                    
                    # STEP 2: Save CBC data to database FIRST
                    cbc_result_id = save_cbc_data(
                        st.session_state.user_id,
                        questionnaire_id,
                        cbc_data,
                        test_date_to_save,
                        file_format,
                        metadata=metadata
                    )
                    
                    if not cbc_result_id:
                        st.error("❌ Failed to save CBC data to database")
                        st.stop()
                    
                    st.success("✅ CBC data saved to database")
                
                # STEP 3: Read from database and run ML inference
                with st.spinner("Running AI cancer risk analysis..."):
                    # Retrieve data from database
                    cbc_data_from_db = get_cbc_data_for_prediction(cbc_result_id)
                    
                    if not cbc_data_from_db:
                        st.error("❌ Failed to retrieve CBC data for analysis")
                        st.stop()
                    
                    # Run ML prediction on database data
                    detailed_prediction = predict_cancer_risk(cbc_data_from_db)
                    
                    # Debug: show what the model predicted
                    print(f"🔍 DEBUG: Full prediction result = {detailed_prediction}")
                    print(f"🔍 DEBUG: CBC data from DB = {cbc_data_from_db}")
                    print(f"🔍 DEBUG: Predicted cancer_probability_pct = {detailed_prediction.get('cancer_probability_pct')}")
                    print(f"🔍 DEBUG: Model used = {detailed_prediction.get('model_used')}")
                    if 'error' in detailed_prediction:
                        print(f"❌ DEBUG: ERROR in prediction = {detailed_prediction.get('error')}")
                    
                    if 'error' in detailed_prediction:
                        # Fallback to questionnaire-based risk
                        from utils.ml_model import _calculate_questionnaire_risk
                        risk_score = _calculate_questionnaire_risk(questionnaire_data)
                        detailed_prediction = {
                            'cancer_probability_pct': risk_score,
                            'risk_level': 'Unknown',
                            'confidence': 0.5,
                            'prediction_label': 'Fallback'
                        }
                    
                    # STEP 4: Update database with predictions
                    prediction_success = update_cbc_predictions(cbc_result_id, detailed_prediction)
                    
                    if not prediction_success:
                        st.warning("⚠️ CBC data saved but predictions could not be stored")
                
                # Update session state
                st.session_state.user_data = get_user_data(st.session_state.user_id)
                
                st.success("✅ Assessment and CBC analysis completed successfully!")
                st.balloons()
                time.sleep(2)
                st.rerun()
            else:
                st.warning("Please either enter the 7 key values manually OR upload your CBC report to complete the assessment")

def show_dashboard_page():
    """User profile page with data visualization panel"""
    st.title(f"🏥 Dashboard - Welcome {st.session_state.username}")
    
    user_data = st.session_state.user_data
    
    if not user_data.get('has_questionnaire'):
        st.info("Complete your health assessment to see personalized insights")
        if st.button("Take Assessment", type="primary"):
            st.session_state.current_page = "Questionnaire"
            st.rerun()
        return
    
    if not user_data.get('has_cbc_results'):
        st.warning("Upload your CBC report in the questionnaire to see detailed analysis")
        return
    
    # Get CBC results
    cbc_results = user_data.get('cbc_results')

    # Get risk score - try cancer_probability_pct first (already a percentage 0-100)
    # Then fall back to other fields
    risk_score = None
    
    # Try to get detailed prediction results
    try:
        detailed_prediction = json.loads(cbc_results.get('risk_interpretation', '{}'))
        has_detailed_prediction = bool(detailed_prediction)
    except Exception:
        detailed_prediction = {}
        has_detailed_prediction = False
    
    # Priority order: cancer_probability_pct (already %) > cancer_probability (decimal 0-1)
    if cbc_results.get('cancer_probability_pct') is not None:
        risk_score = float(cbc_results.get('cancer_probability_pct'))
    elif cbc_results.get('risk_score') is not None:
        risk_score = float(cbc_results.get('risk_score'))
    elif detailed_prediction.get('cancer_probability_pct') is not None:
        risk_score = float(detailed_prediction.get('cancer_probability_pct'))
    elif cbc_results.get('cancer_probability') is not None:
        # This is a decimal (0-1), convert to percentage
        risk_score = float(cbc_results.get('cancer_probability')) * 100
    elif detailed_prediction.get('cancer_probability') is not None:
        # This is a decimal (0-1), convert to percentage
        risk_score = float(detailed_prediction.get('cancer_probability')) * 100
    else:
        risk_score = 0.0

    risk_score = max(0.0, min(100.0, risk_score))
    
    # Get model information
    model_used = None
    model_load_error = None
    if has_detailed_prediction:
        model_used = detailed_prediction.get('model_used') or cbc_results.get('model_used')
        model_load_error = detailed_prediction.get('model_load_error') or cbc_results.get('model_load_error')
    else:
        model_used = cbc_results.get('model_used')
        model_load_error = cbc_results.get('model_load_error')
    
    # Risk interpretation
    if has_detailed_prediction and 'interpretation' in detailed_prediction:
        risk_info = detailed_prediction['interpretation']
    else:
        risk_info = get_risk_interpretation(risk_score)
    
    # ========== SIMPLIFIED DASHBOARD ==========
    
    # 1. CANCER RISK GAUGE
    st.markdown("### 🎯 Cancer Risk Assessment")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        gauge_color = "red" if risk_score > 50 else "orange" if risk_score > 20 else "green"
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = risk_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Cancer Risk Score", 'font': {'size': 24}},
            number = {'suffix': "%", 'font': {'size': 40}, 'valueformat': '.2f'},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': gauge_color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 10], 'color': "lightgreen"},
                    {'range': [10, 30], 'color': "yellow"},
                    {'range': [30, 60], 'color': "orange"},
                    {'range': [60, 100], 'color': "lightcoral"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80}}))
        fig_gauge.update_layout(height=350, font={'color': "darkblue", 'family': "Arial"})
        _render_plotly_chart(fig_gauge)
    
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem; background-color: {risk_info['color']}20; border-radius: 10px; margin: 1rem 0;'>
        <h3 style='color: {risk_info['color']}; margin: 0;'>{risk_info['level']}</h3>
        <p style='margin: 0.5rem 0 0 0;'>{risk_info['message']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if model_used:
        st.caption(f"🔍 Model: {model_used}")
    else:
        st.caption("ℹ️ Model: Clinical risk heuristics")
    
    if model_load_error:
        st.error(f"⚠️ Model load issue: {model_load_error}")
    
    st.markdown("---")
    
    # 2. COMPREHENSIVE CBC DATA TABLE (Extracted + Model Input)
    st.markdown("### 📊 CBC Data & Model Input")
    st.caption("Shows extracted values from your report and values used by the prediction model")
    
    # Get model features from detailed prediction
    model_features = None
    missing_features = []
    imputed_count = 0
    
    if has_detailed_prediction:
        model_features = detailed_prediction.get('model_features')
        missing_features = detailed_prediction.get('missing_features', [])
        imputed_count = detailed_prediction.get('imputed_count', 0)
    
    # Build comprehensive table data
    feature_metadata = {
        'WBC': ('K/uL', 'White Blood Cells'),
        'HGB': ('g/L', 'Hemoglobin'),
        'MCV': ('fL', 'Mean Corpuscular Volume'),
        'PLT': ('K/uL', 'Platelets'),
        'RDW': ('%', 'Red Cell Distribution Width'),
        'NLR': ('ratio', 'Neutrophil-to-Lymphocyte Ratio'),
        'MONO': ('K/uL', 'Monocytes Absolute')
    }
    
    # Map database fields to feature keys
    db_field_map = {
        'WBC': 'wbc',
        'HGB': 'hgb',
        'MCV': 'mcv',
        'PLT': 'plt',
        'RDW': 'rdw',
        'NLR': 'nlr',
        'MONO': 'mono_abs'
    }
    
    table_data = []
    for feature_key in ['WBC', 'HGB', 'MCV', 'PLT', 'RDW', 'NLR', 'MONO']:
        unit, full_name = feature_metadata[feature_key]
        
        # Get extracted value from database
        db_field = db_field_map[feature_key]
        extracted_value = cbc_results.get(db_field)
        
        # Get model input value
        model_value = model_features.get(feature_key) if model_features else None
        
        # Determine source
        is_imputed = feature_key.upper() in [f.upper() for f in missing_features]
        
        if extracted_value is not None:
            extracted_display = f"{extracted_value:.2f}"
            source = "🔸 Imputed" if is_imputed else "✅ Extracted"
        else:
            extracted_display = "—"
            source = "🔸 Imputed" if is_imputed else "—"
        
        # Model input (what was actually used for prediction)
        if model_value is not None:
            model_display = f"{model_value:.2f}"
        else:
            model_display = "—"
        
        table_data.append({
            'Feature': f"{feature_key}",
            'Name': full_name,
            'Extracted Value': extracted_display,
            'Model Input': model_display,
            'Unit': unit,
            'Source': source
        })
    
    # Create DataFrame and display
    import pandas as pd
    df = pd.DataFrame(table_data)
    
    # Style the dataframe
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Feature": st.column_config.TextColumn("Feature", width="small"),
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Extracted Value": st.column_config.TextColumn("Extracted", width="small"),
            "Model Input": st.column_config.TextColumn("Model Input", width="small"),
            "Unit": st.column_config.TextColumn("Unit", width="small"),
            "Source": st.column_config.TextColumn("Source", width="small")
        }
    )
    
    # Summary info
    if imputed_count > 0:
        st.info(f"ℹ️ {imputed_count} feature(s) were imputed using median population values (marked with 🔸)")
    else:
        st.success("✅ All features were extracted from your report - no imputation needed")
    
    st.markdown("---")
    
    # 4. DATA VERIFICATION SECTION
    with st.expander("🔍 Data Verification Details", expanded=False):
        st.markdown("**Database Record:**")
        st.json({
            'cbc_result_id': cbc_results.get('id'),
            'risk_score': cbc_results.get('risk_score'),
            'cancer_probability_pct': cbc_results.get('cancer_probability_pct'),
            'model_used': cbc_results.get('model_used'),
            'created_at': str(cbc_results.get('created_at'))
        })
        
        if has_detailed_prediction:
            st.markdown("**Latest Prediction Result:**")
            st.json({
                'cancer_probability_pct': detailed_prediction.get('cancer_probability_pct'),
                'model_used': detailed_prediction.get('model_used'),
                'missing_features': detailed_prediction.get('missing_features', []),
                'imputed_count': detailed_prediction.get('imputed_count', 0)
            })

def show_about_page():
    """About us page with team profiles"""
    st.title("👥 About Rizome")
    
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h2 style='color: #2E86AB;'>Transforming Healthcare Through Data Science</h2>
        <p style='font-size: 1.2rem; color: #666; max-width: 800px; margin: 0 auto;'>
            Rizome is pioneering the future of personalized medicine by leveraging advanced machine learning 
            to transform routine blood tests into actionable health insights. Our mission is to democratize 
            access to sophisticated health analytics and empower individuals to take control of their health journey.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mission Statement
    st.subheader("🎯 Our Mission")
    st.markdown("""
    To bridge the gap between complex medical data and patient understanding by providing 
    intelligent, accessible, and actionable health insights derived from Complete Blood Count analysis.
    """)
    
    # Team Profiles (same as before)
    st.subheader("👨‍💼 Meet Our Team")
    
    team_members = [
        {
            "name": "Dr Jonathan Cools-Lartigue",
            "role": "Chief Executive Officer",
            "bio": "blurb",
            "avatar": "👩‍⚕️"
        },
        {
            "name": "Shayan Hajhashemi",
            "role": "Chief Technology Officer",
            "bio": "blurb",
            "avatar": "👨‍💻"
        },
        {
            "name": "Benjamin Gordon",
            "role": "Chief Scientific Officer",
            "bio": "blurb",
            "avatar": "👨‍💼"
        },
        {
            "name": "Dr Kim Ma",
            "role": "Chief Medical Officer",
            "bio": "blurb",
            "avatar": "👩‍💼"
        }
    ]
    
    cols = st.columns(2)
    for i, member in enumerate(team_members):
        with cols[i % 2]:
            st.markdown(f"""
            <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; text-align: center;'>
                <div style='font-size: 4rem; margin-bottom: 1rem;'>{member['avatar']}</div>
                <h4 style='color: #2E86AB; margin: 0.5rem 0;'>{member['name']}</h4>
                <h5 style='color: #666; margin: 0.5rem 0;'>{member['role']}</h5>
                <p style='color: #888; font-size: 0.9rem; line-height: 1.4;'>{member['bio']}</p>
            </div>
            """, unsafe_allow_html=True)


def show_settings_page():
    """Account settings and deletion controls"""
    st.title("⚙️ Account Settings")

    user_info = get_current_user() or {}

    st.subheader("Account Details")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Email", user_info.get('email', st.session_state.get('user_email', 'Unknown')))
        st.metric("Username", user_info.get('username', st.session_state.get('username', 'Unknown')))
    with col2:
        created_at = user_info.get('created_at')
        if created_at:
            try:
                created_display = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%B %d, %Y')
            except Exception:
                created_display = created_at
        else:
            created_display = "Unavailable"
        st.metric("Member Since", created_display)

    st.markdown("---")

    with st.expander("🗑️ Delete account and data", expanded=False):
        st.warning("""
        This will permanently delete your questionnaires, CBC results, predictions, and account access. 
        The action cannot be undone.
        """)

        with st.form("delete_account_form"):
            st.markdown("Before continuing, confirm that you understand the consequences of deleting your account.")
            confirm_phrase = st.text_input("Type DELETE to confirm", placeholder="DELETE")
            acknowledge = st.checkbox("I understand this action is permanent and cannot be undone.")
            delete_submit = st.form_submit_button("Delete my account", type="primary")

        if delete_submit:
            if confirm_phrase.strip().upper() != "DELETE":
                st.error("You must type DELETE exactly to confirm.")
            elif not acknowledge:
                st.error("You must acknowledge the permanence of this action.")
            else:
                user_id = st.session_state.get('user_id')
                if not user_id:
                    st.error("Could not determine your user ID. Please sign out and sign back in before deleting your account.")
                    return

                with st.spinner("Deleting your account and associated data..."):
                    success, diagnostics = delete_user_account_and_data(user_id)

                if success:
                    st.success("Your account and data have been permanently removed.")
                    logout()
                    st.session_state["account_deleted_notice"] = True
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("We removed some data, but parts of the deletion process reported issues.")
                    if diagnostics.get("errors"):
                        for item in diagnostics["errors"]:
                            st.warning(item)
                        if any("service role key" in item.lower() for item in diagnostics["errors"]):
                            st.info("Add your Supabase service role key to Streamlit secrets or environment variables to allow automated account removal.")
                    st.info("Please try again later or contact support if the problem persists.")

def show_password_update_page():
    """Page for updating password after clicking reset link"""
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #2E86AB; font-size: 3rem; margin-bottom: 0;'>🔑 Reset Password</h1>
        <p style='font-size: 1.2rem; color: #888; margin: 2rem 0;'>
            Enter your new password below
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("update_password_form"):
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            st.caption("Password must be at least 6 characters")
            
            update_button = st.form_submit_button("Update Password", type="primary")
            
            if update_button:
                if new_password and confirm_password:
                    if new_password == confirm_password:
                        success, message = update_password(new_password)
                        if success:
                            st.success(f"✅ {message}")
                            st.info("💡 You can now sign in with your new password.")
                            time.sleep(2)
                            # Clear query params and redirect to landing
                            st.query_params.clear()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("❌ Passwords do not match")
                else:
                    st.error("❌ Please fill in both password fields")

def main():
    """Main application entry point"""
    
    # Initialize session state and authentication system
    init_session_state()
    init_auth()
    
    # Check for password reset flow
    query_params = st.query_params
    if 'type' in query_params and query_params['type'] == 'recovery':
        # User clicked password reset link
        show_password_update_page()
        return
    
    # Check if user is authenticated
    if not check_authentication():
        show_landing_page()
        return
    
    # Setup navigation for authenticated users
    selected_page = setup_navigation()
    
    # Update current page if navigation changed
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()
    
    # Route to appropriate page based on current_page
    if st.session_state.current_page == "Dashboard":
        show_dashboard_page()
    elif st.session_state.current_page == "Questionnaire":
        show_questionnaire_page()
    elif st.session_state.current_page == "About Us":
        show_about_page()
    elif st.session_state.current_page == "Settings":
        show_settings_page()
    else:
        show_dashboard_page()  # Default to dashboard

if __name__ == "__main__":
    main()