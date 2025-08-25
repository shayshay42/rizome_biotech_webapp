#!/usr/bin/env python3
"""
Find Correct Supabase Host
Try different hostname formats to find the working one
"""

import socket
import psycopg2

def test_hostname_formats():
    """Test different Supabase hostname formats"""
    
    print("🔍 FINDING CORRECT SUPABASE HOSTNAME")
    print("="*50)
    
    project_id = "kqzmwzosluljckadthup"
    password = "ZnJJSIChnpkAmtcS"  # Your password
    
    # Common Supabase hostname patterns
    hostnames_to_try = [
        f"db.{project_id}.supabase.co",           # Standard format
        f"{project_id}.supabase.co",              # Alternative format  
        f"aws-0-us-east-1.pooler.supabase.com",  # Connection pooling
        f"aws-0-us-west-1.pooler.supabase.com",  # Different region
        f"aws-0-eu-west-1.pooler.supabase.com",  # EU region
        f"{project_id}.db.supabase.co",          # Reverse format
    ]
    
    print("🌐 Testing hostname resolution...")
    working_hostnames = []
    
    for hostname in hostnames_to_try:
        try:
            ip = socket.gethostbyname(hostname)
            print(f"✅ {hostname} → {ip}")
            working_hostnames.append(hostname)
        except socket.gaierror:
            print(f"❌ {hostname} - No resolution")
    
    if not working_hostnames:
        print(f"\n❌ No hostnames resolved. Possible issues:")
        print(f"   • Project might be paused/inactive")
        print(f"   • Different hostname format")
        print(f"   • DNS propagation delay")
        return None
    
    print(f"\n🔗 Testing database connections...")
    
    for hostname in working_hostnames:
        try:
            print(f"\n🧪 Testing: {hostname}")
            
            connection = psycopg2.connect(
                user="postgres",
                password=password,
                host=hostname,
                port="5432",
                dbname="postgres",
                connect_timeout=10
            )
            
            cursor = connection.cursor()
            cursor.execute("SELECT NOW();")
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            print(f"✅ SUCCESS! Working hostname: {hostname}")
            print(f"   Time: {result[0]}")
            
            return hostname
            
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    return None

def show_connection_guide():
    """Show how to get correct connection details"""
    
    print(f"\n📝 HOW TO GET CORRECT SUPABASE CONNECTION:")
    print(f"="*50)
    print(f"")
    print(f"1. Go to: https://supabase.com/dashboard")
    print(f"2. Select your project: kqzmwzosluljckadthup")
    print(f"3. Go to Settings → Database")
    print(f"4. Scroll to 'Connection string'")
    print(f"5. Copy the URI that looks like:")
    print(f"   postgresql://postgres.xxx:[PASSWORD]@[HOST]:5432/postgres")
    print(f"")
    print(f"6. Extract the HOST part (between @ and :5432)")
    print(f"")
    print(f"🔧 Alternative: Try the Supabase CLI")
    print(f"   npm install -g supabase")
    print(f"   supabase status")

if __name__ == "__main__":
    working_host = test_hostname_formats()
    
    if working_host:
        print(f"\n🎉 Found working hostname: {working_host}")
        print(f"\n✏️  Update your secrets.toml with:")
        print(f"   host = \"{working_host}\"")
    else:
        show_connection_guide()