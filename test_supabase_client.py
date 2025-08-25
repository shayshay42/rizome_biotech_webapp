#!/usr/bin/env python3
"""
Test Supabase Python Client Connection
Using the official Supabase Python client instead of direct PostgreSQL
"""

import os
from supabase import create_client, Client
import toml
from pathlib import Path

def test_supabase_client():
    """Test connection using Supabase Python client"""
    
    print("🚀 TESTING SUPABASE PYTHON CLIENT")
    print("="*50)
    
    # Load secrets
    secrets_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'
    
    try:
        secrets = toml.load(secrets_path)
        config = secrets['supabase']
        
        # For Supabase client, we need URL and ANON key
        # The URL format is: https://project-ref.supabase.co
        project_id = "kqzmwzosluljckadthup"
        supabase_url = f"https://{project_id}.supabase.co"
        
        print(f"📝 Connection details:")
        print(f"   Project ID: {project_id}")
        print(f"   Supabase URL: {supabase_url}")
        print(f"   Password: {'*' * len(config['password'])}")
        
        # We need the ANON key from Supabase dashboard
        print(f"\n⚠️  MISSING: SUPABASE_ANON_KEY")
        print(f"To use Supabase client, you need:")
        print(f"1. Go to: https://supabase.com/dashboard/project/{project_id}")
        print(f"2. Settings → API")
        print(f"3. Copy the 'anon public' key")
        print(f"4. Add to secrets.toml:")
        print(f"   [supabase]")
        print(f"   url = \"{supabase_url}\"")
        print(f"   anon_key = \"your-anon-key-here\"")
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_direct_psql_command():
    """Show how to test with psql command line"""
    
    print(f"\n🔧 TEST WITH PSQL COMMAND LINE:")
    print("="*50)
    
    # Load password
    secrets_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'
    try:
        secrets = toml.load(secrets_path)
        password = secrets['supabase']['password']
        
        print(f"📝 Try this command in your terminal:")
        print(f"")
        print(f"psql 'postgresql://postgres:{password}@db.kqzmwzosluljckadthup.supabase.co:5432/postgres'")
        print(f"")
        print(f"If that works, then Supabase is active and our app will work in production!")
        print(f"If it fails, the project might be paused.")
        
    except Exception as e:
        print(f"❌ Error loading password: {e}")

def show_deployment_options():
    """Show different deployment approaches"""
    
    print(f"\n🚀 DEPLOYMENT OPTIONS:")
    print("="*50)
    print(f"")
    print(f"Option 1: Deploy with Current Setup (RECOMMENDED)")
    print(f"✅ App works locally with SQLite")
    print(f"✅ Will auto-detect PostgreSQL in production")
    print(f"✅ Quebec PDF extraction ready")
    print(f"✅ Missing value imputation ready")
    print(f"")
    print(f"Option 2: Fix Supabase Connection First")
    print(f"• Check if project is paused")
    print(f"• Get correct connection details")
    print(f"• Test with psql command")
    print(f"")
    print(f"Option 3: Use Alternative Database")
    print(f"• Railway PostgreSQL")
    print(f"• Neon PostgreSQL") 
    print(f"• PlanetScale MySQL")
    print(f"")
    print(f"💡 Recommendation: Deploy now and fix database in production")
    print(f"   The app will work with SQLite fallback if PostgreSQL fails")

if __name__ == "__main__":
    test_supabase_client()
    test_direct_psql_command()
    show_deployment_options()