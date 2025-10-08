"""
Authentication utilities for Rhizome CBC Analysis App
Handles user registration, login, and session management with persistent storage
"""

import streamlit as st
import bcrypt
import sqlite3
import re
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

def init_auth():
    """Initialize authentication system and database"""
    if 'authentication_status' not in st.session_state:
        st.session_state.authentication_status = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    
    # Initialize user database
    init_user_db()

def init_user_db():
    """Initialize SQLite database for user management"""
    db_path = Path(__file__).parent.parent / "data" / "users.db"
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Questionnaires table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questionnaires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            age INTEGER,
            weight REAL,
            height REAL,
            sex TEXT,
            activity_level TEXT,
            smoking TEXT,
            chronic_conditions TEXT,
            medications TEXT,
            family_history TEXT,
            symptoms TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # CBC Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cbc_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            questionnaire_id INTEGER,
            filename TEXT,
            file_format TEXT,  -- PDF format (carnetsante, etc.)
            extraction_success BOOLEAN DEFAULT TRUE,
            
            -- Raw extraction data
            raw_extraction_data TEXT,  -- Full JSON of extraction result
            patient_info TEXT,  -- JSON of patient demographics from PDF
            
            -- Standardized CBC values (main biomarkers)
            wbc REAL,  -- White Blood Cells (10^9/L)
            rbc REAL,  -- Red Blood Cells (10^12/L)
            hgb REAL,  -- Hemoglobin (g/L)
            hct REAL,  -- Hematocrit (L)
            mcv REAL,  -- Mean Corpuscular Volume (fL)
            mch REAL,  -- Mean Corpuscular Hemoglobin (pg)
            mchc REAL, -- Mean Corpuscular Hemoglobin Concentration (g/L)
            rdw REAL,  -- Red Cell Distribution Width (%)
            plt REAL,  -- Platelets (10^9/L)
            mpv REAL,  -- Mean Platelet Volume (fL)
            
            -- Differential counts
            neut_abs REAL,  -- Neutrophils Absolute (10^9/L)
            neut_pct REAL,  -- Neutrophils Percentage (%)
            lymph_abs REAL, -- Lymphocytes Absolute (10^9/L)
            lymph_pct REAL, -- Lymphocytes Percentage (%)
            mono_abs REAL,  -- Monocytes Absolute (10^9/L)
            mono_pct REAL,  -- Monocytes Percentage (%)
            eos_abs REAL,   -- Eosinophils Absolute (10^9/L)
            eos_pct REAL,   -- Eosinophils Percentage (%)
            baso_abs REAL,  -- Basophils Absolute (10^9/L)
            baso_pct REAL,  -- Basophils Percentage (%)
            
            -- Calculated ratios
            nlr REAL,  -- Neutrophil to Lymphocyte Ratio
            
            -- Additional tests (when available)
            additional_tests TEXT,  -- JSON of other lab values
            
            -- ML processing results
            cbc_vector TEXT,  -- JSON string of 175 engineered features
            risk_score REAL,
            risk_interpretation TEXT,  -- JSON of risk analysis
            
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (questionnaire_id) REFERENCES questionnaires (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    """Verify password against hash"""
    # Handle both str (PostgreSQL) and bytes (SQLite) for hashed password
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def register_user(username, email, password):
    """Register new user"""
    if not validate_email(email):
        return False, "Invalid email format"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    from .database import DatabaseManager
    
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Use appropriate placeholder syntax based on database type
    placeholder = "%s" if db.db_type == 'postgresql' else "?"
    
    try:
        password_hash = hash_password(password)
        cursor.execute(
            f"INSERT INTO users (username, email, password_hash) VALUES ({placeholder}, {placeholder}, {placeholder})",
            (username, email, password_hash)
        )
        conn.commit()
        
        if db.db_type == 'postgresql':
            cursor.execute("SELECT lastval()")
            result = cursor.fetchone()
            user_id = result['lastval'] if isinstance(result, dict) else result[0]
        else:
            user_id = cursor.lastrowid
            
        conn.close()
        return True, "Registration successful! Please sign in with your credentials."
    except Exception as e:
        conn.close()
        return False, "Username or email already exists"

def authenticate_user(username, password):
    """Authenticate user login"""
    from .database import DatabaseManager
    
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Use appropriate placeholder syntax based on database type
    placeholder = "%s" if db.db_type == 'postgresql' else "?"
    
    cursor.execute(
        f"SELECT id, password_hash, email FROM users WHERE username = {placeholder} OR email = {placeholder}",
        (username, username)
    )
    result = cursor.fetchone()

    if result:
        # Handle both dict (PostgreSQL with RealDictCursor) and tuple (SQLite) results
        if isinstance(result, dict):
            password_hash = result['password_hash']
            user_id = result['id']
            email = result['email']
        else:
            password_hash = result[1]
            user_id = result[0]
            email = result[2]

        if not verify_password(password, password_hash):
            conn.close()
            return False, None, None
        
        # Try to update last login (ignore if column doesn't exist)
        try:
            cursor.execute(
                f"UPDATE users SET last_login = {placeholder} WHERE id = {placeholder}",
                (datetime.now(), user_id)
            )
            conn.commit()
        except Exception:
            # Column might not exist, continue without error
            pass
            
        conn.close()
        return True, user_id, email
    
    conn.close()
    return False, None, None

def get_user_data(user_id):
    """Get user's questionnaire and CBC data"""
    from .database import DatabaseManager
    
    db = DatabaseManager()
    conn = db.get_connection()
    
    try:
        # Get latest questionnaire
        questionnaire_df = pd.read_sql_query(
            "SELECT * FROM questionnaires WHERE user_id = %s ORDER BY created_at DESC LIMIT 1" if db.db_type == 'postgresql' else "SELECT * FROM questionnaires WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            conn, params=(user_id,)
        )
        
        # Get latest CBC results
        cbc_df = pd.read_sql_query(
            "SELECT * FROM cbc_results WHERE user_id = %s ORDER BY created_at DESC LIMIT 1" if db.db_type == 'postgresql' else "SELECT * FROM cbc_results WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            conn, params=(user_id,)
        )
    finally:
        conn.close()
    
    user_data = {
        'has_questionnaire': len(questionnaire_df) > 0,
        'has_cbc_results': len(cbc_df) > 0,
        'questionnaire': questionnaire_df.to_dict('records')[0] if len(questionnaire_df) > 0 else None,
        'cbc_results': cbc_df.to_dict('records')[0] if len(cbc_df) > 0 else None
    }
    
    return user_data

def save_questionnaire(user_id, questionnaire_data):
    """Save questionnaire data to database"""
    from .database import DatabaseManager
    
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO questionnaires 
        (user_id, age, weight, height, sex, activity_level, smoking, 
         chronic_conditions, medications, family_history, symptoms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        questionnaire_data.get('age'),
        questionnaire_data.get('weight'),
        questionnaire_data.get('height'),
        questionnaire_data.get('sex'),
        questionnaire_data.get('activity_level'),
        questionnaire_data.get('smoking'),
        json.dumps(questionnaire_data.get('chronic_conditions', [])),
        questionnaire_data.get('medications'),
        json.dumps(questionnaire_data.get('family_history', [])),
        json.dumps(questionnaire_data.get('symptoms', []))
    ))
    
    questionnaire_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return questionnaire_id

