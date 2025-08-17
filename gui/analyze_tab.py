"""
Streamlit email analysis interface.
Provides email input, analysis, and results display.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import re
import traceback

from storage.history import update_analysis_history
from storage.urls import save_suspicious_urls

def show_analyze_tab(app):
    """Show the email analysis interface."""
    st.header("📧 Email Analysis")
    
    # Email input section
    st.subheader("Email Input")
    
    # Tabs for different input methods
    input_method = st.radio(
        "Choose input method:",
        ["Paste Email Content", "Upload .eml File", "Sample Emails"],
        horizontal=True
    )
    
    email_content = ""
    
    if input_method == "Paste Email Content":
        email_content = st.text_area(
            "Paste the email content here:",
            height=300,
            placeholder="Paste the raw email including headers, or just the message body.\nFor best results, include as much of the original email as possible."
        )
    
    elif input_method == "Upload .eml File":
        uploaded_file = st.file_uploader(
            "Choose a .eml file",
            type=['eml', 'txt'],
            help="Upload an email file (.eml) or text file containing the email"
        )
        
        if uploaded_file is not None:
            try:
                # Read the file content
                email_content = str(uploaded_file.read(), "utf-8")
                st.success(f"✓ Loaded file: {uploaded_file.name}")
                
                # Show preview
                with st.expander("Preview email content"):
                    st.text_area("Email content:", email_content, height=200, disabled=True)
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    elif input_method == "Sample Emails":
        sample_choice = st.selectbox(
            "Choose a sample email:",
            ["Phishing - Amazon Gift Card Scam", "Phishing - Bank Alert", "Legitimate - Newsletter", "Legitimate - Receipt"]
        )
        
        sample_emails = {
            "Phishing - Amazon Gift Card Scam": """From: Amazon Rewards <promo@amazon-prizes.club>
Reply-To: claim@amazonfreegift.co
Return-Path: winner@amazon-prizes.club
Subject: 🎁 Congratulations! You've Won a $500 Amazon Gift Card

Hello,

You've been selected to receive a $500 Amazon Gift Card. This offer is available for a limited time only.

To claim your reward, please click the link below:
https://bit.ly/3FreeReward

Act now before the offer expires!

Sincerely,
Amazon Promotions Team""",
            
            "Phishing - Bank Alert": """From: Security Alert <security@your-bank.com>
Subject: Urgent: Suspicious Activity Detected
Date: Mon, 15 Aug 2025 10:30:00 +0000

Dear Valued Customer,

We have detected unusual activity on your account. Your account will be suspended within 24 hours unless you verify your credentials immediately.

Click here to verify: http://192.168.0.1/login

If you do not take action immediately, your account will be permanently closed.

Bank Security Team""",
            
            "Legitimate - Newsletter": """From: TechNews Daily <newsletter@technews.com>
Subject: Weekly Tech Roundup - August 2025
Date: Mon, 15 Aug 2025 09:00:00 +0000

Hi there,

Here are this week's top tech stories:

1. AI Breakthrough in Medical Diagnosis
2. New Smartphone Features for 2025
3. Cybersecurity Trends to Watch

Read more at: https://technews.com/weekly-roundup

Best regards,
The TechNews Team

