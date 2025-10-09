# Username Display in Supabase Auth Dashboard - Explained

## The Confusion

When you look at the **Authentication** tab in Supabase Dashboard, you don't see a "Display Name" column with the username. This is expected!

## Why Username Isn't in a "Display Name" Column

**Important:** Supabase Auth **doesn't have a dedicated display_name column** in the users table. The columns you see in the Authentication tab are:

- Email
- Provider
- Created At
- Last Sign In
- (Sometimes) Phone

**The username IS stored** - it's just hidden in the `raw_user_meta_data` JSON field!

---

## Where Username Is Actually Stored

### Location 1: `auth.users.raw_user_meta_data` (JSON)

```json
{
  "username": "john_doe",
  "display_name": "john_doe",
  "full_name": "john_doe"
}
```

**How to see it:**
1. Go to Authentication → Users
2. Click on any user
3. Scroll down to **"User Metadata"** section
4. You'll see the JSON with username!

### Location 2: `user_profiles` table

```
| id (UUID) | username  | display_name | created_at |
|-----------|-----------|--------------|------------|
| abc123... | john_doe  | john_doe     | 2025-10-08 |
```

**How to see it:**
1. Go to Table Editor
2. Select `user_profiles` table
3. Username is right there in a column! ✅

---

## How to View Usernames in Supabase Dashboard

### ✅ Method 1: Table Editor (Easiest)

1. Go to **Table Editor** in sidebar
2. Click **user_profiles** table
3. See the **username** column clearly displayed

### ✅ Method 2: Authentication Tab → User Details

1. Go to **Authentication** in sidebar
2. Click **Users** tab
3. Click on any user row
4. Scroll down to **"User Metadata"** section
5. Look for `"username": "..."` in the JSON

### ✅ Method 3: SQL Query (Most Detailed)

1. Go to **SQL Editor**
2. Run this query:

```sql
SELECT 
  au.id,
  au.email,
  au.raw_user_meta_data->>'username' as username,
  au.raw_user_meta_data->>'display_name' as display_name,
  up.username as profile_username,
  up.display_name as profile_display_name
FROM auth.users au
LEFT JOIN user_profiles up ON au.id = up.id;
```

This shows username from both locations side by side!

---

## What Changed in Your Code

### Updated `register_user()` function

**Before:**
```python
"options": {
    "data": {
        "username": username  # Only username
    }
}
```

**After:**
```python
"options": {
    "data": {
        "username": username,
        "display_name": username,  # Now also sets this
        "full_name": username      # And this
    }
}
```

**Why:** Stores username in multiple metadata fields for better compatibility with different Supabase features.

---

## Test It Yourself

### Step 1: Register a New User

```bash
streamlit run streamlit_app.py
```

Register with:
- Username: `test_user_123`
- Email: `test@example.com`
- Password: `password123`

### Step 2: Check Supabase Dashboard

**Option A - Table Editor:**
1. Go to Table Editor
2. Click `user_profiles`
3. See `test_user_123` in username column ✅

**Option B - Authentication:**
1. Go to Authentication → Users
2. Click on `test@example.com`
3. Scroll to "User Metadata"
4. See:
   ```json
   {
     "username": "test_user_123",
     "display_name": "test_user_123",
     "full_name": "test_user_123"
   }
   ```

---

## Why This Design?

### Supabase Auth's Approach

Supabase Auth is minimal by design:
- Core fields: email, password (encrypted), phone
- Everything else: stored in `user_metadata` JSON
- No built-in "display name" column

### Your App's Approach (Best Practice ✅)

1. **Store in Auth Metadata** - For auth-related lookups
2. **Store in user_profiles Table** - For app queries
3. **Sync on Registration & Login** - Keep both in sync

**Benefits:**
- ✅ Username accessible via Auth API
- ✅ Username queryable in database
- ✅ Can search/filter by username
- ✅ Can join with other tables
- ✅ Best of both worlds!

---

## Common Questions

### Q: Why don't I see "Display Name" in the user list?

**A:** Supabase Auth UI only shows: Email, Provider, Created At, Last Sign In. The display name is in the metadata JSON, visible when you click on a user.

### Q: Can I make username show in the users list?

**A:** Not in the built-in Authentication tab. But you can:
1. Use Table Editor → user_profiles (clearer view)
2. Use SQL Editor with custom query
3. Build custom admin UI that shows username

### Q: Is the username actually being saved?

**A:** Yes! Check by:
1. Running `python check_username_storage.py`
2. Checking user_profiles table
3. Clicking on user in Authentication → Users → User Metadata section

### Q: Do I need to update existing users?

**A:** New users will automatically have username set. For existing users, they'll get their username synced next time they log in (the code updates on login too).

---

## Verification Checklist

- [ ] Run migration: `003_migrate_to_supabase_auth.sql`
- [ ] Run test: `python check_username_storage.py`
- [ ] Register new test user with username
- [ ] Check Table Editor → user_profiles → username column ✅
- [ ] Check Authentication → Users → Click user → User Metadata ✅
- [ ] Verify username appears in both places

---

## Summary

**The username IS being stored!** It's just that:

1. ✅ In `auth.users` - it's in the `raw_user_meta_data` JSON (not a separate column)
2. ✅ In `user_profiles` - it's in the `username` column (easy to see!)

**To see it in Supabase Dashboard:**
- **Easiest:** Table Editor → user_profiles table
- **Also works:** Authentication → Users → Click user → User Metadata section

**Your code is correct!** The username is being stored properly in both locations. The confusion is just about where to look in the dashboard UI. 😊
