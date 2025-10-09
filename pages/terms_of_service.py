import streamlit as st

st.set_page_config(page_title="Terms of Service - Rhizome", page_icon="📋")

st.markdown("""
# Terms of Service

**Last Updated:** January 2025

---

## 1. Acceptance of Terms

By accessing and using Rhizome ("Service"), you accept and agree to be bound by these Terms of Service. If you do not agree, do not use the Service.

---

## 2. Medical Disclaimer

**THIS SERVICE IS NOT A MEDICAL DEVICE AND IS NOT INTENDED FOR MEDICAL DIAGNOSIS, TREATMENT, CURE, OR PREVENTION OF ANY DISEASE.**

- Rhizome provides **educational risk assessments** only
- Results are **NOT medical advice** and should not replace consultation with qualified healthcare professionals
- Always consult a licensed physician for medical decisions
- In case of medical emergency, call 911 or your local emergency services immediately

---

## 3. Description of Service

Rhizome analyzes Complete Blood Count (CBC) reports using artificial intelligence to provide:
- **Risk assessment scores** for potential health concerns
- **Educational information** about blood biomarkers
- **Trend analysis** of your health data over time

---

## 4. User Accounts

### 4.1 Registration
- You must provide accurate, current, and complete information
- You must be at least 18 years old to use this Service
- One account per person; do not share credentials

### 4.2 Account Security
- You are responsible for maintaining password confidentiality
- Notify us immediately of unauthorized account access
- We are not liable for losses from unauthorized use of your account

---

## 5. Permitted Use

You may use Rhizome for:
- Personal health education and awareness
- Tracking your own CBC results over time
- Understanding general biomarker patterns

---

## 6. Prohibited Uses

You may NOT:
- Use the Service for medical diagnosis or treatment decisions
- Share another person's medical data without consent
- Attempt to reverse-engineer or copy our AI models
- Use the Service for illegal purposes
- Resell or redistribute Service access
- Upload false, misleading, or fraudulent data
- Interfere with Service security or operation

---

## 7. Privacy and Data

Your privacy is important. Our **[Privacy Policy](/privacy_policy)** explains:
- What data we collect and how we use it
- How we protect your sensitive health information
- Your rights regarding your data (access, deletion, export)

---

## 8. AI Model Limitations

### 8.1 Accuracy
- Our AI model has **99.83% ROC-AUC** on training data but is NOT perfect
- Results may contain false positives or false negatives
- Performance on your specific case may vary

### 8.2 No Guarantees
- We do not guarantee accuracy, completeness, or reliability
- AI models can produce unexpected results
- Always verify findings with medical professionals

---

## 9. Intellectual Property

- All Service content, AI models, and designs are owned by Rhizome
- You retain ownership of your uploaded health data
- You grant us a license to use your data to improve the Service (anonymized)

---

## 10. Liability Disclaimers

### 10.1 No Warranties
**THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED.**

We disclaim all warranties including:
- Merchantability
- Fitness for a particular purpose
- Accuracy or reliability
- Non-infringement

### 10.2 Limitation of Liability
**TO THE MAXIMUM EXTENT PERMITTED BY LAW:**
- We are NOT liable for any indirect, incidental, special, or consequential damages
- Our total liability shall not exceed $50 CAD or the amount you paid us (if any)
- We are NOT liable for health outcomes, medical decisions, or treatment results

---

## 11. Indemnification

You agree to indemnify and hold Rhizome harmless from claims, damages, or expenses arising from:
- Your use of the Service
- Your violation of these Terms
- Your violation of any third-party rights

---

## 12. Termination

We may suspend or terminate your account at any time for:
- Violation of these Terms
- Fraudulent or illegal activity
- Prolonged inactivity

You may delete your account at any time from the dashboard.

---

## 13. Changes to Terms

We reserve the right to modify these Terms at any time. We will notify users of material changes via email. Continued use after changes constitutes acceptance.

---

## 14. Governing Law and Jurisdiction

These Terms are governed by the laws of **Quebec, Canada**.

Any disputes shall be resolved in the courts of **Montreal, Quebec**.

---

## 15. Dispute Resolution

### 15.1 Informal Resolution
Before filing a claim, submit a support request through the in-app help center for informal resolution.

### 15.2 Binding Arbitration
If informal resolution fails, disputes will be resolved through **binding arbitration** in Montreal, Quebec, under Quebec arbitration rules.

### 15.3 Class Action Waiver
**YOU AGREE TO RESOLVE DISPUTES INDIVIDUALLY, NOT AS PART OF A CLASS ACTION.**

---

## 16. Severability

If any provision is found unenforceable, the remaining provisions remain in effect.

---

## 17. Entire Agreement

These Terms constitute the entire agreement between you and Rhizome.

---

## 18. Contact

**Questions about these Terms?**

Use the in-app help center to reach our team. We respond to all requests through your account dashboard.

---

**By using Rhizome, you acknowledge that you have read, understood, and agree to these Terms of Service.**
""")

# Back button
if st.button("← Back to Home"):
    st.switch_page("streamlit_app.py")
