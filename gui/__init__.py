# GUI package initialization
"""
GUI package for PhishSniffer.
Contains Streamlit interface components and user interaction modules.
"""

from .main_window import PhishingDetectorApp
from .analyze_tab import show_analyze_tab
from .report_tab import show_report_tab

__all__ = [
    'PhishingDetectorApp',
    'show_analyze_tab',
    'show_report_tab'
]