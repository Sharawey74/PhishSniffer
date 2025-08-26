#!/usr/bin/env python3
"""
Streamlit Cloud initialization script for PhishSniffer.
This script handles setup requirements for cloud deployment.
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

def setup_nltk():
    """Setup NLTK for cloud deployment."""
    try:
        import nltk
        print("📚 Setting up NLTK...")
        
        # Create NLTK data directory
        nltk_data_dir = os.path.expanduser('~/nltk_data')
        if not os.path.exists(nltk_data_dir):
            os.makedirs(nltk_data_dir)
        
        # Download required NLTK data
        try:
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt', quiet=True)
            print("✅ NLTK setup completed")
        except Exception as e:
            print(f"⚠️ NLTK download failed: {e}")
            
    except ImportError:
        print("⚠️ NLTK not available - using fallback options")

def setup_model_directory():
    """Ensure model directory exists."""
    model_dirs = ['trained_models', 'models']
    for dir_name in model_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"📁 Created directory: {dir_name}")

def setup_data_directories():
    """Ensure data directories exist."""
    data_dirs = [
        'data', 'cleaned_data', 'config', 'storage', 
        'data/feedback', 'evaluation_plots'
    ]
    for dir_name in data_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

def create_fallback_files():
    """Create fallback configuration files."""
    
    # Create settings.json if not exists
    settings_file = 'data/settings.json'
    if not os.path.exists(settings_file):
        import json
        default_settings = {
            "risk_threshold": 0.5,
            "auto_save": True,
            "url_checking": True
        }
        with open(settings_file, 'w') as f:
            json.dump(default_settings, f, indent=2)
        print(f"✅ Created fallback settings: {settings_file}")
    
    # Create analysis_history.json if not exists
    history_file = 'data/analysis_history.json'
    if not os.path.exists(history_file):
        import json
        with open(history_file, 'w') as f:
            json.dump([], f)
        print(f"✅ Created fallback history: {history_file}")
    
    # Create suspicious_urls.json if not exists
    urls_file = 'data/suspicious_urls.json'
    if not os.path.exists(urls_file):
        import json
        with open(urls_file, 'w') as f:
            json.dump([], f)
        print(f"✅ Created fallback URLs: {urls_file}")

def initialize_for_cloud():
    """Initialize PhishSniffer for cloud deployment."""
    print("🚀 Initializing PhishSniffer for Streamlit Cloud...")
    
    # Setup directories
    setup_model_directory()
    setup_data_directories()
    
    # Setup NLTK
    setup_nltk()
    
    # Create fallback files
    create_fallback_files()
    
    print("✅ Cloud initialization completed!")

if __name__ == "__main__":
    initialize_for_cloud()
