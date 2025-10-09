"""
Authentication utilities using Supabase Auth
Handles user registration, login, and session management
"""

import streamlit as st
from .supabase_client import get_supabase
from datetime import datetime
import re

def init_auth():
    """Initialize authentication system and session state"""
    if 'authentication_status' not in st.session_state:
        st.session_state.authentication_status = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}

    # Check for existing Supabase session
    try:
        supabase = get_supabase()
        session = supabase.auth.get_session()

        if session and session.user:
            # Restore session
            st.session_state.authentication_status = True
            st.session_state.user_email = session.user.email
            st.session_state.user_id = session.user.id

            # Get username from user metadata or email
            user_metadata = session.user.user_metadata or {}
            st.session_state.username = user_metadata.get('username', session.user.email.split('@')[0])

    except Exception as e:
        # No valid session, stay logged out
        pass

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def register_user(username, email, password):
    """
    Register new user using Supabase Auth

    Args:
        username: Desired username
        email: User's email address
        password: User's password

    Returns:
        tuple: (success: bool, message: str)
    """

    # Validate input
    if not validate_email(email):
        return False, "Invalid email format"

    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    if len(username) < 3:
        return False, "Username must be at least 3 characters"

    try:
        supabase = get_supabase()

        # Sign up with Supabase Auth
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "username": username
                }
            }
        })

        if response.user:
            return True, "Registration successful! Please check your email to verify your account."
        else:
            return False, "Registration failed. Please try again."

    except Exception as e:
        error_msg = str(e)

        # Handle common errors
        if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
            return False, "Email already registered"
        elif "invalid email" in error_msg.lower():
            return False, "Invalid email address"
        elif "password" in error_msg.lower() and "weak" in error_msg.lower():
            return False, "Password is too weak. Use at least 6 characters with mixed case and numbers."
        else:
            return False, f"Registration failed: {error_msg}"

def authenticate_user(email, password):
    """
    Authenticate user using Supabase Auth

    Args:
        email: User's email or username
        password: User's password

    Returns:
        tuple: (success: bool, user_id: str, email: str)
    """

    try:
        supabase = get_supabase()

        # If email is not valid email format, assume it's a username
        # We'll need to look it up in user metadata
        if not validate_email(email):
            # For now, require email login
            # TODO: Add username lookup if needed
            return False, None, None

        # Sign in with Supabase Auth
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if response.user and response.session:
            user_id = response.user.id
            user_email = response.user.email

            # Store session in Streamlit state
            st.session_state.authentication_status = True
            st.session_state.user_email = user_email
            st.session_state.user_id = user_id

            # Get username from metadata
            user_metadata = response.user.user_metadata or {}
            username = user_metadata.get('username', user_email.split('@')[0])
            st.session_state.username = username

            return True, user_id, user_email
        else:
            return False, None, None

    except Exception as e:
        error_msg = str(e)

        # Handle common errors silently for security
        # Don't reveal whether email exists or not
        return False, None, None

def check_authentication():
    """Check if user is currently authenticated"""
    return st.session_state.get('authentication_status', False)

def logout():
    """Log out current user"""
    try:
        supabase = get_supabase()
        supabase.auth.sign_out()
    except:
        pass

    # Clear session state
    st.session_state.authentication_status = None
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.user_email = None
    st.session_state.user_data = {}

def get_current_user():
    """Get current authenticated user info"""
    try:
        supabase = get_supabase()
        user = supabase.auth.get_user()

        if user:
            return {
                'id': user.id,
                'email': user.email,
                'username': user.user_metadata.get('username', user.email.split('@')[0]),
                'created_at': user.created_at
            }
        return None
    except:
        return None

def get_user_data(user_id):
    """
    Get user's questionnaire and CBC results data

    Args:
        user_id: Supabase user UUID

    Returns:
        dict: User data including questionnaires and CBC results
    """

    try:
        supabase = get_supabase()

        # Get questionnaires
        questionnaire_response = supabase.table('questionnaires').select('*').eq('user_id', user_id).order('submitted_at', desc=True).limit(1).execute()

        has_questionnaire = len(questionnaire_response.data) > 0
        latest_questionnaire = questionnaire_response.data[0] if has_questionnaire else None

        # Get CBC results
        cbc_response = supabase.table('cbc_results').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(1).execute()

        has_cbc_results = len(cbc_response.data) > 0
        latest_cbc = cbc_response.data[0] if has_cbc_results else None

        return {
            'has_questionnaire': has_questionnaire,
            'questionnaire': latest_questionnaire,
            'has_cbc_results': has_cbc_results,
            'cbc_results': latest_cbc
        }

    except Exception as e:
        print(f"Error fetching user data: {e}")
        return {
            'has_questionnaire': False,
            'questionnaire': None,
            'has_cbc_results': False,
            'cbc_results': None
        }

