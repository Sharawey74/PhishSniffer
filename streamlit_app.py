#!/usr/bin/env python3
"""
Streamlit App Entry Point for PhishSniffer
Launch the dashboard with: streamlit run streamlit_app.py
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the main app
from gui.main_window import main

if __name__ == "__main__":
    main()
