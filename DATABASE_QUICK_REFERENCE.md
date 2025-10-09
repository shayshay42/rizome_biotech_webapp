# Supabase Auth + Database Integration Guide

## Quick Reference

### Problem Fixed
- ✅ Username now stored in database (user_profiles table)
- ✅ Foreign keys connect auth.users to questionnaires & cbc_results
- ✅ CASCADE DELETE removes user data when user deleted
- ✅ Row Level Security protects user privacy

### Files Changed
- ✅ `utils/auth.py` - Added `sync_user_profile()` function
- ✅ `supabase/migrations/003_migrate_to_supabase_auth.sql` - New migration
- ✅ `test_migration.py` - Migration verification script

---

## Quick Start

### 1. Apply Migration

**Via Supabase Dashboard (Easiest):**
1. Go to https://supabase.com/dashboard
2. Select project → SQL Editor → New Query
3. Copy/paste: `supabase/migrations/003_migrate_to_supabase_auth.sql`
4. Click Run

### 2. Verify Migration

```bash
python test_migration.py
```

Should see:
```
✅ Connected to Supabase
✅ user_profiles table exists
✅ Foreign keys configured
```

### 3. Test in App

```bash
streamlit run streamlit_app.py
```

- Register new user
- Check Supabase → Table Editor → user_profiles
- Username should be there!

---

## What Changed

### Database Schema

**NEW TABLE: `user_profiles`**
```sql
CREATE TABLE user_profiles (
    id UUID → auth.users.id,  -- Same UUID as Supabase Auth
    username VARCHAR(50),     -- User's chosen username
    display_name VARCHAR(100),
    bio TEXT,
    avatar_url TEXT,
    preferences JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**UPDATED: `questionnaires` and `cbc_results`**
```sql
-- Changed from INTEGER to UUID
ALTER TABLE questionnaires 
    ALTER COLUMN user_id TYPE UUID;

-- Added foreign key to auth.users
ALTER TABLE questionnaires
    ADD CONSTRAINT questionnaires_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES auth.users(id)
    ON DELETE CASCADE;  -- Automatically delete when user deleted
```

### Code Changes

**New Function in `utils/auth.py`:**
```python
def sync_user_profile(user_id, username):
    """Sync username to user_profiles table"""
    # Creates or updates profile in database
```

**Updated Functions:**
- `register_user()` - Calls `sync_user_profile()` after signup
- `authenticate_user()` - Calls `sync_user_profile()` on login

---

## How It Works

### Registration Flow

```
User signs up
    ↓
Supabase Auth creates user
    ↓ (username in metadata)
Database trigger creates profile
    ↓ (extracts username)
App syncs as backup
    ↓
✅ Username in both places!
```

### Data Access Flow

```
User queries their data
    ↓
RLS checks: auth.uid() == user_id?
    ↓
✅ Allow if match
❌ Deny if not
```

---

## Troubleshooting

### "user_profiles does not exist"
**Fix:** Apply migration via Supabase Dashboard

### "Cannot cast INTEGER to UUID"
**Fix:** Delete test data first:
```sql
DELETE FROM cbc_results;
DELETE FROM questionnaires;
```
Then apply migration.

### Username not appearing
**Fix:** Sign in again - it will auto-sync

---

## Testing Checklist

- [ ] Apply migration
- [ ] Run `python test_migration.py`
- [ ] Register new test user
- [ ] Check user_profiles table has username
- [ ] Submit questionnaire
- [ ] Check questionnaires.user_id is UUID
- [ ] Upload CBC report
- [ ] Check cbc_results.user_id is UUID

---

## Full Documentation

See `DATABASE_MIGRATION_GUIDE.md` for complete details.
