# Deploying Streamlit App with Private GitHub Repository

## Yes, You Can Keep Your Repo Private! 🔒

Streamlit Cloud **fully supports private GitHub repositories**. Your code stays private while your app runs publicly.

---

## 🚀 Deployment Steps

### 1. Push Your Code to GitHub (Private Repo)

```bash
# If you haven't initialized git yet
cd /Users/shayanhajhashemi/Documents/Rhizome/streamlit_app
git init

# Create .gitignore
cat > .gitignore << EOF
__pycache__/
*.pyc
*.pyo
.env
.venv/
venv/
*.sqlite
*.db
.DS_Store
*.log
EOF

# Add and commit
git add .
git commit -m "Initial commit: Rhizome CBC Analysis Platform"

# Create private repo on GitHub (via GitHub.com or CLI)
# Option 1: Via GitHub.com
#   - Go to github.com/new
#   - Name: rhizome-app (or whatever you prefer)
#   - ✅ Check "Private"
#   - Create repository

# Option 2: Via GitHub CLI
gh repo create rhizome-app --private --source=. --push
```

### 2. Connect Streamlit Cloud to Private GitHub

**Go to:** https://share.streamlit.io/

1. **Sign in with GitHub**
   - Click "Sign in"
   - Choose "Continue with GitHub"
   - Authorize Streamlit Cloud

2. **Grant Access to Private Repos**
   - Streamlit will ask for permission to access private repos
   - Click "Authorize streamlit"
   - ✅ This allows Streamlit to read your private repo (but NOT make it public)

3. **Deploy Your App**
   - Click "New app"
   - Repository: Select your private repo (e.g., `yourusername/rhizome-app`)
   - Branch: `main` (or `master`)
   - Main file path: `streamlit_app.py`
   - Click "Deploy!"

### 3. Configure Environment Variables (Secrets)

Your Supabase credentials should NEVER be in code. Use Streamlit Secrets:

1. In Streamlit Cloud dashboard, click your app
2. Click "⚙️ Settings" → "Secrets"
3. Add your secrets in TOML format:

```toml
# .streamlit/secrets.toml format
[supabase]
url = "https://your-project.supabase.co"
key = "your-anon-key-here"

[database]
connection_string = "postgresql://user:password@host:5432/dbname"
```

4. Update your code to read from secrets:

```python
# utils/supabase_client.py
import streamlit as st

# Use secrets if available (production), otherwise use .env (local dev)
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
except:
    # Fallback for local development
    from dotenv import load_dotenv
    load_dotenv()
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
```

---

## 🔒 Privacy Breakdown

### What Stays Private:
- ✅ Your GitHub repository code
- ✅ Git history and commits
- ✅ Contributors and collaborators
- ✅ Issues and pull requests
- ✅ Secrets/environment variables

### What Becomes Public:
- 🌐 The running app (at your-app.streamlit.app)
- 🌐 Users can USE the app
- ❌ Users CANNOT see the code
- ❌ Users CANNOT access your database directly

---

## 📋 Required Files for Deployment

### 1. `requirements.txt`

Create in your repo root:

```txt
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
supabase>=2.0.0
python-dotenv>=1.0.0
autogluon.tabular>=1.0.0
xgboost>=2.0.0
```

### 2. `.streamlit/config.toml` (Optional)

```toml
[theme]
primaryColor = "#2E86AB"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true
```

### 3. `.gitignore`

```
__pycache__/
*.pyc
*.pyo
.env
.streamlit/secrets.toml
.venv/
venv/
*.sqlite
*.db
.DS_Store
*.log
```

---

## 🔧 Deployment Checklist

- [ ] Code pushed to **private** GitHub repo
- [ ] `requirements.txt` includes all dependencies
- [ ] Streamlit Cloud authorized to access private repos
- [ ] Secrets configured in Streamlit Cloud (not in code!)
- [ ] Supabase URL whitelisted for your Streamlit app domain
- [ ] Database RLS policies configured
- [ ] App tested locally with `streamlit run streamlit_app.py`
- [ ] `.gitignore` prevents sensitive files from being committed
- [ ] Environment variables using `st.secrets` (not hardcoded)

---

## 🌐 Accessing Your Deployed App

After deployment, your app will be available at:

```
https://your-app-name.streamlit.app
```

Or with custom domain:
```
https://rhizome.yourdomain.com  # (requires Streamlit Teams plan)
```

### Sharing Options:
- **Public URL**: Anyone with the link can access
- **Password Protection**: Add authentication (what you already have!)
- **Private**: Streamlit Teams plan offers IP whitelisting

---

## 🔐 Security Best Practices

### 1. Never Commit Secrets
```bash
# Check before committing
git status
git diff

# If you accidentally committed secrets:
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

### 2. Use Environment Variables
```python
# ❌ BAD
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# ✅ GOOD
SUPABASE_KEY = st.secrets["supabase"]["key"]
```

### 3. Enable RLS on Supabase
```sql
-- Ensure all tables have RLS enabled
ALTER TABLE cbc_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE questionnaires ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Create policies (users can only see their own data)
CREATE POLICY "Users can view own cbc_results"
  ON cbc_results FOR SELECT
  USING (auth.uid() = user_id);
```

### 4. Whitelist Your App Domain in Supabase
In Supabase Dashboard:
1. Settings → API
2. "Site URL" → Add `https://your-app.streamlit.app`
3. "Redirect URLs" → Add `https://your-app.streamlit.app/**`

---

## 🐛 Troubleshooting

### App Won't Start
```
Check:
- requirements.txt has all dependencies
- Python version compatible (3.9-3.11 recommended)
- No syntax errors (test locally first)
```

### Database Connection Fails
```
Check:
- Secrets configured correctly in Streamlit Cloud
- Supabase URL whitelisted
- RLS policies allow access
- API keys are valid (anon key, not service key)
```

### Import Errors
```
# Add missing packages to requirements.txt
streamlit run streamlit_app.py  # Test locally
pip freeze > requirements.txt   # Update requirements
```

---

## 📈 Monitoring Your App

Streamlit Cloud provides:
- 📊 **Analytics**: Visitors, page views, sessions
- 🚨 **Logs**: Real-time app logs and errors
- 🔄 **Reboot**: Restart app if needed
- 📦 **Deployments**: History of deployments

Access via: https://share.streamlit.io/

---

## 💰 Pricing

### Streamlit Community Cloud (FREE)
- ✅ Unlimited public apps
- ✅ 1 private app
- ✅ Private GitHub repos supported
- ✅ 1 GB RAM per app
- ✅ Community support

### Streamlit Teams ($250/month)
- ✅ Unlimited private apps
- ✅ Custom domains
- ✅ SSO authentication
- ✅ Priority support
- ✅ More resources

**For your use case:** Community Cloud is perfect! ✅

---

## 🎉 Summary

**Question:** "Can I keep my source repo private while getting Streamlit to work online?"

**Answer:** YES! 🎉

1. Push code to **private** GitHub repo
2. Connect Streamlit Cloud to your GitHub
3. Grant access to private repos (one-time)
4. Deploy from private repo
5. App is public, code stays private ✅

**Your code is safe, your app is live!** 🚀
