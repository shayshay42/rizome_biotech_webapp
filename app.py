#!/usr/bin/env python3
"""
Rhizome CBC Analysis Web Application
Main Streamlit application entry point with multi-page navigation
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.auth import init_auth, check_authentication
from utils.navigation import setup_navigation
from pages import landing, questionnaire, profile, about

# Page configuration
st.set_page_config(
    page_title="Rhizome CBC Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    
    # Initialize authentication system
    init_auth()
    
    # Check if user is authenticated
    if not check_authentication():
        landing.show()
        return
    
    # Setup navigation for authenticated users
    selected_page = setup_navigation()
    
    # Route to appropriate page
    if selected_page == "Dashboard":
        profile.show()
    elif selected_page == "Questionnaire":
        questionnaire.show()
    elif selected_page == "About Us":
        about.show()
    else:
        profile.show()  # Default to profile/dashboard

if __name__ == "__main__":
    main()