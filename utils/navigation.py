"""
Navigation utilities for Rhizome CBC Analysis App
"""

import streamlit as st
from streamlit_option_menu import option_menu

def setup_navigation():
    """Setup sidebar navigation menu"""
    
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.username}! 👋")
        
        # Navigation menu
        options = ["Dashboard", "Questionnaire", "About Us", "Settings"]
        try:
            current_index = options.index(st.session_state.current_page)
        except (ValueError, AttributeError):
            current_index = 0
            
        selected = option_menu(
            menu_title="Navigation",
            options=options,
            icons=["house", "clipboard-data", "people", "gear"],
            menu_icon="cast",
            default_index=current_index,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#2E86AB", "font-size": "18px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#2E86AB"},
            }
        )
        
        st.markdown("---")
        
        # User status info
        if hasattr(st.session_state, 'user_data') and st.session_state.user_data:
            if st.session_state.user_data.get('has_questionnaire'):
                st.markdown("**Assessment Status:** ✅ Complete")
            else:
                st.markdown("**Assessment Status:** ⏳ Pending")
            
            if st.session_state.user_data.get('has_cbc_results'):
                cbc_data = st.session_state.user_data.get('cbc_results')
                if cbc_data:
                    st.markdown(f"**Last Report:** {cbc_data.get('filename', 'Unknown')}")
                    st.markdown(f"**Risk Score:** {cbc_data.get('risk_score', 'N/A')}")
        
        st.markdown("---")
        
        # Logout button
    if st.button("🚪 Logout", type="secondary", width='stretch'):
            from utils.auth import logout
            logout()
    
    return selected