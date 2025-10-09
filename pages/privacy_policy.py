import streamlit as st

st.set_page_config(page_title="Privacy Policy - Rhizome", page_icon="🔒")

st.markdown("""
# Privacy Policy

**Last Updated:** January 2025

**Effective Date:** January 2025

---

## Our Commitment to Your Privacy

At Rhizome, we take your privacy seriously. This Privacy Policy explains how we collect, use, protect, and share your information when you use our Service.

**We DO NOT sell your personal data. Period.**

---

## 1. Information We Collect

### 1.1 Account Information
When you create an account, we collect:
- Email address (required)
- Username/display name (optional)
- Password (encrypted, we cannot see it)
- Account creation date

### 1.2 Health Information
When you use our Service, we collect:
- **Complete Blood Count (CBC) data** including:
  - White Blood Cell count (WBC)
  - Hemoglobin (HGB)
  - Mean Corpuscular Volume (MCV)
  - Platelet count (PLT)
  - Red Cell Distribution Width (RDW)
  - Monocyte count (MONO)
  - Neutrophil-to-Lymphocyte Ratio (NLR)
- Test dates
- Uploaded PDF/image files of CBC reports (if applicable)

### 1.3 Usage Information
We automatically collect:
- Login times and frequency
- Pages visited within the app
- Device type and browser
- IP address (for security)

### 1.4 Optional Information
You may choose to provide:
- Demographic information (age, location)
- Health history questionnaire responses

---

## 2. How We Use Your Information

### 2.1 Primary Purposes
- **Risk Assessment**: Analyze CBC data using our AI model
- **Personalization**: Show your historical trends and patterns
- **Account Management**: Authenticate you and maintain your account
- **Communication**: Send important updates about your account or the Service

### 2.2 Research and Improvement
- **Model Training**: Improve AI accuracy (anonymized and aggregated only)
- **Service Enhancement**: Understand usage patterns to improve features
- **Quality Assurance**: Test and validate model performance

### 2.3 Legal Compliance
- Comply with applicable laws and regulations
- Respond to legal requests (court orders, subpoenas)
- Prevent fraud and abuse

---

## 3. How We Share Your Information

### 3.1 We DO NOT Sell Your Data
**We will never sell, rent, or trade your personal or health information.**

### 3.2 Service Providers
We share data with trusted third parties who help us operate:
- **Supabase**: Database hosting and authentication
- **Streamlit Cloud**: Application hosting
- **Email Service**: Account notifications (if implemented)

All providers are bound by strict confidentiality agreements.

### 3.3 Legal Requirements
We may disclose information when required by law or to:
- Comply with court orders or legal processes
- Protect our rights or property
- Prevent harm or illegal activity

### 3.4 Aggregated Data
We may share **anonymized, aggregated statistics** (e.g., "50% of users have X biomarker pattern") with:
- Researchers
- Public health organizations
- Academic institutions

This data **cannot identify you personally**.

---

## 4. Data Security

### 4.1 Technical Measures
- **Encryption in transit**: HTTPS/TLS for all data transmission
- **Encryption at rest**: Database encryption for stored data
- **Secure authentication**: Industry-standard Supabase Auth
- **Access controls**: Role-based access and Row-Level Security (RLS)

### 4.2 Organizational Measures
- Regular security audits
- Employee training on data protection
- Limited access to personal data (need-to-know basis)

### 4.3 No Perfect Security
While we implement strong security measures, **no system is 100% secure**. Use strong passwords and report suspicious activity immediately.

---

## 5. Your Rights and Choices

### 5.1 Access
You can view all your data in the dashboard at any time.

### 5.2 Correction
Update your account information directly in the app settings.

### 5.3 Deletion (Right to be Forgotten)
You can delete your account and all associated data:
- Go to Settings → Delete Account
- Or submit a request through the in-app help center

**Note**: Deletion is permanent and cannot be undone. Anonymized data used in research cannot be removed.

### 5.4 Data Export
Request a copy of your data in machine-readable format:
- Submit a data export request from the in-app help center
- We will respond within 30 days

### 5.5 Opt-Out of Research Use
Send an opt-out request through the in-app help center to stop having your anonymized data used for model improvement.

---

## 6. Data Retention

- **Active accounts**: Data retained indefinitely while account is active
- **Inactive accounts**: May be deleted after 24 months of inactivity (with notice)
- **Deleted accounts**: Personal data deleted within 30 days
- **Anonymized research data**: Retained permanently (cannot identify you)
- **Legal hold**: Data retained longer if required by law

---

## 7. Children's Privacy

Rhizome is **NOT intended for users under 18**. We do not knowingly collect data from minors. If we discover such data, we will delete it immediately.

---

## 8. International Users

### 8.1 Data Location
Your data is stored on servers located in **Canada** (or other regions as specified by Supabase/Streamlit).

### 8.2 Cross-Border Transfers
If you access Rhizome from outside Canada, your data may be transferred internationally. By using the Service, you consent to this transfer.

---

## 9. Cookies and Tracking

We use **essential cookies only** for:
- Session management (keeping you logged in)
- Security features

We do **NOT** use advertising or tracking cookies.

---

## 10. Third-Party Links

Our Service may contain links to external websites. We are not responsible for their privacy practices. Review their policies before sharing data.

---

## 11. Changes to This Policy

We may update this Privacy Policy from time to time. We will:
- Notify you via email of material changes
- Update the "Last Updated" date
- Provide 30 days' notice before changes take effect

Continued use after changes constitutes acceptance.

---

## 12. Jurisdiction-Specific Rights

### 12.1 Canada (PIPEDA Compliance)
Canadian users have rights under PIPEDA including:
- Right to access personal information
- Right to challenge accuracy
- Right to withdraw consent (where applicable)
- Right to file a complaint with the Privacy Commissioner of Canada

### 12.2 European Union (GDPR)
EU users have additional rights including:
- Right to data portability
- Right to restrict processing
- Right to object to processing
- Right to lodge a complaint with supervisory authority

### 12.3 California (CCPA)
California residents have rights including:
- Right to know what data is collected
- Right to delete personal information
- Right to opt-out of data sales (**Note**: We do not sell data)
- Right to non-discrimination for exercising CCPA rights

---

## 13. Data Protection Officer

For privacy-related inquiries, contact our Data Protection Officer via the in-app help center. All requests are tracked and addressed through your account dashboard.

---

## 14. Complaints and Disputes

If you have concerns about our privacy practices:

1. **Contact us first**: submit a privacy ticket through the in-app help center
2. **Regulatory authorities**: You may file a complaint with:
   - **Canada**: Privacy Commissioner of Canada (priv.gc.ca)
   - **EU**: Your local Data Protection Authority
   - **California**: California Attorney General

---

## 15. Contact Information

**Questions about this Privacy Policy?**

Support is available through the in-app help center located in the dashboard.

---

**By using Rhizome, you acknowledge that you have read and understood this Privacy Policy.**
""")

# Back button
if st.button("← Back to Home"):
    st.switch_page("streamlit_app.py")
