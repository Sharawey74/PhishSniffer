import csv
import json
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
import os
import traceback
import webbrowser

def setup_report_tab(app):
    """Set up the report tab with a placeholder for analysis results"""
    container = ttk.Frame(app.report_tab)
    container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    # Initial message when no analysis has been performed
    app.report_placeholder = ttk.Label(
        container,
        text="No analysis results yet. Please analyze an email first.",
        font=("Segoe UI", 12),
        bootstyle="secondary"
    )
    app.report_placeholder.pack(expand=True)

def display_analysis_results(app):
    """Display the analysis results in the report tab"""
    # Check if we have results
    if not app.analysis_results:
        return

    # Clear the report tab
    for widget in app.report_tab.winfo_children():
        widget.destroy()

    # Container with padding
    container = ttk.Frame(app.report_tab)
    container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    # Create two columns
    left_col = ttk.Frame(container)
    left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    right_col = ttk.Frame(container)
    right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

    # Left column - Summary and primary results
    create_summary_section(app, left_col)
    create_indicators_section(app, left_col)

    # Right column - Email details and technical analysis
    create_email_details_section(app, right_col)
    create_urls_section(app, right_col)

    # Add action buttons at the bottom
    create_action_buttons(app, container)

def create_summary_section(app, parent):
    """Create the summary section of the report"""
    # Summary frame
    summary_frame = ttk.LabelFrame(parent, text="Analysis Summary")
    summary_frame.pack(fill=tk.X, pady=(0, 15))

    # Get values from results
    is_phishing = app.analysis_results.get('is_phishing', False)
    probability = app.analysis_results.get('probability', 0.0)

    # Summary content
    summary_content = ttk.Frame(summary_frame)
    summary_content.pack(fill=tk.X, padx=15, pady=15)

    # Verdict with icon
    verdict_frame = ttk.Frame(summary_content)
    verdict_frame.pack(fill=tk.X, pady=(0, 15))

    if is_phishing:
        verdict_icon = "🔴"  # Red circle for phishing
        verdict_text = "PHISHING DETECTED"
        verdict_color = "danger"
    else:
        verdict_icon = "🟢"  # Green circle for safe
        verdict_text = "NO PHISHING DETECTED"
        verdict_color = "success"

    ttk.Label(
        verdict_frame,
        text=verdict_icon,
        font=("Segoe UI", 24)
    ).pack(side=tk.LEFT, padx=(0, 10))

    verdict_text_frame = ttk.Frame(verdict_frame)
    verdict_text_frame.pack(side=tk.LEFT)

    ttk.Label(
        verdict_text_frame,
        text=verdict_text,
        font=("Segoe UI", 16, "bold"),
        bootstyle=verdict_color
    ).pack(anchor=tk.W)

    ttk.Label(
        verdict_text_frame,
        text=f"Confidence: {probability:.1%}",
        bootstyle="secondary"
    ).pack(anchor=tk.W)

    # Probability meter
    meter_frame = ttk.Frame(summary_content)
    meter_frame.pack(fill=tk.X, pady=(0, 15))

    ttk.Label(
        meter_frame,
        text="Phishing Probability:",
        font=("Segoe UI", 10, "bold")
    ).pack(anchor=tk.W, pady=(0, 5))

    # Probability bar
    prob_bar = ttk.Progressbar(
        meter_frame,
        value=probability * 100,
        length=300,
        bootstyle=verdict_color
    )
    prob_bar.pack(fill=tk.X)

    # Scale labels
    scale_frame = ttk.Frame(meter_frame)
    scale_frame.pack(fill=tk.X)

    ttk.Label(
        scale_frame,
        text="0%",
        bootstyle="secondary"
    ).pack(side=tk.LEFT)

    ttk.Label(
        scale_frame,
        text="50%",
        bootstyle="secondary"
    ).pack(side=tk.LEFT, padx=(125, 0))

    ttk.Label(
        scale_frame,
        text="100%",
        bootstyle="secondary"
    ).pack(side=tk.RIGHT)

    # Summary text
    summary_text = f"The email was analyzed on {app.current_datetime}. "

    if is_phishing:
        summary_text += "Our analysis indicates this is very likely a phishing attempt. "
        summary_text += "We recommend you do NOT click any links, download attachments, or reply to this message."
    else:
        summary_text += "Our analysis suggests this email is likely safe, "
        summary_text += "but always exercise caution with unexpected emails."

    ttk.Label(
        summary_content,
        text=summary_text,
        wraplength=400,
        justify=tk.LEFT
    ).pack(fill=tk.X)

