# Supabase Auth Setup Guide

## ✅ What Changed

We've refactored the app to use **Supabase Auth** instead of manual bcrypt password hashing. This provides:

- ✅ Secure password hashing (managed by Supabase)
- ✅ Email verification
- ✅ Password reset emails
- ✅ Session management
- ✅ Future: OAuth (Google/GitHub login)
- ✅ No manual password handling

## 📋 Setup Steps

### 1. Get Supabase Credentials

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project: `kqzmwzosluljckadthup`
3. Go to **Settings** → **API**
4. Copy these values:
   - **Project URL**: `https://kqzmwzosluljckadthup.supabase.co`
   - **Anon/Public Key**: The long string starting with `eyJ...`

### 2. Create Local Secrets File

Create `.streamlit/secrets.toml` (not committed to git):

```toml
[supabase]
url = "https://kqzmwzosluljckadthup.supabase.co"
key = "YOUR_ANON_KEY_HERE"  # Paste the anon key from dashboard
```

### 3. Enable Email Auth in Supabase

1. Go to **Authentication** → **Providers** in Supabase dashboard
2. Make sure **Email** provider is enabled
3. **Optional**: Disable email confirmation for testing:
   - Go to **Authentication** → **Settings**
   - Under "Email Auth", toggle off **"Enable email confirmations"**
   - This lets you test without needing to check emails

### 4. Test Locally

```bash
cd /Users/shayanhajhashemi/Documents/Rhizome/streamlit_app
streamlit run streamlit_app.py
```

Try to:
- ✅ Register a new user
- ✅ Login with that user
- ✅ Check that session persists

### 5. Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [Streamlit Cloud](https://share.streamlit.io)
3. In your app settings, add secrets:

```toml
[supabase]
url = "https://kqzmwzosluljckadthup.supabase.co"
key = "YOUR_ANON_KEY_HERE"
```

## 🔧 Database Schema (No Changes Needed!)

Supabase Auth creates its own `auth.users` table automatically. Your existing tables (`questionnaires`, `cbc_results`) just need to reference the Supabase user UUID instead of a custom user ID.

**Important**: The `user_id` column in your tables should be type `UUID` (or `TEXT` for the UUID string).

### If You Need to Update Schema:

```sql
-- Make sure user_id columns accept UUIDs
ALTER TABLE questionnaires ALTER COLUMN user_id TYPE UUID USING user_id::uuid;
ALTER TABLE cbc_results ALTER COLUMN user_id TYPE UUID USING user_id::uuid;

-- Optional: Add foreign key constraints to Supabase auth
-- (Only if you want automatic cascade deletes)
-- Note: This requires proper Row Level Security policies
```

## 🧪 Testing

Run the new test suite:

```bash
/opt/homebrew/opt/python@3.11/bin/python3.11 test_supabase_auth.py
```

This will test:
- ✅ Supabase client connection
- ✅ User registration
- ✅ User login
- ✅ Session persistence
- ✅ Data save/retrieve with UUID user IDs

## 🔐 Security Benefits

### Old System (Manual bcrypt):
- ❌ Manual password hashing
- ❌ Manual session management
- ❌ No email verification
- ❌ No password reset
- ❌ Store passwords in database
- ❌ Complex error-prone code

### New System (Supabase Auth):
- ✅ Managed password hashing
- ✅ Automatic session handling
- ✅ Built-in email verification
- ✅ Built-in password reset
- ✅ Passwords never in your database
- ✅ Simple, secure API

## 🚀 Next Steps

After testing locally:

1. **Enable Email Confirmations** (production):
   - Go to Auth → Settings
   - Enable "Enable email confirmations"
   - Configure email templates if desired

2. **Add OAuth** (optional):
   - Go to Auth → Providers
   - Enable Google, GitHub, etc.
   - Update code to add OAuth buttons

3. **Set Up Row Level Security** (recommended):
   - Ensures users can only see their own data
   - Auto-configured with Supabase Auth

## 📝 Code Changes Summary

### What Was Changed:

1. **`utils/auth.py`**: Complete rewrite to use Supabase Auth
   - `register_user()`: Now uses `supabase.auth.sign_up()`
   - `authenticate_user()`: Now uses `supabase.auth.sign_in_with_password()`
   - `logout()`: Now uses `supabase.auth.sign_out()`
   - Session restored automatically on app load

2. **`utils/supabase_client.py`**: New file
   - Centralized Supabase client creation
   - Handles credentials from secrets or env vars

3. **`requirements.txt`**: Updated
   - Added `supabase>=2.0.0`
   - Removed `bcrypt` and `streamlit-authenticator` (not needed)

4. **`.streamlit/secrets.toml.template`**: Updated
   - Added `url` and `key` fields for Supabase Auth

### What Stayed The Same:

- ✅ Database tables (questionnaires, cbc_results)
- ✅ ML model integration
- ✅ CBC extraction pipeline
- ✅ Streamlit UI
- ✅ All business logic

## ⚠️ Migration Notes

**Existing users in database will NOT work** with the new system because:
- Old system: Custom users table with bcrypt passwords
- New system: Supabase auth.users table with managed auth

**Solution**: After deploying, users will need to re-register. You can:
1. Clear old users table (no longer used)
2. Inform users to re-register
3. Or: Write migration script to copy users to Supabase Auth (complex)

## 💡 Tips

- **Development**: Disable email confirmation for faster testing
- **Production**: Enable email confirmation for security
- **Local Testing**: Use `.streamlit/secrets.toml`
- **Cloud Deployment**: Use Streamlit Cloud secrets UI
- **Security**: Never commit secrets.toml to git (already in .gitignore)
