#!/usr/bin/env python3
"""
Streamlit Cloud entry point for PhishSniffer.
This file should be set as the main module in Streamlit Cloud deployment.
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Cloud deployment setup
print("🚀 Initializing PhishSniffer for Streamlit Cloud...")

try:
    # Import and run cloud setup
    from setup_cloud import initialize_for_cloud
    initialize_for_cloud()
except Exception as e:
    print(f"⚠️ Setup warning: {e}")

try:
    # Import and run the main GUI
    from gui.main_window import main
    
    if __name__ == "__main__":
        main()
        
except Exception as e:
    import streamlit as st
    st.error(f"❌ Application Error: {e}")
    st.info("📧 Please contact support if this error persists.")
    
    # Show basic info even if app fails
    st.title("🛡️ PhishSniffer - Email Security Platform")
    st.write("An advanced AI-powered phishing detection system.")
    st.write("**Note:** The application is currently experiencing technical difficulties.")