def create_indicators_section(app, parent):
    """Create the indicators section of the report"""
    # Get indicators from results
    indicators = app.analysis_results.get('indicators', [])

    if not indicators:
        return

    # Indicators frame
    indicators_frame = ttk.LabelFrame(parent, text="Suspicious Indicators")
    indicators_frame.pack(fill=tk.BOTH, expand=True)

    # Container for indicators with scrolling
    indicators_canvas = ttk.Canvas(indicators_frame)
    scrollbar = ttk.Scrollbar(indicators_frame, orient="vertical", command=indicators_canvas.yview)
    scrollable_frame = ttk.Frame(indicators_canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: indicators_canvas.configure(scrollregion=indicators_canvas.bbox("all"))
    )

    indicators_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    indicators_canvas.configure(yscrollcommand=scrollbar.set)

    indicators_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y", pady=10)

    # Add indicators to the frame
    for i, indicator in enumerate(indicators):
        create_indicator_item(scrollable_frame, indicator, i, len(indicators))

def create_indicator_item(parent, indicator, index, total):
    """Create an individual indicator item"""
    # Get indicator data
    indicator_type = indicator.get('type', 'info')
    indicator_name = indicator.get('name', 'Unknown')
    indicator_desc = indicator.get('description', '')

    # Map type to style and icon
    style_map = {
        'critical': ('danger', '⚠️'),
        'warning': ('warning', '⚠️'),
        'info': ('info', 'ℹ️')
    }

    style, icon = style_map.get(indicator_type, style_map['info'])

    # Create frame for this indicator
    item_frame = ttk.Frame(parent)
    item_frame.pack(fill=tk.X, pady=(0, 10))

    # Icon and name row
    header_frame = ttk.Frame(item_frame)
    header_frame.pack(fill=tk.X)

    ttk.Label(
        header_frame,
        text=icon,
        font=("Segoe UI", 12)
    ).pack(side=tk.LEFT)

    ttk.Label(
        header_frame,
        text=indicator_name,
        font=("Segoe UI", 10, "bold"),
        bootstyle=style
    ).pack(side=tk.LEFT, padx=(5, 0))

    # Description
    ttk.Label(
        item_frame,
        text=indicator_desc,
        wraplength=370,
        justify=tk.LEFT
    ).pack(fill=tk.X, padx=(25, 0))

    # Add separator if not the last item
    if index < total - 1:
        ttk.Separator(parent).pack(fill=tk.X, pady=(0, 10))

def create_email_details_section(app, parent):
    """Create the email details section"""
    # Email details frame
    details_frame = ttk.LabelFrame(parent, text="Email Details")
    details_frame.pack(fill=tk.X, pady=(0, 15))

    details_content = ttk.Frame(details_frame)
    details_content.pack(fill=tk.X, padx=15, pady=15)

    # Get email data
    email_data = app.analysis_results.get('email', {})

    # Create scrollable frame for headers with fixed height
    headers_canvas = ttk.Canvas(details_content, height=200)  # Set height here, not in pack
    headers_scrollbar = ttk.Scrollbar(details_content, orient="vertical", command=headers_canvas.yview)
    headers_frame = ttk.Frame(headers_canvas)

    headers_frame.bind(
        "<Configure>",
        lambda e: headers_canvas.configure(scrollregion=headers_canvas.bbox("all"))
    )

    headers_canvas.create_window((0, 0), window=headers_frame, anchor="nw")
    headers_canvas.configure(yscrollcommand=headers_scrollbar.set)

    # Pack widgets properly
    headers_canvas.pack(side="left", fill="both", expand=True)  # Height removed from here
    headers_scrollbar.pack(side="right", fill="y")

    # Details table - include all available headers
    details = []

    # Add standard headers first
    standard_headers = [
        ("From:", email_data.get('from', 'Unknown')),
        ("To:", email_data.get('to', 'Unknown')),
        ("Subject:", email_data.get('subject', 'No Subject')),
        ("Date:", email_data.get('date', 'Unknown')),
        ("Source:", app.analysis_results.get('source', 'Manual input'))
    ]

    details.extend(standard_headers)

    # Add additional headers if available
    if 'headers' in email_data and isinstance(email_data['headers'], dict):
        for header, value in email_data['headers'].items():
            # Skip headers we already included
            if header.lower() not in ['from', 'to', 'subject', 'date']:
                details.append((f"{header}:", value))

    # Add headers to the frame
    for i, (label, value) in enumerate(details):
        ttk.Label(
            headers_frame,
            text=label,
            font=("Segoe UI", 10, "bold")
        ).grid(row=i, column=0, sticky=tk.W, pady=2)

        ttk.Label(
            headers_frame,
            text=value,
            wraplength=300
        ).grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=2)

