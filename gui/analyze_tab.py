import tkinter as tk
from tkinter import filedialog, StringVar, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
import os
import time
import threading
import traceback
from email import policy
from email.parser import BytesParser, Parser

from  email_utils.parser import extract_email_content, extract_email_features
from  model.features import analyze_sender, check_special_patterns, extract_urls, scan_phishing_patterns, prepare_features_for_model
from  model.predict import run_model, generate_suspicious_indicators
from  storage.history import update_analysis_history
from  storage.urls import save_suspicious_urls
from  gui.report_tab import display_analysis_results

def setup_analyze_tab(app):
    """Set up the analyze email tab with modern UI components"""
    # Container with padding
    container = ttk.Frame(app.analyze_tab)
    container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    # Left panel - Email input
    left_panel = ttk.Frame(container)
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Right panel - Controls and info
    # Set width when creating the frame, not when packing it
    right_panel = ttk.Frame(container, width=250)
    right_panel.pack_propagate(False)  # Prevents the frame from shrinking to fit contents
    right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))  # Width removed from here

    # Email input area with title
    input_label = ttk.Label(
        left_panel,
        text="Email Content",
        font=("Segoe UI", 14, "bold")
    )
    input_label.pack(anchor=tk.W, pady=(0, 10))

    # Email text area with line numbers and syntax highlighting
    app.email_text = ScrolledText(
        left_panel,
        height=20,
        autohide=True,
        bootstyle="info"
    )
    app.email_text.pack(fill=tk.BOTH, expand=True)

    # Placeholder text
    placeholder = "Paste the email content here or upload an .eml file...\n\n" \
                  "You can paste the raw email including headers, or just the message body.\n" \
                  "For best results, include as much of the original email as possible."
    app.email_text.insert(tk.END, placeholder)

    # Right panel components
    # 1. File Upload Section
    upload_frame = ttk.LabelFrame(
        right_panel,
        text="Upload Email",
        bootstyle="info"
    )
    upload_frame.pack(fill=tk.X, pady=(0, 15))

    upload_btn = ttk.Button(
        upload_frame,
        text="Upload .eml File",
        command=lambda: upload_eml_file(app),
        bootstyle="info"
    )
    upload_btn.pack(padx=10, pady=10)

    # 2. Model Selection
    model_frame = ttk.LabelFrame(
        right_panel,
        text="Model Selection",
        bootstyle="info"
    )
    model_frame.pack(fill=tk.X, pady=(0, 15))

    # Model type radio buttons
    app.model_type = StringVar(value="existing")

    existing_radio = ttk.Radiobutton(
        model_frame,
        text="Use existing model",
        variable=app.model_type,
        value="existing",
        command=lambda: toggle_model_selection(app),
        bootstyle="info"
    )
    existing_radio.pack(fill=tk.X, padx=10, pady=(10, 5), anchor=tk.W)

    external_radio = ttk.Radiobutton(
        model_frame,
        text="Train new model",
        variable=app.model_type,
        value="external",
        command=lambda: toggle_model_selection(app),
        bootstyle="info"
    )
    external_radio.pack(fill=tk.X, padx=10, pady=(0, 5), anchor=tk.W)

    # Model info
    ttk.Label(model_frame, text="Current Model:").pack(anchor=tk.W, padx=10, pady=(5, 0))

    app.model_info_label = ttk.Label(
        model_frame,
        text="Custom Trained Model" if app.loaded_model else "No model loaded",
        bootstyle="info",
        wraplength=220
    )
    app.model_info_label.pack(padx=10, pady=(5, 10), fill=tk.X)

    # External model path display
    app.external_model_frame = ttk.Frame(model_frame)
    app.external_model_label = ttk.Label(
        app.external_model_frame,
        text="Train with custom datasets",
        bootstyle="secondary",
        wraplength=200
    )
    app.external_model_label.pack(padx=10, pady=5, fill=tk.X)

    # Initially hide the external model frame
    # Will be shown when "Train new model" is selected

    
    buttons_frame = ttk.Frame(right_panel)
    buttons_frame.pack(fill=tk.X, pady=(0, 15))
    # 3. Analyze Button
    app.analyze_btn = ttk.Button(
        buttons_frame,
        text="Analyze Email",
        command=lambda: analyze_email(app),
        bootstyle="success"
    )
    app.analyze_btn.pack(fill=tk.X, pady=(0, 15))

    # Reset button
    app.reset_btn = ttk.Button(
    buttons_frame,
    text="Reset",
    command=lambda: reset_analysis(app),
    bootstyle="secondary"
    )
    app.reset_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

    # 4. Quick Info Panel
    info_frame = ttk.LabelFrame(
        right_panel,
        text="Analysis Information",
        bootstyle="info"
    )
    info_frame.pack(fill=tk.BOTH, expand=True)

    # Status indicator
    status_frame = ttk.Frame(info_frame)
    status_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(
        status_frame,
        text="Status:",
        font=("Segoe UI", 10, "bold")
    ).pack(side=tk.LEFT)

    app.analysis_status_label = ttk.Label(
        status_frame,
        text="Ready to analyze",
        bootstyle="success"
    )
    app.analysis_status_label.pack(side=tk.LEFT, padx=(5, 0))

    # Previous results
    ttk.Separator(info_frame).pack(fill=tk.X, padx=10, pady=5)

    ttk.Label(
        info_frame,
        text="Recent Analyses:",
        font=("Segoe UI", 10, "bold")
    ).pack(anchor=tk.W, padx=10, pady=(5, 0))

    # Create a frame for previous results that will be updated
    app.prev_results_frame = ttk.Frame(info_frame)
    app.prev_results_frame.pack(fill=tk.X, padx=10, pady=5)

    # Load and display previous analysis history
    load_analysis_history(app)

