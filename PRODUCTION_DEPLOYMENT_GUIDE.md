# 🚀 Production Deployment Guide - Streamlit Community Cloud

**Status:** ⚠️ **Almost Ready** - 2 issues to fix first
**Target:** Streamlit Community Cloud (FREE tier)

---

## ⚠️ **PRE-DEPLOYMENT ISSUES TO FIX**

### Issue 1: Database Files in Git (CRITICAL)
**Problem:** Local SQLite database files are tracked in git
```bash
data/users.db
data/users.backup.db
```

**Why it's bad:** Contains user data, shouldn't be in git
**Already fixed:** Updated `.gitignore` to exclude `*.db`

**ACTION REQUIRED:**
```bash
# Remove from git history
git rm --cached data/users.db data/users.backup.db

# Commit the change
git add .gitignore
git commit -m "Remove database files from git tracking"
```

### Issue 2: Verify App Runs Locally (RECOMMENDED)
**ACTION REQUIRED:**
```bash
cd streamlit_app
streamlit run streamlit_app.py

# Test these flows:
# 1. Sign up new user
# 2. Sign in
# 3. Fill questionnaire
# 4. Upload CBC PDF
# 5. View results
```

---

## ✅ **PRODUCTION READINESS STATUS**

### What's Working:
- ✅ Supabase database connected (Transaction Pooler, IPv4)
- ✅ 3 tables created with correct schema (users, questionnaires, cbc_results)
- ✅ All indexes in place for performance
- ✅ Quebec Health Booklet PDF support ready
- ✅ ML pipeline with imputation support
- ✅ requirements.txt has all dependencies
- ✅ secrets.toml properly gitignored
- ✅ Database auto-detection (SQLite local, PostgreSQL production)

### What Needs Attention:
- ⚠️  Database files in git (fix above)
- ⚠️  Local testing recommended
- ⚠️  No README.md for users (optional but nice)

---

## 📋 **DEPLOYMENT CHECKLIST**

### Pre-Deployment (DO THESE FIRST)

- [ ] **Remove database files from git**
  ```bash
  git rm --cached data/users.db data/users.backup.db
  git add .gitignore
  git commit -m "chore: remove database files from git tracking"
  ```

- [ ] **Test app locally with Supabase**
  ```bash
  streamlit run streamlit_app.py
  # Verify: registration, login, questionnaire, CBC upload
  ```

- [ ] **Commit all changes**
  ```bash
  git status  # Review what's changed
  git add .
  git commit -m "feat: production-ready Supabase integration"
  ```

- [ ] **Push to GitHub**
  ```bash
  git push origin main
  ```

### Deployment Steps

- [ ] **1. Go to Streamlit Community Cloud**
  - Visit: https://share.streamlit.io
  - Click "New app" or "Deploy an app"

- [ ] **2. Connect GitHub**
  - Authorize Streamlit to access your repos
  - Select repository: `shayshay42/rizome_biotech_webapp` (or your repo name)
  - Branch: `main`
  - Main file path: `streamlit_app/streamlit_app.py`

- [ ] **3. Add Secrets**
  Click "Advanced settings" → "Secrets" and paste:
  ```toml
  [supabase]
  host = "aws-1-ca-central-1.pooler.supabase.com"
  port = "6543"
  user = "postgres.kqzmwzosluljckadthup"
  password = "ZnJJSIChnpkAmtcS"
  database = "postgres"

  [general]
  environment = "production"
  ```

- [ ] **4. Deploy!**
  - Click "Deploy"
  - Wait 2-3 minutes for build
  - App will be live at `https://[your-app-name].streamlit.app`

### Post-Deployment

- [ ] **Test production app**
  - Register new user
  - Upload Quebec Health Booklet PDF
  - Verify data saves to Supabase
  - Check ML predictions work

- [ ] **Monitor first users**
  - Check Supabase dashboard for data
  - Review Streamlit Cloud logs for errors

- [ ] **Optional: Custom domain**
  - Add CNAME record pointing to your app
  - Configure in Streamlit Cloud settings

---

## 🔧 **DEPLOYMENT COMMANDS (COPY-PASTE)**

### Step 1: Clean Up Git
```bash
# Make sure you're in the streamlit_app directory
cd /Users/shayanhajhashemi/Documents/Rhizome/streamlit_app

# Remove database files from git
git rm --cached data/users.db data/users.backup.db

# Add the updated .gitignore
git add .gitignore

# Commit
git commit -m "chore: remove database files and update gitignore"

# Push
git push origin main
```

### Step 2: Test Locally (Optional but Recommended)
```bash
# Run the app
streamlit run streamlit_app.py

# In browser, test:
# 1. Sign up: username "testuser", email "test@test.com", password "test123"
# 2. Sign in with those credentials
# 3. Fill out questionnaire
# 4. Try uploading a CBC PDF (if you have one)
# 5. Check Supabase dashboard - data should appear!
```

### Step 3: Deploy to Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click "New app"
3. Connect GitHub repo
4. Set:
   - Repository: `[your-username]/[your-repo-name]`
   - Branch: `main`
   - Main file: `streamlit_app/streamlit_app.py`
5. Click "Advanced settings"
6. Paste secrets (from section above)
7. Click "Deploy"!

---

## 🔐 **SECURITY CHECKLIST**

### Already Secure:
- ✅ Passwords hashed with bcrypt
- ✅ SQL injection protection (parameterized queries)
- ✅ Secrets not in git
- ✅ Environment-based config (dev vs prod)
- ✅ Foreign key constraints

