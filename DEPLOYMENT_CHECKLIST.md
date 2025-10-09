# Deployment Checklist: Password Reset Feature

Use this checklist to deploy the password reset feature to production.

---

## ✅ Pre-Deployment (Local Testing)

- [ ] **Run automated tests**
  ```bash
  cd /Users/shayanhajhashemi/Documents/Rhizome/streamlit_app
  python test_password_reset.py
  ```
  - [ ] All tests pass

- [ ] **Test locally with Streamlit**
  ```bash
  streamlit run streamlit_app.py
  ```
  - [ ] App starts without errors
  - [ ] Landing page shows 3 tabs (Sign In, Sign Up, Forgot Password)
  - [ ] Sign in works with test account
  - [ ] Sign up shows password requirements
  - [ ] Forgot Password tab displays correctly

- [ ] **Test password reset flow locally**
  - [ ] Enter your real email in Forgot Password tab
  - [ ] Click "Send Reset Link"
  - [ ] Check email received (check spam folder too)
  - [ ] Click reset link in email
  - [ ] App shows password update page
  - [ ] Enter new password
  - [ ] Successfully updates password
  - [ ] Can sign in with new password

---

## 🔧 Configuration Updates

- [ ] **Update redirect URL in code**
  - [ ] Open `utils/auth.py`
  - [ ] Go to line ~167 in `request_password_reset()` function
  - [ ] Change `"redirect_to": "https://your-app-url.streamlit.app/"`
  - [ ] To your actual production URL
  - [ ] Save file

- [ ] **Configure Supabase Dashboard**
  - [ ] Go to https://supabase.com/dashboard
  - [ ] Select your project: `kqzmwzosluljckadthup`
  - [ ] Navigate to **Authentication** → **URL Configuration**
  
  **Site URL:**
  - [ ] Set to your production URL (e.g., `https://rhizome-cbc.streamlit.app`)
  
  **Redirect URLs (add both):**
  - [ ] `http://localhost:8501/*` (for local testing)
  - [ ] `https://your-app.streamlit.app/*` (your production URL)
  
  - [ ] Click **Save**

- [ ] **Verify Email Templates (optional)**
  - [ ] Go to **Authentication** → **Email Templates**
  - [ ] Review "Reset Password" template
  - [ ] Customize if desired (or use default)

---

## 🚀 Deployment to Streamlit Cloud

- [ ] **Push code to GitHub**
  ```bash
  cd /Users/shayanhajhashemi/Documents/Rhizome/streamlit_app
  git add .
  git commit -m "Add password reset and improved error messages"
  git push
  ```

- [ ] **Deploy to Streamlit Cloud**
  - [ ] Go to https://share.streamlit.io
  - [ ] Select your app (or create new deployment)
  - [ ] Point to `streamlit_app/streamlit_app.py`
  - [ ] Verify secrets are configured:
    ```toml
    [supabase]
    url = "https://kqzmwzosluljckadthup.supabase.co"
    key = "YOUR_ANON_KEY_HERE"
    ```
  - [ ] Click **Deploy**

- [ ] **Wait for deployment**
  - [ ] App builds successfully
  - [ ] No deployment errors
  - [ ] App is accessible at production URL

---

## 🧪 Production Testing

- [ ] **Test basic auth**
  - [ ] Sign in with existing account
  - [ ] Sign out
  - [ ] Sign up with new test account
  - [ ] Verify error messages are friendly

- [ ] **Test password reset in production**
  - [ ] Go to Forgot Password tab
  - [ ] Enter real email address
  - [ ] Click "Send Reset Link"
  - [ ] Verify success message appears
  - [ ] Check email inbox (and spam)
  - [ ] Email received within 1-2 minutes
  - [ ] Click reset link
  - [ ] Redirects to production app
  - [ ] Shows password update page
  - [ ] Enter new password
  - [ ] Click "Update Password"
  - [ ] Success message appears
  - [ ] Redirects to sign in
  - [ ] Can sign in with new password

- [ ] **Test error scenarios**
  - [ ] Try wrong password → See friendly error message
  - [ ] Try reset with invalid email format → See validation error
  - [ ] Request multiple resets rapidly → Verify rate limiting

---

## 📊 Monitoring

- [ ] **Check Supabase Logs**
  - [ ] Go to Supabase Dashboard
  - [ ] Navigate to **Authentication** → **Logs**
  - [ ] Verify auth events are logging correctly
  - [ ] Check for any error patterns

- [ ] **Monitor Email Delivery**
  - [ ] Track password reset emails sent
  - [ ] Check bounce rates
  - [ ] Verify users receive emails promptly

- [ ] **User Feedback**
  - [ ] Monitor for user reports of issues
  - [ ] Check if password reset flow is intuitive
  - [ ] Gather feedback on error messages

---

## 🔒 Security Verification

- [ ] **Password Security**
  - [ ] Minimum 6 characters enforced ✓
  - [ ] Passwords never logged or displayed ✓
  - [ ] Supabase handles hashing ✓

- [ ] **Email Security**
  - [ ] Reset emails don't reveal account existence ✓
  - [ ] Links expire after 1 hour ✓
  - [ ] Links are one-time use ✓

- [ ] **Rate Limiting**
  - [ ] Supabase rate limiting active ✓
  - [ ] Error messages don't reveal system details ✓

---

## 📈 Optional Enhancements

- [ ] **Custom SMTP Provider** (for higher email limits)
  - [ ] Choose provider (SendGrid, Mailgun, AWS SES)
  - [ ] Create account and get SMTP credentials
  - [ ] Configure in Supabase: **Settings** → **Auth** → **SMTP Settings**
  - [ ] Test email delivery
  - [ ] Higher rate limits now available

- [ ] **Email Template Customization**
  - [ ] Customize reset email with your branding
  - [ ] Add company logo
  - [ ] Personalize messaging
  - [ ] Test customized template

- [ ] **Analytics Tracking**
  - [ ] Track password reset requests
  - [ ] Monitor completion rate
  - [ ] Identify common issues

---

## 🎉 Launch Checklist

- [ ] All automated tests pass ✓
- [ ] Local testing complete ✓
- [ ] Configuration updated ✓
- [ ] Code deployed to production ✓
- [ ] Production testing complete ✓
- [ ] Error monitoring in place ✓
- [ ] Documentation updated ✓

---

## 📝 Post-Deployment

- [ ] **Document Production URL**
  - Where: `________________________`
  - Date deployed: `________________________`

- [ ] **Note Any Issues**
  - Issue 1: `________________________`
  - Issue 2: `________________________`

- [ ] **Schedule Follow-up**
  - Review analytics in 1 week
  - Check user feedback
  - Plan next enhancements

---

## 🆘 Troubleshooting

If something goes wrong, see:
- `PASSWORD_RESET_IMPLEMENTATION.md` → Troubleshooting section
- `PASSWORD_RESET_QUICKSTART.md` → Quick fixes
- Supabase Dashboard → Authentication → Logs

---

## ✅ Success Criteria

Your deployment is successful when:
- ✅ Users can reset forgotten passwords
- ✅ Reset emails arrive within 2 minutes
- ✅ Reset links work correctly
- ✅ Error messages are clear and helpful
- ✅ No auth-related errors in logs

---

**Ready to deploy? Start with the Pre-Deployment section!** 🚀
