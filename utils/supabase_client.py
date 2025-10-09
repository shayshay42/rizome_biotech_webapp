"""
Supabase Client Configuration
Centralized Supabase client for authentication and database operations
"""

import streamlit as st
from supabase import create_client, Client
import os

def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance

    Uses Streamlit secrets in production or environment variables in development
    """

    # Try to get credentials from Streamlit secrets first
    try:
        if hasattr(st, 'secrets') and 'supabase' in st.secrets:
            url = st.secrets['supabase'].get('url') or st.secrets['supabase'].get('supabase_url')
            key = st.secrets['supabase'].get('key') or st.secrets['supabase'].get('supabase_key')

            if url and key:
                return create_client(url, key)
    except:
        pass

    # Fall back to environment variables
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

    if not url or not key:
        raise ValueError(
            "Supabase credentials not found. Please set either:\n"
            "1. Streamlit secrets: .streamlit/secrets.toml with [supabase] url and key\n"
            "2. Environment variables: SUPABASE_URL and SUPABASE_KEY"
        )

    return create_client(url, key)

# Global client instance (lazy loaded)
_supabase_client = None

def get_supabase() -> Client:
    """Get cached Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = get_supabase_client()
    return _supabase_client
