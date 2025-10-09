"""
Supabase Client Configuration
Centralized Supabase client for authentication and database operations
"""

import streamlit as st
from supabase import create_client, Client
import os
from typing import Optional

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
_supabase_admin_client = None

def get_supabase() -> Client:
    """Get cached Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = get_supabase_client()
    return _supabase_client


def get_supabase_admin() -> Optional[Client]:
    """Get Supabase client authenticated with service role key (if available)."""

    global _supabase_admin_client
    if _supabase_admin_client is not None:
        return _supabase_admin_client

    url = None
    service_key = None

    # Try Streamlit secrets first
    try:
        if hasattr(st, 'secrets') and 'supabase' in st.secrets:
            config = st.secrets['supabase']
            url = config.get('url') or config.get('supabase_url') or url
            service_key = (
                config.get('service_key')
                or config.get('service_role_key')
                or config.get('supabase_service_key')
            )
    except Exception:
        pass

    # Fall back to environment variables
    if not url:
        url = os.getenv('SUPABASE_URL') or os.getenv('SUPABASE_PROJECT_URL')
    if not service_key:
        service_key = (
            os.getenv('SUPABASE_SERVICE_KEY')
            or os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            or os.getenv('SUPABASE_SECRET_KEY')
        )

    if not url or not service_key:
        return None

    try:
        _supabase_admin_client = create_client(url, service_key)
    except Exception:
        _supabase_admin_client = None

    return _supabase_admin_client