def toggle_model_selection(app):
    """Toggle between existing model selection and external model loading"""
    if app.model_type.get() == "existing":
        app.external_model_frame.pack_forget()
        app.model_info_label.config(
            text="Using trained model from custom datasets",
            bootstyle="info"
        )
    else:
        app.external_model_frame.pack(fill=tk.X, padx=10, pady=5)
        app.model_info_label.config(
            text="Training new model...",
            bootstyle="warning"
        )
        # Start model training
        from  model.training import train_custom_model
        train_custom_model(app)

def upload_eml_file(app):
    """Upload and parse .eml file"""
    try:
        file_path = filedialog.askopenfilename(
            title="Select Email File",
            filetypes=[("Email files", "*.eml"), ("Text files", "*.txt"), ("All files", "*.*")]
        )

        if file_path:
            try:
                # Read the .eml file
                with open(file_path, 'rb') as file:
                    msg = BytesParser(policy=policy.default).parse(file)

                # Extract content to display with ALL headers
                email_content = extract_email_content(msg)

                # Clear and update the text widget
                app.email_text.delete(1.0, tk.END)
                app.email_text.insert(tk.END, email_content)

                # Save the loaded email
                app.current_email = {
                    'msg': msg,
                    'source': os.path.basename(file_path),
                    'path': file_path
                }

                app.update_status(f"Loaded email file: {os.path.basename(file_path)}", "info")
            except Exception as e:
                print(f"Error loading email: {e}")
                traceback.print_exc()

                Messagebox.show_error(
                    f"Error loading email file: {str(e)}",
                    "Error Loading Email"
                )
                app.update_status("Error loading email file", "error")
    except Exception as e:
        print(f"Error in upload dialog: {e}")
        traceback.print_exc()

def analyze_email(app):
    """Analyze the email for phishing indicators"""
    # Get the email content
    email_text = app.email_text.get(1.0, tk.END).strip()

    if not email_text or email_text == "Paste the email content here or upload an .eml file...":
        Messagebox.show_warning(
            "Please enter email content or upload an .eml file.",
            "No Email Content"
        )
        return

    # Reset previous analysis results - ADD THESE TWO LINES
    app.analysis_results = None
    app.current_email = None

    # Store the email content
    try:
        msg = Parser(policy=policy.default).parsestr(email_text)
        app.current_email = {
            'msg': msg,
            'source': 'manual input',
            'path': None
        }
    except Exception as e:
        print(f"Error parsing email: {e}")
        traceback.print_exc()
        # If parsing fails, still proceed with the raw text
        app.current_email = {
            'msg': email_text,
            'source': 'manual input',
            'path': None
        }

    # Show loading dialog and start analysis in a separate thread
    show_analysis_dialog(app)

def reset_analysis(app):
    """Reset the analysis and clear the input field"""
    # Clear the email text input
    app.email_text.delete(1.0, tk.END)
    
    # Reset placeholder text
    placeholder = "Paste the email content here or upload an .eml file...\n\n" \
                  "You can paste the raw email including headers, or just the message body.\n" \
                  "For best results, include as much of the original email as possible."
    app.email_text.insert(tk.END, placeholder)
    
    # Clear analysis results
    app.analysis_results = None
    app.current_email = None
    
    # Reset status
    app.update_status("Ready for new analysis", "info")
    app.analysis_status_label.config(text="Ready to analyze", bootstyle="success")
    
    # If we're on the report tab, switch back to analyze tab
    if app.tab_control.tab(app.tab_control.select(), "text") == "📊 Report":
        app.tab_control.select(app.analyze_tab)

