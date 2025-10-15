"""
Fix RLS policies using Python and service role key
"""

import sys
sys.path.insert(0, '.')

from utils.supabase_client import get_supabase_admin
from getpass import getpass

def fix_rls_policies():
    print("\n" + "="*60)
    print("FIX RLS POLICIES FOR QUESTIONNAIRES AND CBC_RESULTS")
    print("="*60)
    
    print("\nThis will fix the Row-Level Security policies that are")
    print("blocking you from saving questionnaires and CBC results.")
    
    # Get admin client
    admin = get_supabase_admin()
    if not admin:
        print("\n⚠️  No service role key found in secrets.")
        service_key = getpass("\nEnter your Supabase service role key: ")
        if not service_key or len(service_key) < 100:
            print("❌ Invalid service key")
            return False
        
        # Create admin client manually
        from supabase import create_client
        url = "https://kqzmwzosluljckadthup.supabase.co"
        admin = create_client(url, service_key)
    
    print("\n✅ Connected with service role")
    
    # SQL to fix RLS policies
    sql_commands = [
        # Drop old policies for questionnaires
        "DROP POLICY IF EXISTS \"Users can only view their own questionnaires\" ON public.questionnaires;",
        "DROP POLICY IF EXISTS \"Users can only insert their own questionnaires\" ON public.questionnaires;",
        "DROP POLICY IF EXISTS \"Users can only update their own questionnaires\" ON public.questionnaires;",
        "DROP POLICY IF EXISTS \"Users can only delete their own questionnaires\" ON public.questionnaires;",
        
        # Drop old policies for cbc_results
        "DROP POLICY IF EXISTS \"Users can only view their own cbc_results\" ON public.cbc_results;",
        "DROP POLICY IF EXISTS \"Users can only insert their own cbc_results\" ON public.cbc_results;",
        "DROP POLICY IF EXISTS \"Users can only update their own cbc_results\" ON public.cbc_results;",
        "DROP POLICY IF EXISTS \"Users can only delete their own cbc_results\" ON public.cbc_results;",
        
        # Enable RLS
        "ALTER TABLE public.questionnaires ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE public.cbc_results ENABLE ROW LEVEL SECURITY;",
        
        # Create new permissive policies for questionnaires
        """CREATE POLICY "Allow authenticated users to insert their own questionnaires"
           ON public.questionnaires FOR INSERT TO authenticated
           WITH CHECK (auth.uid() = user_id);""",
        
        """CREATE POLICY "Allow authenticated users to view their own questionnaires"
           ON public.questionnaires FOR SELECT TO authenticated
           USING (auth.uid() = user_id);""",
        
        """CREATE POLICY "Allow authenticated users to update their own questionnaires"
           ON public.questionnaires FOR UPDATE TO authenticated
           USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);""",
        
        """CREATE POLICY "Allow authenticated users to delete their own questionnaires"
           ON public.questionnaires FOR DELETE TO authenticated
           USING (auth.uid() = user_id);""",
        
        # Create new permissive policies for cbc_results
        """CREATE POLICY "Allow authenticated users to insert their own cbc_results"
           ON public.cbc_results FOR INSERT TO authenticated
           WITH CHECK (auth.uid() = user_id);""",
        
        """CREATE POLICY "Allow authenticated users to view their own cbc_results"
           ON public.cbc_results FOR SELECT TO authenticated
           USING (auth.uid() = user_id);""",
        
        """CREATE POLICY "Allow authenticated users to update their own cbc_results"
           ON public.cbc_results FOR UPDATE TO authenticated
           USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);""",
        
        """CREATE POLICY "Allow authenticated users to delete their own cbc_results"
           ON public.cbc_results FOR DELETE TO authenticated
           USING (auth.uid() = user_id);""",
        
        # Grant permissions
        "GRANT ALL ON public.questionnaires TO authenticated;",
        "GRANT ALL ON public.cbc_results TO authenticated;",
        "GRANT ALL ON public.questionnaires TO service_role;",
        "GRANT ALL ON public.cbc_results TO service_role;",
    ]
    
    print("\n🔧 Executing SQL commands...")
    
    # Execute via REST API (PostgREST doesn't support direct SQL)
    import requests
    
    url = "https://kqzmwzosluljckadthup.supabase.co"
    service_key = admin.supabase_key
    
    # Combine all SQL into one command
    combined_sql = "\n".join(sql_commands)
    
    print("\n📋 Since direct SQL execution isn't available via Python,")
    print("please run this in your Supabase SQL Editor:")
    print("\n" + "="*60)
    print(combined_sql)
    print("="*60)
    
    print("\n🌐 Open: https://supabase.com/dashboard/project/kqzmwzosluljckadthup/sql/new")
    print("\nAfter running the SQL, your app will be able to save data!")
    
    return None

if __name__ == '__main__':
    fix_rls_policies()