def save_questionnaire(user_id, questionnaire_data):
    """
    Save questionnaire data to Supabase

    Args:
        user_id: Supabase user UUID
        questionnaire_data: Dictionary of questionnaire responses

    Returns:
        int: Questionnaire ID if successful, None otherwise
    """

    try:
        supabase = get_supabase()

        # Prepare data
        data = {
            'user_id': user_id,
            'age': questionnaire_data.get('age'),
            'weight': questionnaire_data.get('weight'),
            'height': questionnaire_data.get('height'),
            'sex': questionnaire_data.get('sex'),
            'activity_level': questionnaire_data.get('activity_level'),
            'smoking': questionnaire_data.get('smoking'),
            'chronic_conditions': ','.join(questionnaire_data.get('chronic_conditions', [])) if isinstance(questionnaire_data.get('chronic_conditions'), list) else questionnaire_data.get('chronic_conditions'),
            'medications': questionnaire_data.get('medications'),
            'family_history': questionnaire_data.get('family_history'),
            'symptoms': questionnaire_data.get('symptoms')
        }

        response = supabase.table('questionnaires').insert(data).execute()

        if response.data:
            return response.data[0]['id']
        return None

    except Exception as e:
        print(f"Error saving questionnaire: {e}")
        return None

def save_cbc_results(user_id, questionnaire_id, extraction_result, cbc_vector, risk_score, detailed_prediction):
    """
    Save CBC results and ML predictions to Supabase

    Args:
        user_id: Supabase user UUID
        questionnaire_id: ID of associated questionnaire
        extraction_result: Dictionary with extraction metadata and CBC data
        cbc_vector: Feature vector array
        risk_score: Overall risk score (0-100)
        detailed_prediction: Dictionary with detailed ML prediction results

    Returns:
        bool: True if successful
    """

    try:
        supabase = get_supabase()

        import json

        # Extract CBC data
        cbc_data = extraction_result.get('cbc_data', {})
        metadata = extraction_result.get('extraction_metadata', {})

        # Helper function to extract value from dict or direct value
        def get_value(item):
            if isinstance(item, dict):
                return item.get('value')
            return item

        # Prepare data
        data = {
            'user_id': user_id,
            'questionnaire_id': questionnaire_id,
            'file_format': metadata.get('format', 'unknown'),
            'extraction_success': metadata.get('success', False),
            'raw_extraction_data': json.dumps(extraction_result),

            # CBC values
            'wbc': get_value(cbc_data.get('WBC')),
            'rbc': get_value(cbc_data.get('RBC')),
            'hgb': get_value(cbc_data.get('HGB') or cbc_data.get('Hemoglobin')),
            'hct': get_value(cbc_data.get('HCT') or cbc_data.get('Hematocrit')),
            'mcv': get_value(cbc_data.get('MCV')),
            'mch': get_value(cbc_data.get('MCH')),
            'mchc': get_value(cbc_data.get('MCHC')),
            'rdw': get_value(cbc_data.get('RDW')),
            'plt': get_value(cbc_data.get('PLT') or cbc_data.get('Platelets')),
            'mpv': get_value(cbc_data.get('MPV')),

            # Differential counts
            'neut_abs': get_value(cbc_data.get('NEUT_ABS')),
            'lymph_abs': get_value(cbc_data.get('LYMPH_ABS')),
            'mono_abs': get_value(cbc_data.get('MONO_ABS') or cbc_data.get('MONO') or cbc_data.get('Monocytes')),
            'eos_abs': get_value(cbc_data.get('EOS_ABS')),
            'baso_abs': get_value(cbc_data.get('BASO_ABS')),

            'neut_pct': get_value(cbc_data.get('NEUT_PCT') or cbc_data.get('Neutrophils')),
            'lymph_pct': get_value(cbc_data.get('LYMPH_PCT') or cbc_data.get('Lymphocytes')),
            'mono_pct': get_value(cbc_data.get('MONO_PCT')),
            'eos_pct': get_value(cbc_data.get('EOS_PCT') or cbc_data.get('Eosinophils')),
            'baso_pct': get_value(cbc_data.get('BASO_PCT') or cbc_data.get('Basophils')),

            # Calculated ratios
            'nlr': get_value(cbc_data.get('NLR')),

            # ML predictions
            'cbc_vector': json.dumps(cbc_vector) if isinstance(cbc_vector, list) else str(cbc_vector),
            'risk_score': risk_score,
            'risk_interpretation': json.dumps(detailed_prediction),

            # Missing/imputed data
            'missing_biomarkers': detailed_prediction.get('missing_features', []),
            'imputed_count': detailed_prediction.get('imputed_count', 0),
            'imputation_warning': detailed_prediction.get('imputation_warning')
        }

        response = supabase.table('cbc_results').insert(data).execute()

        return len(response.data) > 0

    except Exception as e:
        print(f"Error saving CBC results: {e}")
        import traceback
        traceback.print_exc()
        return False