def show_analysis_dialog(app):
    """Show a loading dialog during email analysis"""
    # Create loading dialog
    loading_window = ttk.Toplevel(app.root)
    loading_window.title("Analyzing Email")
    loading_window.geometry("400x200")

    # Center the loading window
    screen_width = loading_window.winfo_screenwidth()
    screen_height = loading_window.winfo_screenheight()
    x = (screen_width - 400) // 2
    y = (screen_height - 200) // 2
    loading_window.geometry(f"400x200+{x}+{y}")

    # Make it modal
    loading_window.transient(app.root)
    loading_window.grab_set()

    # Loading content
    content_frame = ttk.Frame(loading_window)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    ttk.Label(
        content_frame,
        text="Analyzing Email Content",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=(0, 15))

    # Status message
    status_var = StringVar(value="Extracting email components...")
    status_label = ttk.Label(
        content_frame,
        textvariable=status_var,
        bootstyle="info"
    )
    status_label.pack(pady=(0, 10))

    # Progress bar
    progress = ttk.Progressbar(
        content_frame,
        mode="determinate",
        length=360,
        bootstyle="success-striped"
    )
    progress.pack(pady=(0, 15))

    cancel_button = ttk.Button(
        content_frame,
        text="Cancel",
        command=loading_window.destroy,
        bootstyle="danger-outline"
    )
    cancel_button.pack()

    # Analysis steps
    analysis_steps = [
        "Extracting email components...",
        "Analyzing sender information...",
        "Checking for suspicious URLs...",
        "Scanning for phishing patterns...",
        "Running machine learning model...",
        "Calculating phishing probability...",
        "Generating report..."
    ]

    # Run analysis in a separate thread
    def run_analysis():
        try:
            # Step 1: Extract components
            progress["value"] = 14
            app.root.after(0, lambda: status_var.set(analysis_steps[0]))
            time.sleep(0.5)  # Simulate processing time

            email_features = extract_email_features(app.current_email)

            # Step 2: Analyze sender
            progress["value"] = 28
            app.root.after(0, lambda: status_var.set(analysis_steps[1]))
            time.sleep(0.5)

            sender_features = analyze_sender(email_features)

            # Step 3: Check URLs
            progress["value"] = 42
            app.root.after(0, lambda: status_var.set(analysis_steps[2]))
            time.sleep(0.5)

            url_features, extracted_urls = extract_urls(email_features)

            # Step 4: Scan patterns
            progress["value"] = 56
            app.root.after(0, lambda: status_var.set(analysis_steps[3]))
            time.sleep(0.5)

            pattern_features = scan_phishing_patterns(email_features)

            # Step 5: Run ML model
            progress["value"] = 70
            app.root.after(0, lambda: status_var.set(analysis_steps[4]))
            time.sleep(0.5)

            # Combine all features
            all_features = {**email_features, **sender_features, **url_features, **pattern_features}
            app.features_dict = all_features

            # Prepare features for the model
            features_for_model = prepare_features_for_model(all_features, getattr(app, 'model_feature_count', 10))

            # Run the model
            prediction_probability = run_model(app, features_for_model)

            # Generate indicators based on features
            suspicious_indicators = generate_suspicious_indicators(all_features)

            # Check for special phishing patterns - ADD THIS SECTION
            is_special_pattern = check_special_patterns(all_features)
            if is_special_pattern:
                # Override the prediction if it matches a special pattern
                prediction_probability = max(0.95, prediction_probability)  # Set to at least 95%
                # Add special pattern indicator to suspicious indicators
                suspicious_indicators.append({
                    "name": "Matches known phishing pattern",
                    "description": "This email matches a known phishing campaign pattern",
                    "severity": "Critical"
                })
                app.root.after(0, lambda: status_var.set("Known phishing pattern detected!"))
                time.sleep(0.5)

            # Step 6: Calculate probability
            progress["value"] = 84
            app.root.after(0, lambda: status_var.set(analysis_steps[5]))
            time.sleep(0.5)

            

            # Step 7: Generate report
            progress["value"] = 100
            app.root.after(0, lambda: status_var.set(analysis_steps[6]))
            time.sleep(0.5)

            # Create results object
            is_phishing = prediction_probability >= 0.7  # Threshold

            app.analysis_results = {
                'email': email_features,
                'timestamp': app.current_datetime,
                'probability': prediction_probability,
                'is_phishing': is_phishing,
                'indicators': suspicious_indicators,
                'extracted_urls': extracted_urls,
                'source': app.current_email['source'],
                'features': all_features
            }

            # Store URLs
            add_suspicious_urls(app, extracted_urls, is_phishing)

            # Update analysis history
            updated_history = update_analysis_history(app.history_file, 
                                            app.current_email['source'], 
                                            app.current_datetime,
                                            is_phishing, 
                                            prediction_probability)
            
            # Update history display
            app.root.after(0, lambda: update_history_display(app, updated_history))

            # Close loading window if it still exists
            if loading_window.winfo_exists():
                loading_window.destroy()

            # Update UI with results - use after to safely update from thread
            app.root.after(0, lambda: display_analysis_results(app))

            # Update status - use thread-safe update
            verdict = "Phishing detected" if is_phishing else "No phishing detected"
            status_type = "error" if is_phishing else "success"
            app.update_status(f"Analysis complete: {verdict}", status_type)

            # Update quick info - use after to safely update from thread
            app.root.after(0, lambda: app.analysis_status_label.config(
                text="Analysis complete",
                bootstyle="success"
            ))

            # Switch to report tab - use after to safely update from thread
            app.root.after(0, lambda: app.tab_control.select(app.report_tab))

        except Exception as e:
            print(f"Analysis error: {str(e)}")
            traceback.print_exc()

            # Close loading window if it still exists
            if loading_window.winfo_exists():
                loading_window.destroy()

            # Show error message in the main thread
            app.root.after(0, lambda: Messagebox.show_error(
                f"An error occurred during analysis: {str(e)}",
                "Analysis Error"
            ))
            app.update_status("Error during analysis", "error")

    # Start analysis thread
    threading.Thread(target=run_analysis, daemon=True).start()

