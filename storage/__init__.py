"""
Storage package for PhishSniffer.
Contains data persistence, URL management, and history tracking utilities.
"""

from .urls import load_suspicious_urls, save_suspicious_urls
from .history import load_analysis_history, update_analysis_history
from .extract import extract_data, extract_email_data, extract_multiple_datasets

__all__ = [
    'load_suspicious_urls',
    'save_suspicious_urls',
    'load_analysis_history',
    'update_analysis_history',
    'extract_data',
    'extract_email_data',
    'extract_multiple_datasets'
]