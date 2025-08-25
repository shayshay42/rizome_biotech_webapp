"""
Database Configuration for CBC Analysis App
Supports both local SQLite (development) and Supabase PostgreSQL (production)
"""

import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
from typing import Dict, List, Optional, Any
import hashlib
from datetime import datetime

class DatabaseManager:
    """Unified database manager supporting SQLite and PostgreSQL"""
    
    def __init__(self):
        self.db_type = self._detect_database_type()
        self.connection = None
        
    def _detect_database_type(self) -> str:
        """Detect whether to use SQLite or PostgreSQL based on environment"""
        # Check if running in Streamlit Cloud or if Supabase credentials are available
        try:
            # Check environment variables first
            if os.getenv('SUPABASE_URL') or os.getenv('DATABASE_URL'):
                return 'postgresql'
            
            # Check Streamlit secrets if available
            if hasattr(st, 'secrets'):
                try:
                    if 'supabase' in st.secrets:
                        return 'postgresql'
                except:
                    # Secrets not accessible, continue to SQLite
                    pass
            
            return 'sqlite'
            
        except Exception:
            # If any error occurs, default to SQLite
            return 'sqlite'
    
    def get_connection(self):
        """Get database connection based on environment"""
        if self.db_type == 'postgresql':
            return self._get_postgresql_connection()
        else:
            return self._get_sqlite_connection()
    
    def _get_sqlite_connection(self):
        """Get SQLite connection (local development)"""
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return sqlite3.connect(db_path)
    
    def _get_postgresql_connection(self):
        """Get PostgreSQL connection (Supabase production)"""
        try:
            # Try Streamlit secrets first
            if hasattr(st, 'secrets') and 'supabase' in st.secrets:
                config = st.secrets['supabase']
                conn_string = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
            else:
                # Fall back to environment variables
                conn_string = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_URL')
                
            return psycopg2.connect(conn_string, cursor_factory=RealDictCursor)
        except Exception as e:
            st.error(f"Failed to connect to PostgreSQL: {e}")
            # Fall back to SQLite
            self.db_type = 'sqlite'
            return self._get_sqlite_connection()
    
    def execute_query(self, query: str, params: tuple = None, fetch: str = None):
        """Execute a query with unified interface for both databases"""
        conn = self.get_connection()
        
        try:
            if self.db_type == 'postgresql':
                cursor = conn.cursor()
            else:
                cursor = conn.cursor()
                
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch == 'all':
                result = cursor.fetchall()
            elif fetch == 'one':
                result = cursor.fetchone()
            else:
                result = None
                
            conn.commit()
            return result
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def create_tables(self):
        """Create all required tables with proper schema for both databases"""
        
        if self.db_type == 'postgresql':
            # PostgreSQL schema
            queries = [
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    email VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS questionnaires (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    q1_family_history BOOLEAN,
                    q2_smoking_status VARCHAR(20),
                    q3_alcohol_consumption VARCHAR(20),
                    q4_previous_cancer BOOLEAN,
                    q5_medications TEXT,
                    q6_symptoms TEXT,
                    q7_recent_infections BOOLEAN,
                    q8_chronic_conditions TEXT,
                    q9_exercise_frequency VARCHAR(20),
                    q10_stress_level VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS cbc_results (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    questionnaire_id INTEGER REFERENCES questionnaires(id),
                    test_date DATE,
                    file_format VARCHAR(50),
                    extraction_method VARCHAR(50),
                    
                    -- Individual CBC biomarkers
                    wbc REAL,
                    rbc REAL,
                    hgb REAL,
                    hct REAL,
                    mcv REAL,
                    mch REAL,
                    mchc REAL,
                    rdw REAL,
                    plt REAL,
                    mpv REAL,
                    
                    -- Differential counts (absolute)
                    neut_abs REAL,
                    lymph_abs REAL,
                    mono_abs REAL,
                    eos_abs REAL,
                    baso_abs REAL,
                    
                    -- Differential counts (percentage)
                    neut_pct REAL,
                    lymph_pct REAL,
                    mono_pct REAL,
                    eos_pct REAL,
                    baso_pct REAL,
                    
                    -- Calculated ratios
                    nlr REAL,
                    
                    -- Additional fields
                    nrbc_abs REAL,
                    nrbc_pct REAL,
                    
                    -- ML prediction results
                    cancer_probability REAL,
                    prediction_label VARCHAR(50),
                    risk_level VARCHAR(20),
                    confidence_score REAL,
                    
                    -- Metadata
                    missing_biomarkers TEXT[],
                    imputed_count INTEGER DEFAULT 0,
                    imputation_warning TEXT,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            ]
        else:
            # SQLite schema (keep existing structure)
            queries = [
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS questionnaires (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    q1_family_history BOOLEAN,
                    q2_smoking_status TEXT,
                    q3_alcohol_consumption TEXT,
                    q4_previous_cancer BOOLEAN,
                    q5_medications TEXT,
                    q6_symptoms TEXT,
                    q7_recent_infections BOOLEAN,
                    q8_chronic_conditions TEXT,
                    q9_exercise_frequency TEXT,
                    q10_stress_level TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS cbc_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    questionnaire_id INTEGER,
                    test_date DATE,
                    file_format TEXT,
                    extraction_method TEXT,
                    
                    -- Individual CBC biomarkers
                    wbc REAL,
                    rbc REAL,
                    hgb REAL,
                    hct REAL,
                    mcv REAL,
                    mch REAL,
                    mchc REAL,
                    rdw REAL,
                    plt REAL,
                    mpv REAL,
                    
                    -- Differential counts (absolute)
                    neut_abs REAL,
                    lymph_abs REAL,
                    mono_abs REAL,
                    eos_abs REAL,
                    baso_abs REAL,
                    
                    -- Differential counts (percentage)
                    neut_pct REAL,
                    lymph_pct REAL,
                    mono_pct REAL,
                    eos_pct REAL,
                    baso_pct REAL,
                    
                    -- Calculated ratios
                    nlr REAL,
                    
                    -- Additional fields
                    nrbc_abs REAL,
                    nrbc_pct REAL,
                    
                    -- ML prediction results
                    cancer_probability REAL,
                    prediction_label TEXT,
                    risk_level TEXT,
                    confidence_score REAL,
                    
                    -- Metadata
                    missing_biomarkers TEXT,
                    imputed_count INTEGER DEFAULT 0,
                    imputation_warning TEXT,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (questionnaire_id) REFERENCES questionnaires (id)
                )
                """
            ]
        
        for query in queries:
            try:
                self.execute_query(query)
                print(f"✅ Table created successfully")
            except Exception as e:
                print(f"❌ Error creating table: {e}")

# Global database manager instance
_db_manager = None

def get_db_manager():
    """Get or create database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

def init_database():
    """Initialize database tables"""
    db = get_db_manager()
    db.create_tables()
    return db.db_type

# User management functions
def hash_password(password: str) -> str:
    """Hash password for secure storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username: str, password: str, email: str = None) -> bool:
    """Create a new user"""
    db = get_db_manager()
    password_hash = hash_password(password)
    
    try:
        db.execute_query(
            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
            (username, password_hash, email)
        )
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user and return user data"""
    db = get_db_manager()
    password_hash = hash_password(password)
    
    try:
        user = db.execute_query(
            "SELECT id, username, email FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash),
            fetch='one'
        )
        
        if user:
            if db.db_type == 'postgresql':
                return dict(user)
            else:
                return {
                    'id': user[0],
                    'username': user[1], 
                    'email': user[2]
                }
        return None
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None

def save_cbc_results(user_id: int, cbc_data: Dict, prediction_results: Dict, 
                     questionnaire_id: int = None, file_format: str = "unknown") -> bool:
    """Save CBC results and prediction to database"""
    db = get_db_manager()
    
    # Prepare missing biomarkers for storage
    missing_biomarkers = prediction_results.get('missing_features', [])
    if db.db_type == 'postgresql':
        missing_biomarkers_str = missing_biomarkers  # PostgreSQL supports arrays
    else:
        missing_biomarkers_str = ','.join(missing_biomarkers) if missing_biomarkers else None
    
    try:
        query = """
        INSERT INTO cbc_results (
            user_id, questionnaire_id, test_date, file_format, extraction_method,
            wbc, rbc, hgb, hct, mcv, mch, mchc, rdw, plt, mpv,
            neut_abs, lymph_abs, mono_abs, eos_abs, baso_abs,
            neut_pct, lymph_pct, mono_pct, eos_pct, baso_pct,
            nlr, nrbc_abs, nrbc_pct,
            cancer_probability, prediction_label, risk_level, confidence_score,
            missing_biomarkers, imputed_count, imputation_warning
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?
        )
        """
        
        params = (
            user_id, questionnaire_id, datetime.now().date(), file_format, "universal_extractor",
            cbc_data.get('WBC', {}).get('value'), cbc_data.get('RBC', {}).get('value'),
            cbc_data.get('HGB', {}).get('value'), cbc_data.get('HCT', {}).get('value'),
            cbc_data.get('MCV', {}).get('value'), cbc_data.get('MCH', {}).get('value'),
            cbc_data.get('MCHC', {}).get('value'), cbc_data.get('RDW', {}).get('value'),
            cbc_data.get('PLT', {}).get('value'), cbc_data.get('MPV', {}).get('value'),
            cbc_data.get('NEUT_ABS', {}).get('value'), cbc_data.get('LYMPH_ABS', {}).get('value'),
            cbc_data.get('MONO_ABS', {}).get('value'), cbc_data.get('EOS_ABS', {}).get('value'),
            cbc_data.get('BASO_ABS', {}).get('value'), cbc_data.get('NEUT_PCT', {}).get('value'),
            cbc_data.get('LYMPH_PCT', {}).get('value'), cbc_data.get('MONO_PCT', {}).get('value'),
            cbc_data.get('EOS_PCT', {}).get('value'), cbc_data.get('BASO_PCT', {}).get('value'),
            cbc_data.get('NLR', {}).get('value'), cbc_data.get('NRBC_ABS', {}).get('value'),
            cbc_data.get('NRBC_PCT', {}).get('value'),
            prediction_results.get('cancer_probability'), prediction_results.get('prediction_label'),
            prediction_results.get('risk_level'), prediction_results.get('confidence'),
            missing_biomarkers_str, prediction_results.get('imputed_count', 0),
            prediction_results.get('imputation_warning')
        )
        
        db.execute_query(query, params)
        return True
        
    except Exception as e:
        print(f"Error saving CBC results: {e}")
        return False

def get_user_cbc_history(user_id: int) -> List[Dict]:
    """Get CBC test history for a user"""
    db = get_db_manager()
    
    try:
        results = db.execute_query(
            """
            SELECT * FROM cbc_results 
            WHERE user_id = ? 
            ORDER BY created_at DESC
            """,
            (user_id,),
            fetch='all'
        )
        
        if db.db_type == 'postgresql':
            return [dict(row) for row in results] if results else []
        else:
            # Convert SQLite rows to dicts
            columns = [
                'id', 'user_id', 'questionnaire_id', 'test_date', 'file_format', 'extraction_method',
                'wbc', 'rbc', 'hgb', 'hct', 'mcv', 'mch', 'mchc', 'rdw', 'plt', 'mpv',
                'neut_abs', 'lymph_abs', 'mono_abs', 'eos_abs', 'baso_abs',
                'neut_pct', 'lymph_pct', 'mono_pct', 'eos_pct', 'baso_pct',
                'nlr', 'nrbc_abs', 'nrbc_pct',
                'cancer_probability', 'prediction_label', 'risk_level', 'confidence_score',
                'missing_biomarkers', 'imputed_count', 'imputation_warning', 'created_at'
            ]
            return [dict(zip(columns, row)) for row in results] if results else []
            
    except Exception as e:
        print(f"Error getting CBC history: {e}")
        return []