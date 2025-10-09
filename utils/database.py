"""
Database Configuration for CBC Analysis App
Supports both local SQLite (development) and Supabase PostgreSQL (production)
"""

import os
import json
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
from typing import Dict, List, Optional, Any
import hashlib
from datetime import datetime, date

from .supabase_client import get_supabase, get_supabase_admin

class DatabaseManager:
    """Unified database manager supporting SQLite and PostgreSQL"""
    
    def __init__(self):
        self.db_type = self._detect_database_type()
        self.connection = None
        self._table_columns_cache: Dict[str, List[str]] = {}
        
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

    def get_table_columns(self, table_name: str) -> List[str]:
        """Return list of column names for a table, caching results per session."""
        if table_name in self._table_columns_cache:
            return self._table_columns_cache[table_name]

        conn = self.get_connection()
        columns: List[str] = []
        try:
            cursor = conn.cursor()
            if self.db_type == 'postgresql':
                cursor.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = %s
                    ORDER BY ordinal_position
                    """,
                    (table_name,)
                )
                rows = cursor.fetchall()
                for row in rows:
                    if isinstance(row, dict):
                        columns.append(row.get('column_name'))
                    else:
                        columns.append(row[0])
            else:
                cursor.execute(f"PRAGMA table_info({table_name})")
                rows = cursor.fetchall()
                for row in rows:
                    if isinstance(row, dict):
                        col_name = row.get('name')
                    else:
                        col_name = row[1] if len(row) > 1 else None
                    if col_name:
                        columns.append(col_name)
        finally:
            conn.close()

        self._table_columns_cache[table_name] = columns
        return columns

    def has_column(self, table_name: str, column_name: str) -> bool:
        """Check if a specific column exists on a table."""
        return column_name in self.get_table_columns(table_name)

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

def save_cbc_data(user_id: Any, questionnaire_id: Any, cbc_data: Dict,
                  test_date=None, file_format: str = "unknown",
                  metadata: Optional[Dict[str, Any]] = None) -> int:
    """
    Save raw CBC data to database (without predictions)
    Returns: cbc_result_id for later prediction updates
    """
    db = get_db_manager()
    metadata = metadata or {}
    
    try:
        # Use provided test_date or current date
        if test_date is None:
            test_date = datetime.now().date()
        elif hasattr(test_date, 'date'):  # Handle datetime objects
            test_date = test_date.date()

        # Extract values handling both dict and plain values with fallback keys
        def get_value(primary_key, *fallback_keys):
            for key in (primary_key,) + fallback_keys:
                val = cbc_data.get(key)
                if isinstance(val, dict):
                    value = val.get('value')
                    if value is not None:
                        return value
                elif val is not None:
                    return val
            return None

        table_name = 'cbc_results'

        def column_exists(column: str) -> bool:
            if db.db_type != 'postgresql':
                return True
            return db.has_column(table_name, column)

        column_values: List[tuple] = []

        def add_column(column: str, value: Any):
            column_values.append((column, value))

        def add_column_if_exists(column: str, value: Any):
            if column_exists(column):
                column_values.append((column, value))

        # Core identifiers
        add_column('user_id', user_id)
        add_column('questionnaire_id', questionnaire_id)

        # Determine appropriate test date column for the current schema
        date_column = None
        if db.db_type == 'postgresql':
            for candidate in ('test_date', 'collection_date', 'cbc_test_date', 'sample_date', 'collected_at'):
                if column_exists(candidate):
                    date_column = candidate
                    break
        else:
            date_column = 'test_date'

        if date_column:
            add_column(date_column, test_date)

        add_column_if_exists('file_format', file_format)
        add_column_if_exists('extraction_method', "universal_extractor")

        # Include optional metadata columns if they exist in the target schema
        for meta_key, meta_value in metadata.items():
            if isinstance(meta_value, (dict, list)):
                meta_value = json.dumps(meta_value)
            if meta_key not in [col for col, _ in column_values]:
                add_column_if_exists(meta_key, meta_value)

        biomarker_mappings = [
            ('wbc', 'WBC'),
            ('rbc', 'RBC'),
            ('hgb', 'HGB', 'Hemoglobin'),
            ('hct', 'HCT', 'Hematocrit'),
            ('mcv', 'MCV'),
            ('mch', 'MCH'),
            ('mchc', 'MCHC'),
            ('rdw', 'RDW'),
            ('plt', 'PLT', 'Platelets'),
            ('mpv', 'MPV'),
            ('neut_abs', 'NEUT_ABS', 'Neutrophils'),
            ('lymph_abs', 'LYMPH_ABS', 'Lymphocytes'),
            ('mono_abs', 'MONO_ABS', 'MONO', 'Monocytes'),
            ('eos_abs', 'EOS_ABS', 'Eosinophils'),
            ('baso_abs', 'BASO_ABS', 'Basophils'),
            ('neut_pct', 'NEUT_PCT', 'Neutrophils'),
            ('lymph_pct', 'LYMPH_PCT', 'Lymphocytes'),
            ('mono_pct', 'MONO_PCT', 'Monocytes'),
            ('eos_pct', 'EOS_PCT', 'Eosinophils'),
            ('baso_pct', 'BASO_PCT', 'Basophils'),
            ('nlr', 'NLR'),
            ('nrbc_abs', 'NRBC_ABS'),
            ('nrbc_pct', 'NRBC_PCT')
        ]

        for column, primary, *fallbacks in biomarker_mappings:
            add_column_if_exists(column, get_value(primary, *fallbacks))

        columns = [col for col, _ in column_values]
        values = tuple(val for _, val in column_values)

        if not columns:
            raise ValueError("No columns available to insert into cbc_results")

        placeholder = "%s" if db.db_type == 'postgresql' else "?"
        placeholders = ', '.join([placeholder] * len(columns))
        base_query = f"""
        INSERT INTO cbc_results ({', '.join(columns)})
        VALUES ({placeholders})
        """

        if db.db_type == 'postgresql':
            # Attempt to insert via Supabase REST interface first to handle UUID casting and RLS
            supabase_clients: List[Any] = []

            try:
                client = get_supabase()
                if client:
                    supabase_clients.append(client)
            except Exception:
                pass

            try:
                admin_client = get_supabase_admin()
                if admin_client and admin_client not in supabase_clients:
                    supabase_clients.append(admin_client)
            except Exception:
                pass

            record = {}

            def serialize_value(val: Any):
                if isinstance(val, datetime):
                    return val.isoformat()
                if isinstance(val, date):
                    return val.isoformat()
                return val

            for column, value in column_values:
                record[column] = serialize_value(value)

            for client in supabase_clients:
                try:
                    response = client.table(table_name).insert(record).execute()
                    data = getattr(response, 'data', None)
                    if data:
                        inserted = data[0]
                        return inserted.get('id') or inserted.get('ID')
                except Exception as supabase_error:
                    print(f"Supabase insert via {client.__class__.__name__} failed: {supabase_error}")

            # Fallback to direct PostgreSQL insert if Supabase clients are unavailable
            query = base_query + " RETURNING id"
            result = db.execute_query(query, values, fetch='one')
            if isinstance(result, dict):
                return result.get('id')
            return result[0] if result else None
        else:
            db.execute_query(base_query, values)
            result = db.execute_query("SELECT last_insert_rowid() as id", fetch='one')
            if isinstance(result, dict):
                return result.get('id')
            return result[0] if result else None

    except Exception as e:
        print(f"Error saving CBC data: {e}")
        return None

def update_cbc_predictions(cbc_result_id: int, prediction_results: Dict) -> bool:
    """
    Update CBC record with ML predictions
    Args:
        cbc_result_id: ID of the cbc_results record
        prediction_results: Dict with cancer_probability, risk_level, etc.
    """
    db = get_db_manager()
    
    # Prepare missing biomarkers for storage
    missing_biomarkers = prediction_results.get('missing_features', [])
    if db.db_type == 'postgresql':
        missing_biomarkers_str = missing_biomarkers
    else:
        missing_biomarkers_str = ','.join(missing_biomarkers) if missing_biomarkers else None
    
    try:
        query = """
        UPDATE cbc_results 
        SET cancer_probability = ?,
            prediction_label = ?,
            risk_level = ?,
            confidence_score = ?,
            missing_biomarkers = ?,
            imputed_count = ?,
            imputation_warning = ?
        WHERE id = ?
        """
        
        params = (
            prediction_results.get('cancer_probability'),
            prediction_results.get('prediction_label'),
            prediction_results.get('risk_level'),
            prediction_results.get('confidence'),
            missing_biomarkers_str,
            prediction_results.get('imputed_count', 0),
            prediction_results.get('imputation_warning'),
            cbc_result_id
        )
        
        db.execute_query(query, params)
        return True
        
    except Exception as e:
        print(f"Error updating CBC predictions: {e}")
        return False

def get_cbc_data_for_prediction(cbc_result_id: int) -> Dict:
    """
    Retrieve CBC data from database for ML prediction
    Returns: Dictionary with CBC values ready for cancer classifier
    """
    db = get_db_manager()
    
    try:
        query = """
        SELECT wbc, nlr, hgb, mcv, plt, rdw, mono_abs as mono,
               rbc, hct, mch, mchc, mpv,
               neut_abs, lymph_abs, eos_abs, baso_abs,
               neut_pct, lymph_pct, mono_pct, eos_pct, baso_pct
        FROM cbc_results
        WHERE id = ?
        """
        
        result = db.execute_query(query, (cbc_result_id,), fetch='one')
        
        if not result:
            return None
        
        # Map to dictionary (handling both dict and tuple results)
        if isinstance(result, dict):
            return result
        else:
            # SQLite returns tuple, map to column names
            columns = ['WBC', 'NLR', 'HGB', 'MCV', 'PLT', 'RDW', 'MONO',
                      'RBC', 'HCT', 'MCH', 'MCHC', 'MPV',
                      'NEUT_ABS', 'LYMPH_ABS', 'EOS_ABS', 'BASO_ABS',
                      'NEUT_PCT', 'LYMPH_PCT', 'MONO_PCT', 'EOS_PCT', 'BASO_PCT']
            return dict(zip(columns, result))
        
    except Exception as e:
        print(f"Error retrieving CBC data: {e}")
        return None

# Legacy function for backward compatibility
def save_cbc_results(user_id: int, cbc_data: Dict, prediction_results: Dict, 
                     questionnaire_id: int = None, file_format: str = "unknown") -> bool:
    """
    DEPRECATED: Use save_cbc_data() + update_cbc_predictions() instead
    Save CBC results and prediction to database (legacy combined function)
    """
    metadata = {
        'filename': 'legacy-save',
        'extraction_source': 'legacy_api',
        'extraction_success': True,
        'raw_extraction_data': cbc_data
    }
    # Save CBC data first
    cbc_result_id = save_cbc_data(user_id, questionnaire_id, cbc_data, None, file_format, metadata)
    
    if cbc_result_id:
        # Update with predictions
        return update_cbc_predictions(cbc_result_id, prediction_results)
    
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