def update_history_display(app, history):
    """Update the display of previous analyses"""
    # Clear current display
    for widget in app.prev_results_frame.winfo_children():
        widget.destroy()

    if not history:
        # Show placeholder
        ttk.Label(
            app.prev_results_frame,
            text="No previous analyses",
            bootstyle="secondary"
        ).pack(pady=5)
        return

    # Add history items
    for i, entry in enumerate(history[:5]):  # Show only most recent 5
        # Get values
        source = entry.get('source', 'Unknown')
        timestamp = entry.get('timestamp', '')
        is_phishing = bool(entry.get('is_phishing', 0))  # Convert back to boolean
        probability = float(entry.get('probability', 0.0))

        # Create item frame
        item_frame = ttk.Frame(app.prev_results_frame)
        item_frame.pack(fill=tk.X, pady=(0, 5))

        # Status indicator
        indicator = "🔴" if is_phishing else "🟢"

        ttk.Label(
            item_frame,
            text=indicator,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT)

        # Source and timestamp
        info_frame = ttk.Frame(item_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        ttk.Label(
            info_frame,
            text=source,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor=tk.W)

        ttk.Label(
            info_frame,
            text=timestamp,
            font=("Segoe UI", 8),
            bootstyle="secondary"
        ).pack(anchor=tk.W)

        # Probability
        ttk.Label(
            item_frame,
            text=f"{probability:.1%}",
            font=("Segoe UI", 9),
            bootstyle="danger" if is_phishing else "success"
        ).pack(side=tk.RIGHT)

        # Add separator
        if i < len(history) - 1 and i < 4:
            ttk.Separator(app.prev_results_frame).pack(fill=tk.X, pady=(0, 5))

def load_analysis_history(app):
    """Load and display analysis history"""
    from  storage.history import load_analysis_history as load_history
    history = load_history(app.history_file)
    update_history_display(app, history)

def add_suspicious_urls(app, urls, is_phishing):
    """Add URLs from analysis to suspicious URLs list"""
    if not urls:
        return

    updated = False  # Track if we updated the list
    
    # Add each URL
    for url in urls:
        # Check if URL already exists
        if any(entry.get('url') == url for entry in app.suspicious_urls):
            continue

        # Create new entry
        url_entry = {
            'url': url,
            'source': app.current_email.get('source', 'Analysis'),
            'date_added': app.current_datetime,
            'risk_level': 'High' if is_phishing else 'Medium'
        }

        app.suspicious_urls.append(url_entry)
        updated = True

    # Save updated list if changes were made
    if updated:
        save_suspicious_urls(app.urls_file, app.suspicious_urls)

        # Always update the URLs tab display if we're on that tab
        app.root.after(0, lambda: update_urls_display(app))

def update_urls_display(app):
    """Update the URLs tab display regardless of current tab"""
    from gui.urls_tab import display_suspicious_urls
    
    # Force update of URLs display
    if hasattr(app, 'url_tree'):
        display_suspicious_urls(app)

