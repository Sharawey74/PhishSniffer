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
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px; padding: 1.5rem; margin: 1rem 0; color: white;">
        <h1 style="color: white; text-align: center; margin-bottom: 1rem;">📧 Email Analysis</h1>
        <p style="text-align: center; opacity: 0.8;">Advanced AI-powered phishing detection and email security analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Email input section
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 15px; padding: 1rem; margin: 1rem 0; color: white;">
        <h3 style="color: white; margin-bottom: 1rem;">📝 Email Input</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different input methods
    input_method = st.radio(
        "Choose input method:",
        ["Paste Email Content", "Upload .eml File", "Sample Emails"],
        horizontal=True
    )
    
    email_content = ""
    
    if input_method == "Paste Email Content":
        # Add custom CSS for dark themed email input without glowing effects - forced for all users
        st.markdown("""
        <style>
        .stTextArea textarea::placeholder {
            color: #ffffff !important;
            font-weight: normal;
            opacity: 0.8;
        }
        
        .stTextArea textarea {
            color: #ffffff !important;
            font-weight: 600;
            background: #2d3748 !important;
            border: 2px solid #4a5568 !important;
            border-radius: 8px !important;
            padding: 1rem !important;
            outline: none !important;
            box-shadow: none !important;
            text-shadow: none !important;
            transition: border-color 0.2s ease;
        }
        
        .stTextArea textarea:focus {
            background: #2d3748 !important;
            border: 2px solid #3182ce !important;
            outline: none !important;
            box-shadow: none !important;
            text-shadow: none !important;
        }
        
        .stTextArea textarea:hover {
            background: #2d3748 !important;
            border: 2px solid #4a5568 !important;
            box-shadow: none !important;
        }
        
        /* Force dark background for container in all themes */
        .stTextArea {
            background: #2d3748 !important;
        }
        
        /* Override Streamlit's default light mode styles */
        .stTextArea > div {
            background: #2d3748 !important;
        }
        
        /* Ensure dark background persists in all states and themes */
        .stTextArea textarea[data-baseweb="textarea"] {
            background: #2d3748 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
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
                
                # Extract and store URLs from email content
                extracted_urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', email_content)
                
                # Store URLs in the result for consistency
                if 'extracted_urls' not in result:
                    result['extracted_urls'] = extracted_urls
                
                # Also store in details for display consistency
                if 'details' not in result:
                    result['details'] = {}
                result['details']['extracted_urls'] = extracted_urls
                result['details']['email_content'] = email_content
                
                # Update features detected to accurately reflect URL count
                if 'details' in result and 'features_detected' in result['details']:
                    features = result['details']['features_detected']
                    # Update or add URL count feature
                    url_count = len(extracted_urls)
                    url_feature = f"Contains {url_count} URL(s)" if url_count > 0 else "No URLs detected"
                    
                    # Replace any existing URL count feature or add new one
                    updated_features = []
                    url_feature_added = False
                    for feature in features:
                        if "URL(s)" in feature or "urls" in feature.lower():
                            updated_features.append(url_feature)
                            url_feature_added = True
                        else:
                            updated_features.append(feature)
                    
                    if not url_feature_added and url_count > 0:
                        updated_features.append(url_feature)
                    
                    result['details']['features_detected'] = updated_features
                
                if extracted_urls:
                    for url in extracted_urls:
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
    """Display the analysis results with enhanced styling."""
    st.markdown('<div class="analysis-result">', unsafe_allow_html=True)
    
    # Enhanced Header with proper date formatting
    analysis_time = result.get('timestamp')
    if analysis_time:
        try:
            # Parse the ISO format timestamp and format it nicely
            if isinstance(analysis_time, str):
                from datetime import datetime
                dt = datetime.fromisoformat(analysis_time.replace('T', ' '))
                formatted_date = dt.strftime("%B %d, %Y at %I:%M %p")
            else:
                formatted_date = analysis_time
        except:
            formatted_date = str(analysis_time)
    else:
        formatted_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #1e3c72; margin-bottom: 0.5rem;">� Analysis Report</h2>
        <h3 style="color: #64748b; font-weight: 500; margin-bottom: 0.5rem;">📧 Email Security Analysis</h3>
        <div class="analysis-date">Analysis Date: {formatted_date}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main verdict with enhanced styling
    probability = result.get('probability', 0)
    is_phishing = result['is_phishing']
    
    if is_phishing:
        risk_class = "risk-high"
        icon = "🚨"
        title = "PHISHING DETECTED"
        level = "HIGH RISK"
        recommendation = "⚠️ Do NOT click any links, download attachments, or reply to this email. Report to IT security immediately."
    else:
        if probability > 0.3:
            risk_class = "risk-medium"
            icon = "⚠️"
            title = "SUSPICIOUS CONTENT"
            level = "MEDIUM RISK"
            recommendation = "⚡ Exercise caution. Verify sender identity before taking any action."
        else:
            risk_class = "risk-low"
            icon = "✅"
            title = "EMAIL APPEARS SAFE"
            level = "LOW RISK"
            recommendation = "✓ Email appears legitimate, but always remain vigilant."
    
    st.markdown(f"""
    <div class="{risk_class}">
        <h3 style="margin: 0; font-size: 1.5rem;">{icon} {title}</h3>
        <p style="margin: 0.5rem 0; font-size: 1.1rem;"><strong>Risk Level:</strong> {level}</p>
        <p style="margin: 0.5rem 0; font-size: 1.1rem;"><strong>Confidence:</strong> {probability:.1%}</p>
        <p style="margin: 1rem 0 0 0; font-size: 1rem;">{recommendation}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced Probability visualization
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Create an enhanced gauge chart with proper colors
        import plotly.graph_objects as go
        
        # Determine color based on risk level - match the risk indicators
        if probability >= 0.7:
            gauge_color = "#ff6b6b"  # Red for high risk
            risk_level = "HIGH"
        elif probability >= 0.3:
            gauge_color = "#ffd43b"  # Yellow for medium risk  
            risk_level = "MEDIUM"
        else:
            gauge_color = "#51cf66"  # Green for low risk
            risk_level = "LOW"
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = probability * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Risk Level: {risk_level}", 'font': {'size': 18, 'color': '#FFFFFF'}},
            delta = {'reference': 50, 'suffix': '%', 'font': {'color': '#FFFFFF'}},
            number = {'font': {'size': 24, 'color': gauge_color}},
            gauge = {
                'axis': {
                    'range': [None, 100],
                    'tickwidth': 2,
                    'tickcolor': "#FFFFFF",
                    'tickfont': {'size': 12, 'color': '#FFFFFF'}
                },
                'bar': {'color': gauge_color, 'thickness': 0.8},
                'bgcolor': "rgba(255,255,255,0.1)",
                'borderwidth': 3,
                'bordercolor': "#FFFFFF",
                'steps': [
                    {'range': [0, 30], 'color': "rgba(81, 207, 102, 0.3)"},
                    {'range': [30, 70], 'color': "rgba(255, 212, 59, 0.3)"},
                    {'range': [70, 100], 'color': "rgba(255, 107, 107, 0.3)"}
                ],
                'threshold': {
                    'line': {'color': "#FFFFFF", 'width': 3},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        
        fig.update_layout(
            height=350,
            font={'color': "#FFFFFF", 'family': "Inter"},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Enhanced metrics display
        st.markdown("""
        <div class="content-card">
            <h4 style="color: #1e3c72; margin-bottom: 1rem;">📈 Analysis Metrics</h4>
        </div>
        """, unsafe_allow_html=True)
        
        details = result.get('details', {})
        confidence = details.get('confidence_level', 'Unknown')
        
        # Create enhanced metrics
        col2_1, col2_2 = st.columns(2)
        
        with col2_1:
            st.metric(
                "Confidence Level", 
                confidence,
                help="How confident the model is in its prediction"
            )
            st.metric(
                "Risk Score", 
                f"{probability:.3f}",
                help="Numerical risk score (0-1)"
            )
        
        with col2_2:
            classification = "⚠️ Phishing" if is_phishing else "✅ Legitimate"
            st.metric(
                "Classification", 
                classification,
                help="Final classification result"
            )
            
            # Calculate risk percentage for display
            risk_percent = f"{probability*100:.1f}%"
            st.metric(
                "Risk Level", 
                risk_percent,
                help="Percentage risk assessment"
            )
    
    # Enhanced Detailed Analysis Section
    st.markdown("""
    <div class="content-card">
        <h4 style="color: #1e3c72; margin-bottom: 1rem;">🔍 Detailed Analysis</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different analysis aspects
    detail_tab1, detail_tab2, detail_tab3 = st.tabs(["🚨 Risk Factors", "🔍 Features Detected", "🌐 URLs Found"])
    
    with detail_tab1:
        risk_factors = details.get('risk_factors', [])
        if risk_factors:
            st.markdown("**Identified Risk Factors:**")
            for i, factor in enumerate(risk_factors, 1):
                st.markdown(f"""
                <div style="background: rgba(255, 107, 107, 0.1); padding: 0.8rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid #ff6b6b;">
                    <strong>{i}.</strong> {factor}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("✅ No specific risk factors detected in this email.")
    
    with detail_tab2:
        features = details.get('features_detected', [])
        if features:
            st.markdown("**Features Detected:**")
            for i, feature in enumerate(features, 1):
                st.markdown(f"""
                <div style="background: rgba(102, 126, 234, 0.1); padding: 0.8rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid #667eea;">
                    <strong>{i}.</strong> {feature}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ No suspicious features detected.")
    
    with detail_tab3:
        # Get URLs from result data for consistency
        extracted_urls = result.get('extracted_urls', [])
        
        # Also check details for backward compatibility
        if not extracted_urls and 'details' in result:
            extracted_urls = result['details'].get('extracted_urls', [])
        
        # Fallback: extract from email content if available
        if not extracted_urls:
            email_content = result.get('email_content', '')
            if not email_content and 'details' in result:
                email_content = result['details'].get('email_content', '')
            
            if email_content:
                extracted_urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', str(email_content))
        
        if extracted_urls:
            st.markdown("**URLs Found in Email:**")
            
            # Create a proper table display for URLs
            url_data = []
            for i, url in enumerate(extracted_urls, 1):
                # Determine URL risk based on analysis result
                url_risk = "High" if is_phishing else ("Medium" if probability > 0.3 else "Low")
                risk_color = "#ff6b6b" if url_risk == "High" else ("#ffd43b" if url_risk == "Medium" else "#51cf66")
                
                # Extract domain for better display
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc or "Unknown"
                except:
                    domain = "Unknown"
                
                url_data.append({
                    '#': i,
                    'URL': url,
                    'Domain': domain,
                    'Risk Level': url_risk
                })
            
            # Display as dataframe for better formatting
            df = pd.DataFrame(url_data)
            st.dataframe(df, use_container_width=True)
            
            # Also show individual URL cards for detailed view
            st.markdown("**Detailed URL Analysis:**")
            for i, url in enumerate(extracted_urls, 1):
                url_risk = "High" if is_phishing else ("Medium" if probability > 0.3 else "Low")
                risk_color = "#ff6b6b" if url_risk == "High" else ("#ffd43b" if url_risk == "Medium" else "#51cf66")
                
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); padding: 1rem; margin: 0.5rem 0; border-radius: 8px; color: #FFFFFF;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 0; margin-right: 1rem;">
                            <strong style="color: #FFFFFF;">{i}.</strong> <code style="background: rgba(255,255,255,0.1); padding: 0.2rem 0.5rem; border-radius: 4px; color: #FFFFFF; word-break: break-all;">{url}</code>
                        </div>
                        <div style="background: {risk_color}; color: white; padding: 0.3rem 0.8rem; border-radius: 12px; font-size: 0.8rem; white-space: nowrap;">
                            {url_risk} Risk
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🔗 No URLs found in this email.")
    
    # Enhanced Feedback Section
    st.markdown("""
    <div class="content-card">
        <h4 style="color: #1e3c72; margin-bottom: 1rem;">💬 Help Us Improve</h4>
        <p style="color: #64748b; margin-bottom: 1rem;">Your feedback helps train our AI to become more accurate:</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🚨 Report Phishing", use_container_width=True, help="Mark this email as phishing"):
            st.success("✅ Reported as phishing. Thank you for helping improve our detection!")
    
    with col2:
        if st.button("✅ Mark as Safe", use_container_width=True, help="Confirm this email is legitimate"):
            st.success("✅ Marked as safe. Thank you for the feedback!")
    
    with col3:
        if st.button("❓ Uncertain", use_container_width=True, help="Not sure about this classification"):
            st.info("📝 Uncertainty noted. We'll review this case for improvement.")
    
    # Enhanced timestamp with proper styling
    st.markdown(f"""
    <div style="text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e9ecef;">
        <div class="analysis-date">Analysis completed on {formatted_date}</div>
    </div>
    """, unsafe_allow_html=True)

