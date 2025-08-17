#!/usr/bin/env python3
"""
Main Streamlit application launcher for PhishSniffer.
Runs the web-based GUI interface.
"""

import streamlit as st
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from gui.main_window import main

if __name__ == "__main__":
    main()
