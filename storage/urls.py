import os
import json
import traceback

def load_suspicious_urls(urls_file):
    """Load suspicious URLs from file"""
    try:
        if os.path.exists(urls_file):
            with open(urls_file, 'r') as file:
                return json.load(file)
        else:
            return []
    except Exception as e:
        print(f"Error loading suspicious URLs: {e}")
        traceback.print_exc()
        return []

def save_suspicious_urls(urls_file, suspicious_urls):
    """Save suspicious URLs to file"""
    try:
        with open(urls_file, 'w') as file:
            json.dump(suspicious_urls, file, indent=2)
    except Exception as e:
        print(f"Error saving suspicious URLs: {e}")
        traceback.print_exc()