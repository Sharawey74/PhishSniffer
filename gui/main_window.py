"""
Main Streamlit application for phishing email detection.
Replaces the tkinter GUI with a modern web-based interface.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.predict import PhishingPredictor
from storage.history import load_analysis_history, update_analysis_history
from storage.urls import load_suspicious_urls, save_suspicious_urls

class PhishingDetectorApp:
    """Main Streamlit application class."""
    
    def __init__(self):
        self.predictor = PhishingPredictor()
        self.history_file = "data/analysis_history.json"
        self.urls_file = "data/suspicious_urls.json"
        
        # Initialize session state
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        if 'suspicious_urls' not in st.session_state:
            st.session_state.suspicious_urls = load_suspicious_urls(self.urls_file)
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load the trained model."""
        try:
            self.predictor.load_model()
            st.session_state.model_loaded = True
        except Exception as e:
            st.session_state.model_loaded = False
            st.session_state.model_error = str(e)
    
    def run(self):
        """Run the main Streamlit application."""
        st.set_page_config(
            page_title="PhishSniffer - Email Security",
            page_icon="�️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #1f4e79, #2d5aa0);
            padding: 1rem;
            border-radius: 0.5rem;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .risk-high {
            background-color: #ffebee;
            border-left: 5px solid #f44336;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        .risk-low {
            background-color: #e8f5e8;
            border-left: 5px solid #4caf50;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        .metric-card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #dee2e6;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>�️ PhishSniffer - Advanced Email Security</h1>
            <p>AI-Powered Phishing Detection & Analysis Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox(
            "Choose a section:",
            ["📧 Analyze Email", "📊 Reports & History", "🔗 Suspicious URLs", "⚙️ Settings & Model Info"]
        )
        
        # Check model status
        if not st.session_state.get('model_loaded', False):
            st.error(f"⚠️ Model not loaded: {st.session_state.get('model_error', 'Unknown error')}")
            st.info("Please ensure the model is trained and available.")
            return
        
        # Route to different pages
        if page == "📧 Analyze Email":
            self._show_analyze_page()
        elif page == "📊 Reports & History":
            self._show_reports_page()
        elif page == "🔗 Suspicious URLs":
            self._show_urls_page()
        elif page == "⚙️ Settings & Model Info":
            self._show_settings_page()
    
    def _show_analyze_page(self):
        """Show the email analysis page."""
        from gui.analyze_tab import show_analyze_tab
        show_analyze_tab(self)
    
    def _show_reports_page(self):
        """Show the reports and history page."""
        from gui.report_tab import show_report_tab
        show_report_tab(self)
    
    def _show_urls_page(self):
        """Show the suspicious URLs page."""
        from gui.urls_tab import show_urls_tab
        show_urls_tab(self)
    
    def _show_settings_page(self):
        """Show the settings and model info page."""
        from gui.settings_tab import show_settings_tab
        show_settings_tab(self)

def main():
    """Main function to run the Streamlit app."""
    app = PhishingDetectorApp()
    app.run()

if __name__ == "__main__":
    main()