Unsubscribe: https://technews.com/unsubscribe""",
            
            "Legitimate - Receipt": """From: orders@company.com
Subject: Your Order Confirmation #12345
Date: Mon, 15 Aug 2025 14:20:00 +0000

Thank you for your order!

Order #12345
Date: August 15, 2025
Total: $49.99

Items:
- Product XYZ (Qty: 1) - $49.99

Shipping Address:
123 Main St
City, State 12345

Estimated Delivery: August 18, 2025

Track your order: https://company.com/track/12345

Customer Service: support@company.com"""
        }
        
        email_content = sample_emails[sample_choice]
        
        with st.expander("Preview sample email"):
            st.text_area("Email content:", email_content, height=200, disabled=True)
    
    # Analysis section
    st.subheader("Analysis")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        analyze_button = st.button("🔍 Analyze Email", type="primary", use_container_width=True)
    
    with col2:
        threshold = st.slider("Threshold", 0.0, 1.0, 0.5, 0.05, help="Classification threshold for phishing detection")
        app.predictor.set_threshold(threshold)
    
    with col3:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.session_state.analysis_results = None
        st.rerun()
    
    # Perform analysis
    if analyze_button and email_content.strip():
        with st.spinner("Analyzing email..."):
            try:
                # Perform prediction
                result = app.predictor.predict_single(email_content, return_details=True)
                
                # Store result in session state
                st.session_state.analysis_results = result
                
                # Update history
                update_analysis_history(
                    app.history_file,
                    "manual input",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    result['is_phishing'],
                    result.get('probability', 0.5)
                )
                
                # Extract and store URLs
                urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', email_content)
                if urls:
                    for url in urls:
                        url_entry = {
                            'url': url,
                            'source': 'email analysis',
                            'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'risk_level': 'High' if result['is_phishing'] else 'Medium'
                        }
                        
                        # Check if URL already exists
                        if not any(entry.get('url') == url for entry in st.session_state.suspicious_urls):
                            st.session_state.suspicious_urls.append(url_entry)
                    
                    # Save updated URLs
                    save_suspicious_urls(app.urls_file, st.session_state.suspicious_urls)
                
                st.success("✓ Analysis completed!")
                
            except Exception as e:
                st.error(f"Error during analysis: {e}")
                traceback.print_exc()
    
    elif analyze_button and not email_content.strip():
        st.warning("Please enter email content before analyzing.")
    
    # Display results
    if st.session_state.analysis_results:
        _display_analysis_results(st.session_state.analysis_results)

def _display_analysis_results(result):
    """Display the analysis results."""
    st.subheader("📊 Analysis Results")
    
    # Main verdict
    probability = result.get('probability', 0)
    is_phishing = result['is_phishing']
    
    if is_phishing:
        st.markdown(f"""
        <div class="risk-high">
            <h3>🚨 PHISHING DETECTED</h3>
            <p><strong>Risk Level:</strong> HIGH</p>
            <p><strong>Confidence:</strong> {probability:.1%}</p>
            <p><strong>Recommendation:</strong> Do NOT click any links, download attachments, or reply to this email.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="risk-low">
            <h3>✅ NO PHISHING DETECTED</h3>
            <p><strong>Risk Level:</strong> LOW</p>
            <p><strong>Confidence:</strong> {(1-probability):.1%}</p>
            <p><strong>Recommendation:</strong> Email appears legitimate, but always exercise caution.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Probability gauge
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Create a gauge chart
        import plotly.graph_objects as go
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = probability * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Phishing Probability (%)"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "red" if is_phishing else "green"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Confidence level and details
        details = result.get('details', {})
        confidence = details.get('confidence_level', 'Unknown')
        
        st.metric("Confidence Level", confidence)
        st.metric("Prediction Score", f"{probability:.3f}")
        st.metric("Classification", "Phishing" if is_phishing else "Legitimate")
    
    # Detailed analysis
    if details:
        st.subheader("🔍 Detailed Analysis")
        
        # Risk factors
        risk_factors = details.get('risk_factors', [])
        if risk_factors:
            st.write("**Risk Factors Found:**")
            for factor in risk_factors:
                st.write(f"• {factor}")
        
        # Features detected
        features = details.get('features_detected', [])
        if features:
            st.write("**Features Detected:**")
            for feature in features:
                st.write(f"• {feature}")
        
        if not risk_factors and not features:
            st.info("No specific risk factors or suspicious features detected.")
    
    # Feedback section
    st.subheader("💬 Feedback")
    st.write("Help us improve by providing feedback on this analysis:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Report as Phishing 🚨", use_container_width=True):
            st.success("Thank you for reporting this as phishing. This feedback will help improve our model.")
    
    with col2:
        if st.button("Mark as Safe ✅", use_container_width=True):
            st.success("Thank you for confirming this email is safe. This feedback will help improve our model.")
    
    # Timestamp
    st.caption(f"Analysis performed at: {result.get('timestamp', 'Unknown')}")

