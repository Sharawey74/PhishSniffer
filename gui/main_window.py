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
            page_icon="🛡️",
            layout="wide",
            initial_sidebar_state="collapsed"  # Collapse sidebar since we're using tabs
        )
        
        # Enhanced CSS for modern dashboard with glowing blue background and glassmorphism
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles with Glowing Blue Background */
        .stApp {
            font-family: 'Inter', sans-serif;
            background: radial-gradient(circle at center, #004cc5 0%, #002a6b 50%, #001433 100%);
            min-height: 100vh;
            position: relative;
        }
        
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 30%, rgba(0, 76, 197, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 70%, rgba(0, 76, 197, 0.2) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(0, 76, 197, 0.1) 0%, transparent 50%);
            animation: glow 4s ease-in-out infinite alternate;
            z-index: -1;
        }
        
        @keyframes glow {
            0% { opacity: 0.5; transform: scale(1); }
            100% { opacity: 1; transform: scale(1.1); }
        }
        
        /* Glassmorphism Header */
        .main-header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 15px 35px rgba(0, 76, 197, 0.3), 0 5px 15px rgba(0, 0, 0, 0.1);
            animation: slideDown 0.8s ease-out;
            position: relative;
            overflow: hidden;
        }
        
        .main-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            animation: shimmer 3s infinite;
        }
        
        .main-header h1 {
            font-weight: 700;
            font-size: 2.8rem;
            margin: 0;
            text-shadow: 0 0 20px rgba(255, 255, 255, 0.5), 0 0 40px rgba(0, 76, 197, 0.8);
            background: linear-gradient(45deg, #ffffff, #a8d8ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .main-header p {
            font-size: 1.2rem;
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        }
        
        /* Animation Keyframes */
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        /* Enhanced Tabs with Glassmorphism */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 8px;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 76, 197, 0.2);
            animation: fadeInUp 0.6s ease-out 0.2s both;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 55px;
            padding: 0px 28px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            color: #ffffff;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .stTabs [data-baseweb="tab"]::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #004cc5 0%, #0066ff 100%);
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: -1;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #004cc5 0%, #0066ff 100%) !important;
            color: white !important;
            box-shadow: 0 8px 25px rgba(0, 76, 197, 0.5);
            transform: translateY(-2px);
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
        }
        
        .stTabs [aria-selected="true"]::before {
            opacity: 1;
        }
        
        .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
            background: rgba(0, 76, 197, 0.3) !important;
            color: #ffffff !important;
            transform: translateY(-1px);
            box-shadow: 0 5px 15px rgba(0, 76, 197, 0.3);
        }
        
        /* Transparent Content Areas and Tables */
        .analysis-result {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 10px 30px rgba(0, 76, 197, 0.2);
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* Transparent Tables */
        .stDataFrame {
            background: transparent !important;
        }
        
        .stDataFrame > div {
            background: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 15px !important;
        }
        
        .stDataFrame table {
            background: transparent !important;
            color: white !important;
        }
        
        .stDataFrame table th {
            background: rgba(0, 76, 197, 0.3) !important;
            color: white !important;
            border: none !important;
        }
        
        .stDataFrame table td {
            background: transparent !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        .stDataFrame table tr:hover {
            background: rgba(255, 255, 255, 0.1) !important;
        }
        
        /* Risk Level Styling */
        .risk-high {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
            color: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 6px 20px rgba(255, 107, 107, 0.3);
            animation: pulse 2s infinite;
        }
        
        .risk-low {
            background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
            color: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 6px 20px rgba(81, 207, 102, 0.3);
        }
        
        .risk-medium {
            background: linear-gradient(135deg, #ffd43b 0%, #fab005 100%);
            color: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 6px 20px rgba(255, 212, 59, 0.3);
        }
        
        /* Transparent Text Input Areas */
        .stSelectbox > div > div {
            background: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 15px !important;
            color: white !important;
        }
        
        .stSelectbox > div > div > div {
            color: white !important;
        }
        
        .stTextArea > div > div > textarea {
            background: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 15px !important;
            color: white !important;
        }
        
        .stTextArea > div > div > textarea::placeholder {
            color: rgba(255, 255, 255, 0.7) !important;
        }
        
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 15px !important;
            color: white !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: rgba(255, 255, 255, 0.7) !important;
        }
        
        /* Enhanced Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #004cc5 0%, #0066ff 100%);
            color: white;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 6px 20px rgba(0, 76, 197, 0.4);
            backdrop-filter: blur(10px);
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0, 76, 197, 0.6);
            background: linear-gradient(135deg, #0066ff 0%, #0080ff 100%);
        }
        
        /* Transparent Content Cards */
        .content-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 10px 30px rgba(0, 76, 197, 0.2);
            animation: fadeInUp 0.6s ease-out;
            color: white;
        }
        
        /* Enhanced Metrics */
        .metric-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 1rem;
            color: white;
            transition: all 0.3s ease;
        }
        
        .metric-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 76, 197, 0.3);
        }
        
        /* Date Styling */
        .analysis-date {
            color: #64748b;
            font-size: 0.9rem;
            font-weight: 500;
            margin: 0.5rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Enhanced Header with Animation
        st.markdown("""
        <div class="main-header">
            <h1>🛡️ PhishSniffer</h1>
            <p>Advanced Email Security & Phishing Detection Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check model status first
        if not st.session_state.get('model_loaded', False):
            st.error(f"⚠️ Model not loaded: {st.session_state.get('model_error', 'Unknown error')}")
            st.info("Please ensure the model is trained and available.")
            return
        
        # Dashboard tabs navigation (like your image)
        analyze_tab, reports_tab, urls_tab, settings_tab = st.tabs([
            "📧 Analyze Email", 
            "📊 Reports & History", 
            "🔗 Suspicious URLs", 
            "⚙️ Settings & Model Info"
        ])
        
        # Content for each tab
        with analyze_tab:
            self._show_analyze_page()
        
        with reports_tab:
            self._show_reports_page()
        
        with urls_tab:
            self._show_urls_page()
        
        with settings_tab:
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