def save_cbc_results(user_id, questionnaire_id, extraction_result, cbc_vector, risk_score, risk_interpretation):
    """Save CBC analysis results to database with enhanced schema"""
    from .database import DatabaseManager
    
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Extract standardized values from cbc_data
    cbc_data = extraction_result.get('cbc_data', {})
    standardized_values = {}
    
    # Map standardized CBC values
    field_mapping = {
        'WBC': 'wbc', 'RBC': 'rbc', 'HGB': 'hgb', 'HCT': 'hct',
        'MCV': 'mcv', 'MCH': 'mch', 'MCHC': 'mchc', 'RDW': 'rdw',
        'PLT': 'plt', 'MPV': 'mpv', 'NEUT_ABS': 'neut_abs', 'NEUT_PCT': 'neut_pct',
        'LYMPH_ABS': 'lymph_abs', 'LYMPH_PCT': 'lymph_pct', 'MONO_ABS': 'mono_abs',
        'MONO_PCT': 'mono_pct', 'EOS_ABS': 'eos_abs', 'EOS_PCT': 'eos_pct',
        'BASO_ABS': 'baso_abs', 'BASO_PCT': 'baso_pct', 'NLR': 'nlr'
    }
    
    for std_name, db_field in field_mapping.items():
        if std_name in cbc_data:
            # Handle both dict format {'value': x} and direct float values
            if isinstance(cbc_data[std_name], dict):
                standardized_values[db_field] = cbc_data[std_name].get('value')
            else:
                standardized_values[db_field] = cbc_data[std_name]
        else:
            standardized_values[db_field] = None
    
    cursor.execute('''
        INSERT INTO cbc_results 
        (user_id, questionnaire_id, filename, file_format, extraction_success,
         raw_extraction_data, patient_info, additional_tests,
         wbc, rbc, hgb, hct, mcv, mch, mchc, rdw, plt, mpv,
         neut_abs, neut_pct, lymph_abs, lymph_pct, mono_abs, mono_pct,
         eos_abs, eos_pct, baso_abs, baso_pct, nlr,
         cbc_vector, risk_score, risk_interpretation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        questionnaire_id,
        extraction_result.get('extraction_metadata', {}).get('source_file', ''),
        extraction_result.get('extraction_metadata', {}).get('format', 'unknown'),
        extraction_result.get('extraction_metadata', {}).get('success', False),
        json.dumps(extraction_result),
        json.dumps(extraction_result.get('patient_info', {})),
        json.dumps(extraction_result.get('additional_tests', {})),
        standardized_values['wbc'], standardized_values['rbc'], standardized_values['hgb'],
        standardized_values['hct'], standardized_values['mcv'], standardized_values['mch'],
        standardized_values['mchc'], standardized_values['rdw'], standardized_values['plt'],
        standardized_values['mpv'], standardized_values['neut_abs'], standardized_values['neut_pct'],
        standardized_values['lymph_abs'], standardized_values['lymph_pct'], standardized_values['mono_abs'],
        standardized_values['mono_pct'], standardized_values['eos_abs'], standardized_values['eos_pct'],
        standardized_values['baso_abs'], standardized_values['baso_pct'], standardized_values['nlr'],
        json.dumps(cbc_vector),
        risk_score,
        json.dumps(risk_interpretation)
    ))
    
    conn.commit()
    conn.close()

def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.authentication_status == True

def logout():
    """Logout user and clear session"""
    st.session_state.authentication_status = None
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.user_data = {}
    st.rerun()