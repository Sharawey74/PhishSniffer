import tkinter as tk
from tkinter import StringVar
import ttkbootstrap as ttk
import os
import threading
import time
from datetime import datetime

from gui.splash_screen import show_splash
from gui.analyze_tab import setup_analyze_tab
from gui.report_tab import setup_report_tab
from gui.urls_tab import setup_urls_tab, display_suspicious_urls
from gui.settings_tab import setup_settings_tab
from storage.urls import load_suspicious_urls, save_suspicious_urls
from model.training import train_custom_model
from storage.history import load_analysis_history

class PhishingDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phishing Email Detector")
        self.root.geometry("1000x700")
        self.style = ttk.Style("darkly")  # Modern dark theme

        # Initialize data structures
        self.suspicious_urls = []
        self.analysis_results = None
        self.current_email = None
        self.features_dict = {}
        self.loaded_model = None
        self.model_metadata = {}

        # Define file paths
        self.app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.app_dir, "data")
        self.urls_file = os.path.join(self.data_dir, "suspicious_urls.json")
        self.models_dir = os.path.join(self.app_dir, "models")
        self.history_file = os.path.join(self.data_dir, "analysis_history.json")

        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)

        # Current user and datetime
        self.current_user = "Lujain Hesham"
        self.current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Load suspicious URLs from file
        self.suspicious_urls = load_suspicious_urls(self.urls_file)

        # Store the root to hide it during splash screen
        self.root.withdraw()

        # Launch splash screen
        show_splash(self)

    def setup_main_ui(self):
        """Set up the main application UI after splash screen"""
        try:
            # Create header with app title and user info
            self.create_header()

            # Create a notebook for tabs
            self.tab_control = ttk.Notebook(self.root)

            # Create the tabs
            self.analyze_tab = ttk.Frame(self.tab_control)
            self.report_tab = ttk.Frame(self.tab_control)
            self.urls_tab = ttk.Frame(self.tab_control)
            self.settings_tab = ttk.Frame(self.tab_control)

            # Add tabs to notebook with icons
            self.tab_control.add(self.analyze_tab, text="✉️ Analyze Email")
            self.tab_control.add(self.report_tab, text="📊 Report")
            self.tab_control.add(self.urls_tab, text="🔗 Suspicious URLs")
            self.tab_control.add(self.settings_tab, text="⚙️ Model/Settings")
            self.tab_control.pack(expand=1, fill="both", padx=10, pady=(10, 0))

            # Setup each tab
            setup_analyze_tab(self)
            setup_report_tab(self)
            setup_urls_tab(self)
            setup_settings_tab(self)

            # Footer status bar
            self.create_footer()
        except Exception as e:
            print(f"Error setting up UI: {e}")
            import traceback
            traceback.print_exc()

    def create_header(self):
        """Create app header with title and user info"""
        header_frame = ttk.Frame(self.root, bootstyle="dark")
        header_frame.pack(fill=tk.X, padx=0, pady=0)

        # Left side - App title
        title_frame = ttk.Frame(header_frame, bootstyle="dark")
        title_frame.pack(side=tk.LEFT, padx=15, pady=10)

        # App icon and title
        title_label = ttk.Label(
            title_frame,
            text="🛡️Phishing Detector",
            font=("Segoe UI", 16, "bold"),
            bootstyle="light"
        )
        title_label.pack(side=tk.LEFT)

        # Right side - User info
        user_frame = ttk.Frame(header_frame, bootstyle="dark")
        user_frame.pack(side=tk.RIGHT, padx=15, pady=10)

        # User avatar (placeholder circle)
        user_avatar = ttk.Label(
            user_frame,
            text="👤",  # Placeholder avatar
            font=("Segoe UI", 14),
            bootstyle="light"
        )
        user_avatar.pack(side=tk.LEFT, padx=(0, 5))

        # User name
        user_label = ttk.Label(
            user_frame,
            text=f"Welcome, {self.current_user}",
            font=("Segoe UI", 10),
            bootstyle="light"
        )
        user_label.pack(side=tk.LEFT)

    def create_footer(self):
        """Create footer with status information"""
        self.footer_frame = ttk.Frame(self.root, bootstyle="dark")
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Status indicator - green dot for "ready"
        self.status_text_indicator = ttk.Label(
            self.footer_frame,
            text="●",
            font=("Segoe UI", 14),
            foreground="#28a745"
        )
        self.status_text_indicator.pack(side=tk.LEFT, padx=10, pady=5)

        # Status text
        self.status_text = ttk.Label(
            self.footer_frame,
            text="Ready",
            bootstyle="light"
        )
        self.status_text.pack(side=tk.LEFT, padx=0, pady=5)

        # Date/time on right
        self.datetime_label = ttk.Label(
            self.footer_frame,
            text=f"Last updated: {self.current_datetime}",
            bootstyle="secondary"
        )
        self.datetime_label.pack(side=tk.RIGHT, padx=10, pady=5)

    def update_status(self, message, status_type="success"):
        """Update the status bar with a message and appropriate color - Thread Safe"""
        
        def _update():
            color_map = {
                "success": "#28a745",
                "warning": "#ffc107",
                "error": "#dc3545",
                "info": "#17a2b8"
            }

            if hasattr(self, 'status_text_indicator'):
                self.status_text_indicator.config(foreground=color_map.get(status_type, "#28a745"))
            if hasattr(self, 'status_text'):
                self.status_text.config(text=message)
            if hasattr(self, 'datetime_label'):
                self.datetime_label.config(text=f"Last updated: {self.current_datetime}")

        # Check if we're in the main thread
        if threading.current_thread() is threading.main_thread():
            _update()
        else:
            # Schedule the update to run in the main thread
            self.root.after(0, _update)