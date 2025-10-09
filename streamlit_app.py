#!/usr/bin/env python3
"""
Rhizome CBC Analysis Web Application
Main Streamlit application with persistent authentication and storage
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from utils.auth import (
    init_auth, check_authentication, register_user, authenticate_user, 
    logout, get_user_data, save_questionnaire, save_cbc_results,
    request_password_reset, update_password
)
from utils.navigation import setup_navigation
from utils.ml_model import process_cbc_upload, get_biomarker_analysis, get_risk_interpretation

def init_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"

# Page configuration
st.set_page_config(
    page_title="Rhizome CBC Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def show_landing_page():
    """Landing page with logo, sign-in, and sign-up"""
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #2E86AB; font-size: 3rem; margin-bottom: 0;'>🧬 Rhizome</h1>
        <h3 style='color: #666; margin-top: 0;'>Advanced CBC Analysis Platform</h3>
        <p style='font-size: 1.2rem; color: #888; margin: 2rem 0;'>
            Transforming Complete Blood Count data into actionable health insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for sign-in and sign-up
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2, tab3 = st.tabs(["Sign In", "Sign Up", "Forgot Password"])
        
        with tab1:
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
        
        with tab2:
            st.subheader("Join Rhizome")
            with st.form("signup_form"):
                new_username = st.text_input("Choose Username")
                email = st.text_input("Email Address")
                new_password = st.text_input("Create Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                # Password requirements
                st.caption("Password must be at least 6 characters")
                
                signup_button = st.form_submit_button("Create Account", type="primary")
                
                if signup_button:
                    if new_username and email and new_password and confirm_password:
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
        
        with tab3:
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
    
    st.markdown("Please complete the questionnaire and upload your CBC report")
    
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
        
        st.subheader("CBC Report Upload")
        uploaded_file = st.file_uploader(
            "Upload your CBC/Blood Test Report",
            type=["pdf", "jpg", "jpeg", "png"],
            help="Supported formats: PDF, JPG, PNG"
        )
        
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
            
            if uploaded_file:
                # Process the uploaded file with ML model
                with st.spinner("Processing your CBC report with production cancer classifier..."):
                    cbc_data, feature_vector, risk_score, detailed_prediction = process_cbc_upload(uploaded_file, questionnaire_data)
                
                # Get extraction result if available
                extraction_result = cbc_data.get('_extraction_result', {
                    'extraction_metadata': {'format': 'mock', 'success': False},
                    'cbc_data': cbc_data,
                    'patient_info': {},
                    'additional_tests': {}
                })
                
                # Save CBC results to database
                save_cbc_results(
                    st.session_state.user_id,
                    questionnaire_id,
                    extraction_result,
                    feature_vector.tolist(),
                    risk_score,
                    detailed_prediction
                )
                
                # Update session state
                st.session_state.user_data = get_user_data(st.session_state.user_id)
                
                st.success("Assessment and CBC analysis completed successfully!")
                st.balloons()
                time.sleep(2)
                st.rerun()
            else:
                st.warning("Please upload your CBC report to complete the assessment")

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
    risk_score = cbc_results.get('risk_score', 50)
    
    # Try to get detailed prediction results
    try:
        detailed_prediction = json.loads(cbc_results.get('risk_interpretation', '{}'))
        has_detailed_prediction = 'cancer_probability_pct' in detailed_prediction
    except:
        detailed_prediction = {}
        has_detailed_prediction = False
    
    # Get standardized biomarkers from database
    biomarkers = {
        'WBC': cbc_results.get('wbc'),
        'RBC': cbc_results.get('rbc'),
        'Hemoglobin': cbc_results.get('hgb'),
        'Hematocrit': cbc_results.get('hct'),
        'MCV': cbc_results.get('mcv'),
        'Platelets': cbc_results.get('plt'),
        'RDW': cbc_results.get('rdw'),
        'NLR': cbc_results.get('nlr')
    }
    # Filter out None values
    biomarkers = {k: v for k, v in biomarkers.items() if v is not None}
    
    # Display cancer risk prominently
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Cancer Risk Gauge (0-100 scale)
        gauge_title = "Cancer Risk Score (%)"
        gauge_color = "red" if risk_score > 50 else "orange" if risk_score > 20 else "green"
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = risk_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': gauge_title, 'font': {'size': 24}},
            number = {'suffix': "%", 'font': {'size': 40}},
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
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Risk interpretation with detailed prediction if available
    if has_detailed_prediction and 'interpretation' in detailed_prediction:
        risk_info = detailed_prediction['interpretation']
    else:
        risk_info = get_risk_interpretation(risk_score)
    
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem; background-color: {risk_info['color']}20; border-radius: 10px; margin: 1rem 0;'>
        <h3 style='color: {risk_info['color']}; margin: 0;'>{risk_info['level']}</h3>
        <p style='margin: 0.5rem 0 0 0;'>{risk_info['message']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show model information
    if has_detailed_prediction:
        st.info("🎯 **Analysis powered by XGBoost ML model** (99.63% validation AUC) trained on 54,598 patients using 7 key CBC biomarkers")
    else:
        st.info("📊 Analysis based on clinical risk factors and CBC patterns")
    
    # Recommendations
    st.subheader("📋 Recommendations")
    for i, rec in enumerate(risk_info['recommendations'], 1):
        st.write(f"{i}. {rec}")
    
    # Biomarker Analysis
    if biomarkers:
        st.subheader("📊 Biomarker Analysis")
        
        biomarker_analysis = get_biomarker_analysis(biomarkers)
        
        # Create biomarker table
        bio_data = []
        for bio, data in biomarker_analysis.items():
            bio_data.append({
                'Biomarker': bio,
                'Value': f"{data['value']} {data['unit']}",
                'Normal Range': f"{data['range']} {data['unit']}",
                'Status': f"{data['flag']} {data['status']}"
            })
        
        bio_df = pd.DataFrame(bio_data)
        st.dataframe(bio_df, use_container_width=True)
        
        # Biomarker visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Create bar chart of key biomarkers
            key_biomarkers = ['WBC', 'RBC', 'Hemoglobin', 'Platelets']
            if all(bio in biomarkers for bio in key_biomarkers):
                fig_bar = go.Figure(data=[
                    go.Bar(
                        x=key_biomarkers,
                        y=[biomarkers[bio] for bio in key_biomarkers],
                        marker_color=['green' if biomarker_analysis[bio]['status'] == 'Normal' 
                                    else 'red' for bio in key_biomarkers]
                    )
                ])
                fig_bar.update_layout(title="Key Biomarkers", height=400)
                st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # NLR trend (mock data for demonstration)
            if 'NLR' in biomarkers:
                dates = pd.date_range(start='2024-01-01', periods=6, freq='M')
                nlr_values = [2.1, 2.3, 1.9, biomarkers['NLR'], 2.4, 2.0]
                
                fig_trend = px.line(
                    x=dates,
                    y=nlr_values,
                    title="NLR Trend Over Time",
                    labels={'x': 'Date', 'y': 'NLR Ratio'}
                )
                fig_trend.add_hline(y=3.0, line_dash="dash", line_color="red", 
                                  annotation_text="High Risk Threshold")
                
                st.plotly_chart(fig_trend, use_container_width=True)

def show_about_page():
    """About us page with team profiles"""
    st.title("👥 About Rhizome")
    
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h2 style='color: #2E86AB;'>Transforming Healthcare Through Data Science</h2>
        <p style='font-size: 1.2rem; color: #666; max-width: 800px; margin: 0 auto;'>
            Rhizome is pioneering the future of personalized medicine by leveraging advanced machine learning 
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
            "role": "Chief Operational Officer",
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
    else:
        show_dashboard_page()  # Default to dashboard

if __name__ == "__main__":
    main()