def create_urls_section(app, parent):
    """Create the URLs section"""
    # Get URLs from analysis
    urls = app.analysis_results.get('extracted_urls', [])

    if not urls:
        return

    # URLs frame
    urls_frame = ttk.LabelFrame(parent, text="Detected URLs")
    urls_frame.pack(fill=tk.BOTH, expand=True)

    urls_content = ttk.Frame(urls_frame)
    urls_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    # URL count
    ttk.Label(
        urls_content,
        text=f"Found {len(urls)} URLs in this email:",
        font=("Segoe UI", 10, "bold")
    ).pack(anchor=tk.W, pady=(0, 10))

    # URL list with scrolling
    url_canvas = ttk.Canvas(urls_content)
    url_scrollbar = ttk.Scrollbar(urls_content, orient="vertical", command=url_canvas.yview)
    url_frame = ttk.Frame(url_canvas)

    url_frame.bind(
        "<Configure>",
        lambda e: url_canvas.configure(scrollregion=url_canvas.bbox("all"))
    )

    url_canvas.create_window((0, 0), window=url_frame, anchor="nw")
    url_canvas.configure(yscrollcommand=url_scrollbar.set)

    url_canvas.pack(side="left", fill="both", expand=True)
    url_scrollbar.pack(side="right", fill="y")

    # Add URLs to the list
    for i, url in enumerate(urls):
        url_item = ttk.Frame(url_frame)
        url_item.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(
            url_item,
            text=f"{i + 1}.",
            font=("Segoe UI", 10, "bold")
        ).pack(side=tk.LEFT)

        ttk.Label(
            url_item,
            text=url,
            wraplength=300
        ).pack(side=tk.LEFT, padx=(5, 0))