### Future Enhancements (Post-Launch):
- [ ] Add rate limiting for API endpoints
- [ ] Enable Supabase Row Level Security (RLS)
- [ ] Add session timeout (currently infinite)
- [ ] Implement password reset flow
- [ ] Add email verification
- [ ] Set up monitoring/alerts

---

## 📊 **PRODUCTION ARCHITECTURE**

```
User Browser
    ↓
Streamlit Community Cloud (FREE)
    ↓
Supabase PostgreSQL (Canada Central, FREE tier)
    - Users table (authentication)
    - Questionnaires table (health data)
    - CBC Results table (lab data + ML predictions)
```

### Resource Limits (FREE Tier):
**Streamlit Cloud:**
- 1 GB RAM
- 1 CPU core
- Sleeps after inactivity (wakes on visit)
- Unlimited users

**Supabase:**
- 500 MB database
- 2 GB bandwidth/month
- 50 MB file storage
- Connection pooling included

**Your App's Footprint:**
- Database: ~1 KB per user + ~5 KB per CBC result
- Expected usage: Can handle 1000+ users easily on FREE tier

---

## 🐛 **TROUBLESHOOTING**

### Common Deployment Issues

**"Module not found" errors:**
- Check `requirements.txt` has all packages
- Verify package names are correct
- Add missing packages and redeploy

**Database connection fails:**
- Verify secrets are added to Streamlit Cloud
- Check Supabase project is active (not paused)
- Test connection locally first

**App keeps reloading:**
- Check for infinite loops in code
- Review Streamlit Cloud logs
- Verify session state initialization

**Quebec PDF extraction fails:**
- Check file upload size limit (200 MB max)
- Verify PyPDF2 is in requirements.txt
- Test with known good PDF locally first

### Where to Get Help

- **Streamlit docs:** https://docs.streamlit.io
- **Supabase docs:** https://supabase.com/docs
- **App logs:** Streamlit Cloud dashboard → "Manage app" → "Logs"
- **Database:** Supabase dashboard → "Table Editor"

---

## 📈 **MONITORING & ANALYTICS**

### What to Monitor:

1. **Streamlit Cloud Dashboard:**
   - App status (running/sleeping/crashed)
   - Resource usage (RAM, CPU)
   - Error logs
   - Deployment history

2. **Supabase Dashboard:**
   - Database size
   - Query performance
   - Connection count
   - Storage usage

3. **User Metrics (Track Manually):**
   - Daily active users: `SELECT COUNT(DISTINCT user_id) FROM cbc_results WHERE created_at > NOW() - INTERVAL '1 day'`
   - Total registrations: `SELECT COUNT(*) FROM users`
   - Quebec PDFs processed: `SELECT COUNT(*) FROM cbc_results WHERE file_format = 'quebec_health_booklet'`

---

## 🎯 **SUCCESS METRICS**

### App is successfully deployed if:
- ✅ Users can register and login
- ✅ Questionnaires save to Supabase
- ✅ CBC PDFs upload and extract correctly
- ✅ ML predictions display with confidence scores
- ✅ Data persists across app restarts
- ✅ Quebec Health Booklet PDFs work with imputation warnings

### Performance targets:
- Page load: < 3 seconds
- PDF processing: < 10 seconds
- Database queries: < 500ms
- Uptime: > 99% (Streamlit Cloud guarantee)

---

## 🚦 **DEPLOYMENT STATUS**

### Current State: ⚠️ **ALMOST READY**

**Before deploying:**
1. ❌ Remove database files from git
2. ⚠️  Test locally (recommended)
3. ✅ Everything else is ready!

**After fixes:**
1. Run git commands above
2. Test locally
3. Deploy to Streamlit Cloud
4. Add secrets
5. Go live!

**Estimated time to production:** 15-30 minutes (after git cleanup)

---

## 📝 **DEPLOYMENT NOTES**

### What Happens During Deployment:
1. Streamlit Cloud clones your repo
2. Installs packages from requirements.txt (2-3 min)
3. Loads secrets from Cloud config
4. Runs streamlit_app.py
5. App becomes available at public URL

### Auto-Deployment:
- Every git push to `main` triggers redeploy
- Can disable in Streamlit Cloud settings
- Can set up dev/prod branches

### Costs:
- **Development:** $0 (FREE tier)
- **Production (current setup):** $0 (FREE tier)
- **Scale beyond free tier:**
  - Streamlit: $20/month (Team plan)
  - Supabase: $25/month (Pro plan)

---

## ✅ **FINAL PRE-FLIGHT CHECK**

Run this before deploying:

```bash
# 1. Are database files removed from git?
git ls-files | grep '\.db$'
# Expected output: (nothing) ✅

# 2. Is gitignore updated?
grep '*.db' .gitignore
# Expected output: *.db ✅

# 3. Can we connect to Supabase?
python -c "import toml; import psycopg2; config = toml.load('.streamlit/secrets.toml')['supabase']; conn = psycopg2.connect(host=config['host'], port=int(config['port']), database=config['database'], user=config['user'], password=config['password']); print('✅ Supabase connected')"

# 4. Are all files committed?
git status
# Expected: nothing to commit ✅

# If all checks pass: READY TO DEPLOY! 🚀
```

---

**🎊 Once deployed, your app will be live at:**
`https://[your-app-name].streamlit.app`

Share with users and start collecting CBC data! 🧬
