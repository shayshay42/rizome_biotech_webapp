# Hosting Legal Documents on Streamlit

## Summary

✅ **Complete!** Your Terms of Service and Privacy Policy are now hosted directly on Streamlit Cloud as part of your app - no external GitHub links or separate hosting needed.

---

## What Changed

### Before:
- Terms and Privacy were markdown files in repo root
- Links pointed to GitHub URLs (`https://github.com/yourusername/...`)
- Required public GitHub repo or separate hosting

### After:
- Terms and Privacy are Streamlit pages in `streamlit_app/pages/`
- Navigation uses `st.switch_page()` - entirely within your app
- Fully self-contained, works with private repos
- Same styling and navigation as rest of app

---

## File Structure

```
streamlit_app/
├── streamlit_app.py              # Main app
└── pages/
    ├── terms_of_service.py       # Terms page (full document)
    └── privacy_policy.py         # Privacy page (full document)
```

---

## How Users Access Legal Docs

### 1. From Landing Page (About Us Tab)
No login required! Two buttons:
- 📄 **Terms of Service** button → navigates to terms page
- 🔒 **Privacy Policy** button → navigates to privacy page

### 2. From Sign Up Form
Expander shows:
- Key points summary
- Two buttons to view full documents
- Required acceptance checkbox

### 3. Navigation
Each legal page has:
- Full document content (nicely formatted Markdown)
- **"← Back to Home"** button at bottom

---

## Benefits

### 🔒 Privacy
- Legal docs not exposed in public GitHub repo
- Only accessible through your Streamlit app
- Complete control over visibility

### 🎨 Consistency
- Same Streamlit styling as rest of app
- Integrated navigation
- Professional appearance

### 📱 Maintenance
- Update by editing page files
- Deploy changes with your app
- Always in sync with app version

### ⚡ Performance
- Fast page loads (Streamlit native)
- No external requests
- Works offline (in development)

---

## Optional Tweaks

The legal pages no longer contain placeholder contact details. Everything points users to the in-app help center, so deployment-ready defaults are already in place.

If you’d like to adjust anything before launch, you can optionally:

- Refresh the **Last Updated / Effective Date** labels when you make significant changes.
- Update the company name reference if you prefer a different public-facing name.
- Add any supplemental guidance inside your help center (handled outside these pages).

---

## Testing

### Local Testing:
```bash
cd streamlit_app
streamlit run streamlit_app.py
```

Then test:
1. ✅ Click "About Us" tab → Legal buttons work
2. ✅ Click "Sign Up" tab → Expander buttons work
3. ✅ Try signup without checkbox → Shows error
4. ✅ Legal pages → "Back to Home" button works

### On Streamlit Cloud:
Same navigation will work automatically!

---

## Deployment

### For Streamlit Cloud:
1. Push all files to GitHub (repo can be **private**)
2. Deploy via Streamlit Cloud
3. Legal pages automatically available at:
   - `https://yourapp.streamlit.app/terms_of_service`
   - `https://yourapp.streamlit.app/privacy_policy`

### No Extra Configuration Needed!
Streamlit automatically:
- Discovers pages in `pages/` folder
- Creates navigation structure
- Handles page routing

---

## Optional: Database Logging

To log terms acceptances, add this to your database:

```sql
CREATE TABLE terms_acceptances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    terms_version TEXT NOT NULL,
    privacy_version TEXT NOT NULL,
    accepted_at TIMESTAMP DEFAULT NOW(),
    ip_address TEXT,
    user_agent TEXT
);

-- Enable RLS
ALTER TABLE terms_acceptances ENABLE ROW LEVEL SECURITY;

-- Users can only see their own acceptances
CREATE POLICY "Users can view own acceptances"
    ON terms_acceptances FOR SELECT
    USING (auth.uid() = user_id);

-- Insert policy for new acceptances
CREATE POLICY "Users can insert own acceptances"
    ON terms_acceptances FOR INSERT
    WITH CHECK (auth.uid() = user_id);
```

Then in `utils/auth.py`, when registering:
```python
# After successful registration
supabase.table('terms_acceptances').insert({
    'user_id': user_id,
    'terms_version': 'v1.0',
    'privacy_version': 'v1.0'
}).execute()
```

---

## Questions?

The legal documents are now fully integrated into your Streamlit app and ready to use! No external hosting, no GitHub links, completely self-contained.

**Next Steps:**
1. Update effective dates when you're ready to launch (optional)
2. Test locally
3. Deploy to Streamlit Cloud
4. (Optional) Get legal review before launch