def create_action_buttons(app, parent):
    """Create action buttons for the report"""
    button_frame = ttk.Frame(parent)
    button_frame.pack(fill=tk.X, pady=(15, 0))

    # Phishing verdict
    is_phishing = app.analysis_results.get('is_phishing', False)

    if is_phishing:
        # Report phishing button
        ttk.Button(
            button_frame,
            text="Report as Phishing",
            bootstyle="danger",
            command=lambda: report_phishing(app)
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Block sender button
        ttk.Button(
            button_frame,
            text="Block Sender",
            bootstyle="warning",
            command=lambda: block_sender(app)
        ).pack(side=tk.LEFT, padx=(0, 10))

    else:
        # Mark as safe button
        ttk.Button(
            button_frame,
            text="Mark as Safe",
            bootstyle="success",
            command=lambda: mark_as_safe(app)
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Report false negative button
        ttk.Button(
            button_frame,
            text="Report as Phishing",
            bootstyle="warning-outline",
            command=lambda: report_phishing(app)
        ).pack(side=tk.LEFT)

    # Save report button
    ttk.Button(
        button_frame,
        text="Save Report",
        bootstyle="info",
        command=lambda: save_report(app)
    ).pack(side=tk.RIGHT)


def block_sender(app):
    """Block sender of the email"""
    # Get sender email
    if not app.analysis_results:
        return

    sender = app.analysis_results.get('email', {}).get('from', '')

    Messagebox.show_info(
        f"This would typically add the sender '{sender}' to your email client's block list. This is a placeholder for that functionality.",
        "Block Sender"
    )

def report_phishing(app):
    """Report email as phishing and update model"""
    if not app.analysis_results:
        return

    try:
        # Get the current classification
        was_classified_as_phishing = app.analysis_results.get('is_phishing', False)
        
        # If it was already classified as phishing, just acknowledge
        if was_classified_as_phishing:
            Messagebox.show_info(
                "Thank you for confirming our analysis. This feedback helps improve our detection model.",
                "Feedback Received"
            )
        else:
            # This was a false negative - update the model
            # Extract features from the email
            features = app.features_dict
            
            # Log the feedback
            log_feedback(app, "phishing", was_classified_as_phishing)
            
            # Save to phishing samples for model retraining
            save_feedback_sample(app, features, True)
            
            Messagebox.show_info(
                "Thank you for reporting this as phishing. Our model will be updated to better detect similar emails in the future.",
                "Feedback Received"
            )
            
        # Update the UI to reflect the feedback
        app.analysis_results['is_phishing'] = True
        app.analysis_results['user_feedback'] = "phishing"
        display_analysis_results(app)  # Refresh the display
        
    except Exception as e:
        print(f"Error saving phishing report: {e}")
        traceback.print_exc()
        Messagebox.show_error(
            f"Error saving your feedback: {str(e)}",
            "Feedback Error"
        )

def mark_as_safe(app):
    """Mark email as safe and update model"""
    if not app.analysis_results:
        return
        
    try:
        # Get the current classification
        was_classified_as_phishing = app.analysis_results.get('is_phishing', False)
        
        # If it was already classified as safe, just acknowledge
        if not was_classified_as_phishing:
            Messagebox.show_info(
                "Thank you for confirming our analysis. This feedback helps improve our detection model.",
                "Feedback Received"
            )
        else:
            # This was a false positive - update the model
            # Extract features from the email
            features = app.features_dict
            
            # Log the feedback
            log_feedback(app, "safe", was_classified_as_phishing)
            
            # Save to safe samples for model retraining
            save_feedback_sample(app, features, False)
            
            Messagebox.show_info(
                "Thank you for reporting this as safe. Our model will be updated to reduce false positives in the future.",
                "Feedback Received"
            )
            
        # Update the UI to reflect the feedback
        app.analysis_results['is_phishing'] = False
        app.analysis_results['user_feedback'] = "safe"
        display_analysis_results(app)  # Refresh the display
        
    except Exception as e:
        print(f"Error saving safe report: {e}")
        traceback.print_exc()
        Messagebox.show_error(
            f"Error saving your feedback: {str(e)}",
            "Feedback Error"
        )

def log_feedback(app, feedback_type, original_classification):
    """Log user feedback for later analysis"""
    try:
        feedback_dir = os.path.join(app.data_dir, "feedback")
        os.makedirs(feedback_dir, exist_ok=True)
        
        feedback_file = os.path.join(feedback_dir, "feedback_log.csv")
        
        # Create file with headers if it doesn't exist
        if not os.path.exists(feedback_file):
            with open(feedback_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["timestamp", "source", "original_classification", "user_feedback", "sender"])
        
        # Append feedback
        with open(feedback_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                app.current_datetime,
                app.analysis_results.get('source', 'manual input'),
                "phishing" if original_classification else "safe",
                feedback_type,
                app.analysis_results.get('email', {}).get('from', 'unknown')
            ])
            
        app.update_status(f"Feedback logged successfully", "success")
        
    except Exception as e:
        print(f"Error logging feedback: {e}")
        traceback.print_exc()

def save_feedback_sample(app, features, is_phishing):
    """Save email sample for model retraining"""
    try:
        # Create directories if they don't exist
        feedback_dir = os.path.join(app.data_dir, "feedback")
        samples_dir = os.path.join(feedback_dir, "phishing" if is_phishing else "safe")
        os.makedirs(samples_dir, exist_ok=True)
        
        # Create a unique filename
        timestamp = app.current_datetime.replace(":", "-").replace(" ", "_")
        filename = f"sample_{timestamp}.json"
        filepath = os.path.join(samples_dir, filename)
        
        # Save the features and email content
        sample_data = {
            "features": features,
            "email_content": app.current_email.get('msg', ''),
            "is_phishing": is_phishing,
            "source": app.analysis_results.get('source', 'manual input'),
            "timestamp": app.current_datetime
        }
        
        with open(filepath, 'w') as file:
            json.dump(sample_data, file, indent=2, default=str)
            
        print(f"Sample saved to {filepath}")
        
    except Exception as e:
        print(f"Error saving sample: {e}")
        traceback.print_exc()

def save_report(app):
    """Save analysis report to file"""
    if not app.analysis_results:
        return

    # Get a file path to save to
    file_path = filedialog.asksaveasfilename(
        title="Save Report",
        filetypes=[("HTML files", "*.html"), ("Text files", "*.txt"), ("All files", "*.*")],
        defaultextension=".html"
    )

    if not file_path:
        return

    try:
        # Simple HTML report
        if file_path.endswith('.html'):
            save_html_report(app, file_path)
        else:
            save_text_report(app, file_path)

        app.update_status(f"Report saved to {os.path.basename(file_path)}", "success")

    except Exception as e:
        print(f"Error saving report: {e}")
        traceback.print_exc()
        Messagebox.show_error(
            f"Error saving report: {str(e)}",
            "Save Error"
        )

def save_html_report(app, file_path):
    """Save report as HTML file"""
    # Get data
    is_phishing = app.analysis_results.get('is_phishing', False)
    probability = app.analysis_results.get('probability', 0.0)
    email_data = app.analysis_results.get('email', {})
    indicators = app.analysis_results.get('indicators', [])
    urls = app.analysis_results.get('extracted_urls', [])

    # Verdict text
    verdict = "PHISHING DETECTED" if is_phishing else "NO PHISHING DETECTED"
    verdict_color = "#dc3545" if is_phishing else "#28a745"

    # Create HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Phishing Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ text-align: center; margin-bottom: 20px; }}
            .verdict {{ color: {verdict_color}; font-size: 24px; font-weight: bold; }}
            .section {{ margin-bottom: 20px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
            .critical {{ color: #dc3545; }}
            .warning {{ color: #ffc107; }}
            .info {{ color: #17a2b8; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            .footer {{ text-align: center; font-size: 12px; color: #666; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Phishing Email Analysis Report</h1>
            <p>Generated on {app.current_datetime}</p>
            <p class="verdict">{verdict}</p>
            <p>Phishing Probability: {probability:.1%}</p>
        </div>

        <div class="section">
            <h2>Email Details</h2>
            <table>
    """

    # Add email headers to table
    for header, value in email_data.items():
        if header != 'headers' and header != 'body':
            html += f"<tr><th>{header.title()}</th><td>{value}</td></tr>\n"

    # Add source
    html += f"""
                <tr><th>Source</th><td>{app.analysis_results.get('source', 'Manual input')}</td></tr>
            </table>
        </div>
    """

    # Add indicators section
    if indicators:
        html += """
        <div class="section">
            <h2>Suspicious Indicators</h2>
            <ul>
        """

        for indicator in indicators:
            indicator_type = indicator.get('type', 'info')
            indicator_name = indicator.get('name', 'Unknown')
            indicator_desc = indicator.get('description', '')

            html += f"""
            <li>
                <span class="{indicator_type}"><strong>{indicator_name}</strong></span>
                <p>{indicator_desc}</p>
            </li>
            """

        html += """
            </ul>
        </div>
        """

    # Add URLs section
    if urls:
        html += f"""
        <div class="section">
            <h2>Detected URLs ({len(urls)})</h2>
            <ol>
        """

        for url in urls:
            html += f"<li>{url}</li>"

        html += """
            </ol>
        </div>
        """

    # Add all email headers section if available
    if 'headers' in email_data and isinstance(email_data['headers'], dict):
        html += """
        <div class="section">
            <h2>All Email Headers</h2>
            <table>
        """

        for header, value in email_data['headers'].items():
            html += f"<tr><th>{header}</th><td>{value}</td></tr>\n"

        html += """
            </table>
        </div>
        """

    # Add footer and close HTML
    html += f"""
        <div class="footer">
            <p>Generated by Phishing Detector v1.0.0</p>
            <p>&copy; 2025 {app.current_user}</p>
        </div>
    </body>
    </html>
    """

    # Write to file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html)

def save_text_report(app, file_path):
    """Save report as plain text file"""
    # Get data
    is_phishing = app.analysis_results.get('is_phishing', False)
    probability = app.analysis_results.get('probability', 0.0)
    email_data = app.analysis_results.get('email', {})
    indicators = app.analysis_results.get('indicators', [])
    urls = app.analysis_results.get('extracted_urls', [])

    # Verdict text
    verdict = "PHISHING DETECTED" if is_phishing else "NO PHISHING DETECTED"

    # Create text report
    report = f"""
PHISHING EMAIL ANALYSIS REPORT
Generated on {app.current_datetime}

VERDICT: {verdict}
Phishing Probability: {probability:.1%}

EMAIL DETAILS:
"""

    # Add standard email fields
    for key, value in email_data.items():
        if key != 'headers' and key != 'body':
            report += f"{key.title()}: {value}\n"

    report += f"Source: {app.analysis_results.get('source', 'Manual input')}\n"

    # Add indicators section
    if indicators:
        report += "\nSUSPICIOUS INDICATORS:\n"

        for i, indicator in enumerate(indicators):
            indicator_type = indicator.get('type', 'info').upper()
            indicator_name = indicator.get('name', 'Unknown')
            indicator_desc = indicator.get('description', '')

            report += f"{i + 1}. [{indicator_type}] {indicator_name}\n   {indicator_desc}\n\n"

    # Add URLs section
    if urls:
        report += f"\nDETECTED URLS ({len(urls)}):\n"

        for i, url in enumerate(urls):
            report += f"{i + 1}. {url}\n"

    # Add all email headers section if available
    if 'headers' in email_data and isinstance(email_data['headers'], dict):
        report += "\nALL EMAIL HEADERS:\n"

        for header, value in email_data['headers'].items():
            report += f"{header}: {value}\n"

    # Add footer
    report += f"\nGenerated by Phishing Detector v1.0.0\n© 2025 {app.current_user}"

    # Write to file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(report)