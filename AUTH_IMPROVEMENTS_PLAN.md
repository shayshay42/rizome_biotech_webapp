# Supabase Auth Improvements Plan

## Current Status: ✅ Good Foundation

Your implementation follows canonical Supabase patterns. These improvements will make it production-ready.

---

## Recommended Enhancements

### 1. Password Reset Flow ⭐ HIGH PRIORITY

**Current**: No password reset option
**Improvement**: Add "Forgot Password?" link

```python
# In streamlit_app.py, add to Sign In tab:
forgot_password = st.checkbox("Forgot password?")
if forgot_password:
    reset_email = st.text_input("Enter your email for password reset")
    if st.button("Send Reset Link"):
        supabase.auth.reset_password_for_email(reset_email)
        st.success("Password reset email sent! Check your inbox.")
```

**Supabase Setup Required**:
- Go to Authentication → Email Templates in Supabase dashboard
- Customize the "Reset Password" email template
- Set redirect URL to your app

---

### 2. Email Verification Handling ⭐ HIGH PRIORITY

**Current**: Registration says "check email" but no verification flow
**Improvement**: Handle email confirmation callbacks

```python
# Add to init_auth() in utils/auth.py
def handle_email_verification():
    """Handle email verification callback from Supabase"""
    # Check URL parameters for verification token
    params = st.query_params
    
    if 'token_hash' in params and 'type' in params:
        if params['type'] == 'signup':
            # Verify the email
            try:
                supabase = get_supabase()
                supabase.auth.verify_otp({
                    'token_hash': params['token_hash'],
                    'type': 'email'
                })
                st.success("✅ Email verified! You can now sign in.")
                # Clear URL parameters
                st.query_params.clear()
            except Exception as e:
                st.error(f"Verification failed: {e}")
```

**Supabase Setup**:
- Enable email confirmations in Authentication → Settings
- Set Site URL to your deployed app URL
- Set Redirect URLs to `https://your-app.streamlit.app/`

---

### 3. OAuth Providers (Google, GitHub) ⭐ MEDIUM PRIORITY

**Current**: Email/password only
**Improvement**: Add social login buttons

```python
# In show_landing_page(), add before tabs:
st.markdown("### Sign in with")
col1, col2 = st.columns(2)

with col1:
    if st.button("🔵 Continue with Google", use_container_width=True):
        supabase = get_supabase()
        response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": "https://your-app.streamlit.app/"
            }
        })
        st.write(f"[Click to authenticate]({response.url})")

with col2:
    if st.button("⚫ Continue with GitHub", use_container_width=True):
        supabase = get_supabase()
        response = supabase.auth.sign_in_with_oauth({
            "provider": "github",
            "options": {
                "redirect_to": "https://your-app.streamlit.app/"
            }
        })
        st.write(f"[Click to authenticate]({response.url})")

st.markdown("---")
st.markdown("### Or use email/password")
```

**Supabase Setup**:
1. Go to Authentication → Providers
2. Enable Google:
   - Create OAuth client in Google Cloud Console
   - Add Client ID and Secret to Supabase
3. Enable GitHub:
   - Create OAuth App in GitHub Settings
   - Add Client ID and Secret to Supabase

---

### 4. Better Error Handling ⭐ MEDIUM PRIORITY

**Current**: Generic error messages
**Improvement**: User-friendly error messages with help text

```python
# In authenticate_user() in utils/auth.py, replace error handling:
except Exception as e:
    error_msg = str(e).lower()
    
    if "invalid login credentials" in error_msg:
        return False, None, None, "Invalid email or password. Please try again."
    elif "email not confirmed" in error_msg:
        return False, None, None, "Please verify your email before signing in. Check your inbox."
    elif "too many requests" in error_msg:
        return False, None, None, "Too many login attempts. Please try again in a few minutes."
    else:
        return False, None, None, f"Sign in failed: {str(e)}"
```

---

### 5. Session Timeout & Refresh ⭐ LOW PRIORITY

**Current**: Session persists indefinitely until logout
**Improvement**: Automatic session refresh

```python
# In init_auth() in utils/auth.py:
def refresh_session():
    """Refresh auth session if needed"""
    try:
        supabase = get_supabase()
        session = supabase.auth.get_session()
        
        if session and session.expires_at:
            import time
            # Refresh if expiring in next 5 minutes
            if session.expires_at - time.time() < 300:
                supabase.auth.refresh_session()
                st.toast("Session refreshed", icon="🔄")
    except:
        # Session expired, force logout
        logout()
        st.warning("Your session has expired. Please sign in again.")
        st.rerun()
```

---

### 6. Remember Me Option ⭐ LOW PRIORITY

**Current**: All sessions persist equally
**Improvement**: Let users choose session duration

```python
# In Sign In form:
remember_me = st.checkbox("Remember me for 30 days", value=True)

# In authenticate_user():
response = supabase.auth.sign_in_with_password({
    "email": email,
    "password": password,
    "options": {
        "should_create_session": True,
        "persistent_session": remember_me  # Longer session if checked
    }
})
```

---

### 7. User Profile Management ⭐ LOW PRIORITY

**Current**: Username set at registration, cannot change
**Improvement**: Add profile settings page

```python
def show_profile_page():
    """User profile management"""
    st.title("⚙️ Profile Settings")
    
    user = get_current_user()
    
    with st.form("update_profile"):
        new_username = st.text_input("Username", value=user['username'])
        new_email = st.text_input("Email (read-only)", value=user['email'], disabled=True)
        
        st.markdown("### Change Password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("Update Profile"):
            # Update username in metadata
            if new_username != user['username']:
                supabase = get_supabase()
                supabase.auth.update_user({
                    "data": {"username": new_username}
                })
                st.success("Username updated!")
            
            # Update password
            if new_password and new_password == confirm_password:
                supabase.auth.update_user({
                    "password": new_password
                })
                st.success("Password updated!")
```

---

## Implementation Priority

1. **Phase 1 (Essential)**: 
   - ✅ Password reset flow
   - ✅ Email verification handling
   - ✅ Better error messages

2. **Phase 2 (Nice to Have)**:
   - OAuth providers (Google/GitHub)
   - Session refresh
   - User profile page

3. **Phase 3 (Polish)**:
   - Remember me option
   - Multi-factor authentication (MFA)
   - Rate limiting display

---

## Current State: Already Canonical! ✅

Your implementation is actually **already canonical** for Streamlit + Supabase. These improvements just add convenience features.

**What makes it canonical**:
- ✅ Direct Supabase Auth API calls
- ✅ Proper session management
- ✅ UUID user IDs
- ✅ User metadata storage
- ✅ Clean separation of concerns (utils/auth.py)
- ✅ Native Streamlit UI (no hacky iframes or redirects)

**Bottom line**: Keep your current approach, just add the Phase 1 features above!
