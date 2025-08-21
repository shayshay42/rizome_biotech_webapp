#!/usr/bin/env python3
"""
Rhizome CBC Analysis - Streamlit Cloud Compatible Application
Main entry point optimized for Streamlit Community Cloud free hosting
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import hashlib
import time

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Rhizome CBC Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for user management (no external database needed)
def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    if 'questionnaire_data' not in st.session_state:
        st.session_state.questionnaire_data = {}
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Landing"

def hash_password(password):
    """Simple password hashing for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

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
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        
        with tab1:
            st.subheader("Welcome Back")
            with st.form("signin_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                signin_button = st.form_submit_button("Sign In", type="primary")
                
                if signin_button:
                    # Simple demo authentication - in production use proper auth
                    if username and password:
                        # For demo: any non-empty credentials work
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.current_page = "Dashboard"
                        st.rerun()
                    else:
                        st.error("Please enter both username and password")
        
        with tab2:
            st.subheader("Join Rhizome")
            with st.form("signup_form"):
                new_username = st.text_input("Choose Username")
                email = st.text_input("Email Address")
                new_password = st.text_input("Create Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                signup_button = st.form_submit_button("Create Account", type="primary")
                
                if signup_button:
                    if new_username and email and new_password and confirm_password:
                        if new_password == confirm_password:
                            # For demo: automatically sign in after registration
                            st.session_state.authenticated = True
                            st.session_state.username = new_username
                            st.session_state.current_page = "Dashboard"
                            st.success("Account created successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Passwords do not match")
                    else:
                        st.error("Please fill in all fields")

def show_questionnaire_page():
    """Questionnaire and file upload page"""
    st.title("📋 Health Assessment")
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
            # Store questionnaire data in session state
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
            
            st.session_state.questionnaire_data = questionnaire_data
            
            if uploaded_file:
                # Process the uploaded file (mock processing for demo)
                st.session_state.uploaded_file_name = uploaded_file.name
                # In production, here you would:
                # 1. Extract CBC values from PDF/image using OCR
                # 2. Process through your ML model
                # 3. Generate risk score
                
                # Mock ML processing result
                import random
                random.seed(hash(uploaded_file.name) % 1000)
                st.session_state.risk_score = random.randint(15, 85)
                st.session_state.biomarkers = {
                    'WBC': random.uniform(4.0, 11.0),
                    'RBC': random.uniform(4.0, 5.5),
                    'Hemoglobin': random.uniform(12.0, 16.0),
                    'Hematocrit': random.uniform(36.0, 48.0),
                    'MCV': random.uniform(82.0, 98.0),
                    'Platelets': random.uniform(150, 450)
                }
                
                st.success("Assessment submitted successfully!")
                st.session_state.current_page = "Dashboard"
                time.sleep(1)
                st.rerun()
            else:
                st.warning("Please upload your CBC report to complete the assessment")

def show_dashboard_page():
    """User profile page with data visualization panel"""
    st.title(f"🏥 Dashboard - Welcome {st.session_state.username}")
    
    if not st.session_state.questionnaire_data:
        st.info("Complete your health assessment to see personalized insights")
        if st.button("Take Assessment"):
            st.session_state.current_page = "Questionnaire"
            st.rerun()
        return
    
    # Display risk score prominently
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Risk Score Gauge
        risk_score = st.session_state.get('risk_score', 50)
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = risk_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Health Risk Score"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 25], 'color': "lightgreen"},
                    {'range': [25, 50], 'color': "yellow"},
                    {'range': [50, 75], 'color': "orange"},
                    {'range': [75, 100], 'color': "red"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Risk interpretation
    if risk_score < 25:
        risk_level = "Low Risk"
        risk_color = "green"
        risk_message = "Your CBC values indicate good health status."
    elif risk_score < 50:
        risk_level = "Moderate Risk"
        risk_color = "orange"
        risk_message = "Some CBC values may need attention. Consider consulting your physician."
    elif risk_score < 75:
        risk_level = "High Risk"
        risk_color = "red"
        risk_message = "Several CBC values are outside normal ranges. Please consult your physician."
    else:
        risk_level = "Very High Risk"
        risk_color = "darkred"
        risk_message = "CBC values indicate significant abnormalities. Immediate medical attention recommended."
    
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem; background-color: {risk_color}20; border-radius: 10px; margin: 1rem 0;'>
        <h3 style='color: {risk_color}; margin: 0;'>{risk_level}</h3>
        <p style='margin: 0.5rem 0 0 0;'>{risk_message}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Biomarker Analysis
    if 'biomarkers' in st.session_state:
        st.subheader("📊 Biomarker Analysis")
        
        biomarkers = st.session_state.biomarkers
        
        # Create biomarker comparison chart
        normal_ranges = {
            'WBC': (4.0, 11.0),
            'RBC': (4.0, 5.5),
            'Hemoglobin': (12.0, 16.0),
            'Hematocrit': (36.0, 48.0),
            'MCV': (82.0, 98.0),
            'Platelets': (150, 450)
        }
        
        fig_bio = go.Figure()
        
        biomarker_names = list(biomarkers.keys())
        values = list(biomarkers.values())
        
        # Add user values
        fig_bio.add_trace(go.Bar(
            name='Your Values',
            x=biomarker_names,
            y=values,
            marker_color='lightblue'
        ))
        
        # Add normal range indicators
        lower_bounds = [normal_ranges[bio][0] for bio in biomarker_names]
        upper_bounds = [normal_ranges[bio][1] for bio in biomarker_names]
        
        fig_bio.add_trace(go.Scatter(
            name='Normal Range Lower',
            x=biomarker_names,
            y=lower_bounds,
            line=dict(color='green', dash='dash'),
            mode='lines+markers'
        ))
        
        fig_bio.add_trace(go.Scatter(
            name='Normal Range Upper',
            x=biomarker_names,
            y=upper_bounds,
            line=dict(color='red', dash='dash'),
            mode='lines+markers'
        ))
        
        fig_bio.update_layout(
            title="CBC Biomarkers vs Normal Ranges",
            xaxis_title="Biomarkers",
            yaxis_title="Values",
            height=500
        )
        
        st.plotly_chart(fig_bio, use_container_width=True)
        
        # Detailed biomarker table
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Detailed Results")
            bio_df = pd.DataFrame({
                'Biomarker': biomarker_names,
                'Your Value': [f"{v:.1f}" for v in values],
                'Normal Range': [f"{normal_ranges[bio][0]:.1f} - {normal_ranges[bio][1]:.1f}" 
                               for bio in biomarker_names],
                'Status': ['Normal' if normal_ranges[bio][0] <= biomarkers[bio] <= normal_ranges[bio][1] 
                          else 'Abnormal' for bio in biomarker_names]
            })
            st.dataframe(bio_df, use_container_width=True)
        
        with col2:
            st.subheader("📈 Health Trends")
            st.info("Connect multiple test results to see trends over time")
            
            # Mock trend data
            dates = pd.date_range(start='2024-01-01', periods=6, freq='M')
            hemoglobin_trend = [13.2, 13.5, 13.1, biomarkers['Hemoglobin'], 13.8, 14.0]
            
            fig_trend = px.line(
                x=dates,
                y=hemoglobin_trend,
                title="Hemoglobin Trend (Example)",
                labels={'x': 'Date', 'y': 'Hemoglobin (g/dL)'}
            )
            fig_trend.add_hline(y=12.0, line_dash="dash", line_color="red", 
                              annotation_text="Lower Normal")
            fig_trend.add_hline(y=16.0, line_dash="dash", line_color="red", 
                              annotation_text="Upper Normal")
            
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
    
    # Team Profiles
    st.subheader("👨‍💼 Meet Our Team")
    
    # Create team member profiles in a grid
    team_members = [
        {
            "name": "Dr. Sarah Chen",
            "role": "Chief Medical Officer",
            "bio": "Hematologist with 15+ years experience in blood disorders and laboratory medicine. PhD in Clinical Pathology from Johns Hopkins.",
            "avatar": "👩‍⚕️"
        },
        {
            "name": "Alex Rodriguez",
            "role": "Lead Data Scientist",
            "bio": "Machine learning expert specializing in healthcare applications. Former Google Health researcher with expertise in medical imaging and biomarker analysis.",
            "avatar": "👨‍💻"
        },
        {
            "name": "Dr. Michael Thompson",
            "role": "Chief Technology Officer",
            "bio": "Software engineering leader with extensive experience in healthcare technology. Former VP of Engineering at Epic Systems.",
            "avatar": "👨‍💼"
        },
        {
            "name": "Emma Watson",
            "role": "Head of Product",
            "bio": "Product strategist focused on user experience in healthcare. Former product manager at Fitbit, passionate about health democratization.",
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
    
    # Company Values
    st.subheader("💡 Our Values")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔬 Scientific Rigor**
        
        Every algorithm and insight is backed by peer-reviewed research and validated clinical data.
        """)
    
    with col2:
        st.markdown("""
        **🔒 Privacy First**
        
        Your health data is sacred. We employ the highest standards of security and never share personal information.
        """)
    
    with col3:
        st.markdown("""
        **🌍 Accessibility**
        
        Advanced healthcare insights should be available to everyone, regardless of location or economic status.
        """)
    
    # Contact Information
    st.subheader("📞 Get In Touch")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📧 General Inquiries**
        
        info@rhizomehealth.com
        """)
    
    with col2:
        st.markdown("""
        **🩺 Medical Questions**
        
        medical@rhizomehealth.com
        """)
    
    with col3:
        st.markdown("""
        **💻 Technical Support**
        
        support@rhizomehealth.com
        """)

def main():
    """Main application controller"""
    init_session_state()
    
    # Sidebar navigation (only show if authenticated)
    if st.session_state.authenticated:
        with st.sidebar:
            st.markdown(f"### Welcome, {st.session_state.username}! 👋")
            
            # Navigation
            page_options = ["Dashboard", "Questionnaire", "About Us"]
            selected_page = st.radio("Navigate to:", page_options, 
                                    index=page_options.index(st.session_state.current_page) 
                                    if st.session_state.current_page in page_options else 0)
            
            if selected_page != st.session_state.current_page:
                st.session_state.current_page = selected_page
                st.rerun()
            
            st.markdown("---")
            
            # User info
            if st.session_state.questionnaire_data:
                st.markdown("**Assessment Status:** ✅ Complete")
                if 'uploaded_file_name' in st.session_state:
                    st.markdown(f"**Last Report:** {st.session_state.uploaded_file_name}")
            else:
                st.markdown("**Assessment Status:** ⏳ Pending")
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", type="secondary"):
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    # Route to appropriate page
    if not st.session_state.authenticated:
        show_landing_page()
    elif st.session_state.current_page == "Dashboard":
        show_dashboard_page()
    elif st.session_state.current_page == "Questionnaire":
        show_questionnaire_page()
    elif st.session_state.current_page == "About Us":
        show_about_page()
    else:
        show_dashboard_page()  # Default

if __name__ == "__main__":
    main()