#!/usr/bin/env python3
"""
Check Supabase Connection Details
Help diagnose and find correct Supabase connection details
"""

import socket
import requests

def check_supabase_details():
    """Check various Supabase connection formats"""
    
    print("🔍 CHECKING SUPABASE CONNECTION DETAILS")
    print("="*60)
    
    project_id = "kqzmwzosluljckadthup"
    
    # Common Supabase hostname patterns
    hostnames_to_try = [
        f"db.{project_id}.supabase.co",
        f"{project_id}.supabase.co", 
        f"aws-0-us-east-1.pooler.supabase.com",
        f"db-{project_id}.supabase.co"
    ]
    
    print("🌐 Testing hostname resolution...")
    
    for hostname in hostnames_to_try:
        try:
            socket.gethostbyname(hostname)
            print(f"✅ {hostname} - RESOLVES")
        except socket.gaierror:
            print(f"❌ {hostname} - DOES NOT RESOLVE")
    
    print(f"\n📝 How to get correct Supabase connection details:")
    print(f"")
    print(f"1. Go to your Supabase Dashboard: https://supabase.com/dashboard")
    print(f"2. Select your project: {project_id}")
    print(f"3. Go to Settings → Database")
    print(f"4. Look for 'Connection string' or 'Database URL'")
    print(f"5. Copy the correct hostname from there")
    print(f"")
    print(f"🔗 The connection string format should be:")
    print(f"   postgresql://postgres:[password]@[correct-host]:5432/postgres")
    print(f"")
    print(f"⚠️  Common issues:")
    print(f"   • Hostname format has changed")
    print(f"   • Project might be paused/inactive")
    print(f"   • Connection pooling enabled (different port)")
    print(f"")
    print(f"🔧 Alternative test:")
    print(f"   Try connecting with psql from command line:")
    print(f"   psql -h [correct-host] -p 5432 -d postgres -U postgres")

if __name__ == "__main__":
    check_supabase_details()