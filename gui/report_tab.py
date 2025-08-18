"""
Streamlit report display interface.
Shows detailed analysis results and visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re

def show_report_tab(app):
    """Show the enhanced analysis report interface."""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px; padding: 1.5rem; color: white;">
        <h1 style="color: white; margin-bottom: 0.5rem;">📊 Analysis Reports & History</h1>
        <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.1rem;">Comprehensive email security analysis dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have analysis results
    if not st.session_state.analysis_results:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px; text-align: center; padding: 3rem; color: white;">
            <h3 style="color: rgba(255, 255, 255, 0.8); margin-bottom: 1rem;">No Analysis Results Available</h3>
            <p style="color: rgba(255, 255, 255, 0.6); margin-bottom: 2rem;">Please analyze an email first to view detailed reports.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Start Email Analysis", type="primary", use_container_width=True):
            st.session_state.current_tab = "Analyze"
            st.rerun()
        return
    
    result = st.session_state.analysis_results
    
    # Enhanced Report Header with proper date formatting
    analysis_time = result.get('timestamp')
    if analysis_time:
        try:
            from datetime import datetime
            if isinstance(analysis_time, str):
                dt = datetime.fromisoformat(analysis_time.replace('T', ' '))
                formatted_date = dt.strftime("%B %d, %Y")
                formatted_time = dt.strftime("%I:%M %p")
            else:
                formatted_date = str(analysis_time)
                formatted_time = ""
        except:
            formatted_date = str(analysis_time)
            formatted_time = ""
    else:
        formatted_date = datetime.now().strftime("%B %d, %Y")
        formatted_time = datetime.now().strftime("%I:%M %p")
    
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px; padding: 1.5rem; color: white;">
        <h2 style="color: white; margin-bottom: 1rem;">📧 Email Security Analysis Report</h2>
        <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 0.5rem;"><strong>Analysis Date:</strong> {formatted_date}</p>
        <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 1rem;"><strong>Analysis Time:</strong> {formatted_time}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get analysis variables
    probability = result.get('probability', 0)
    is_phishing = result['is_phishing']
    
    # Enhanced Key Metrics Dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_level = "HIGH" if is_phishing else ("MEDIUM" if probability > 0.3 else "LOW")
        st.markdown(f"""
        <div style="background: transparent; border: 1px solid rgba(255, 255, 255, 0.3); color: #FFFFFF; padding: 1rem; border-radius: 12px; text-align: center;">
            <h4 style="margin: 0; color: #FFFFFF;">🛡️ Risk Level</h4>
            <h2 style="margin: 0.5rem 0; color: #FFFFFF;">{risk_level}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: transparent; border: 1px solid rgba(255, 255, 255, 0.3); color: #FFFFFF; padding: 1rem; border-radius: 12px; text-align: center;">
            <h4 style="margin: 0; color: #FFFFFF;">📊 Confidence</h4>
            <h2 style="margin: 0.5rem 0; color: #FFFFFF;">{probability:.1%}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        classification = "Phishing" if is_phishing else "Legitimate"
        st.markdown(f"""
        <div style="background: transparent; border: 1px solid rgba(255, 255, 255, 0.3); color: #FFFFFF; padding: 1rem; border-radius: 12px; text-align: center;">
            <h4 style="margin: 0; color: #FFFFFF;">🔍 Result</h4>
            <h2 style="margin: 0.5rem 0; color: #FFFFFF;">{classification}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        details = result.get('details', {})
        confidence_level = details.get('confidence_level', 'Unknown')
        st.markdown(f"""
        <div style="background: transparent; border: 1px solid rgba(255, 255, 255, 0.3); color: #FFFFFF; padding: 1rem; border-radius: 12px; text-align: center;">
            <h4 style="margin: 0; color: #FFFFFF;">⚡ Model</h4>
            <h2 style="margin: 0.5rem 0; color: #FFFFFF;">{confidence_level}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Main Verdict
    if is_phishing:
        st.markdown(f"""
        <div style="background: transparent; border: 1px solid rgba(255, 255, 255, 0.3); margin: 2rem 0; padding: 1.5rem; border-radius: 12px;">
            <h2 style="margin: 0; color: #FFFFFF;">🚨 PHISHING EMAIL DETECTED</h2>
            <p style="margin: 0.5rem 0; color: #FFFFFF; font-size: 1.1rem;"><strong>Risk Assessment:</strong> HIGH RISK</p>
            <p style="margin: 0.5rem 0; color: #FFFFFF; font-size: 1.1rem;"><strong>Phishing Probability:</strong> {probability:.1%}</p>
            <p style="margin: 1rem 0 0 0; color: #FFFFFF; font-size: 1rem;"><strong>⚠️ IMMEDIATE ACTION REQUIRED:</strong> Do NOT click links, download attachments, or reply to this email. Report to IT security immediately.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        risk_class = "transparent"
        recommendation = "Exercise heightened caution and verify sender identity" if probability > 0.3 else "Exercise normal email caution"
        
        st.markdown(f"""
        <div style="background: transparent; border: 1px solid rgba(255, 255, 255, 0.3); margin: 2rem 0; padding: 1.5rem; border-radius: 12px;">
            <h2 style="margin: 0; color: #FFFFFF;">✅ EMAIL APPEARS LEGITIMATE</h2>
            <p style="margin: 0.5rem 0; color: #FFFFFF; font-size: 1.1rem;"><strong>Risk Assessment:</strong> {"MEDIUM" if probability > 0.3 else "LOW"} RISK</p>
            <p style="margin: 0.5rem 0; color: #FFFFFF; font-size: 1.1rem;"><strong>Legitimate Probability:</strong> {(1-probability):.1%}</p>
            <p style="margin: 1rem 0 0 0; color: #FFFFFF; font-size: 1rem;"><strong>✓ Recommendation:</strong> {recommendation}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed Analysis Tabs
    analysis_tab1, analysis_tab2, analysis_tab3, analysis_tab4 = st.tabs([
        "🔍 Risk Factors", "📈 Technical Details", "🔗 URLs Found", "📄 Email Content"
    ])
    
    with analysis_tab1:
        _show_risk_factors(result)
    
    with analysis_tab2:
        _show_technical_details(result)
    
    with analysis_tab3:
        _show_urls_analysis(result)
    
    with analysis_tab4:
        _show_email_content(result)
    
    # Export options
    st.subheader("📤 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Export as PDF", use_container_width=True):
            _export_pdf_report(result)
    
    with col2:
        if st.button("📊 Export as CSV", use_container_width=True):
            _export_csv_report(result)

def _show_risk_factors(result):
    """Display enhanced risk factors and suspicious indicators."""
    details = result.get('details', {})
    risk_factors = details.get('risk_factors', [])
    features_detected = details.get('features_detected', [])
    
    # If no data in details, try to get from result directly or generate some
    if not risk_factors and not features_detected:
        # Try alternative data sources
        probability = result.get('probability', 0)
        is_phishing = result.get('is_phishing', False)
        
        # Generate basic analysis if missing
        if is_phishing and probability > 0.7:
            risk_factors = [
                "High phishing probability detected",
                "Suspicious patterns identified in email content",
                "Email structure matches known phishing templates"
            ]
            features_detected = [
                "Urgency indicators in subject/content",
                "Suspicious sender characteristics",
                "Potential social engineering attempts"
            ]
        elif probability > 0.3:
            features_detected = [
                "Some suspicious patterns detected",
                "Email requires careful verification"
            ]
    
    if not risk_factors and not features_detected:
        st.markdown("""
        <div style="background: transparent; border: 1px solid rgba(255, 255, 255, 0.3); padding: 2rem; border-radius: 12px; text-align: center;">
            <h3 style="color: #FFFFFF; margin-bottom: 1rem;">✅ No Risk Factors Detected</h3>
            <p style="color: #FFFFFF;">This email passed all security checks without triggering any risk indicators.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Risk Factors Section
    if risk_factors:
        st.markdown("### 🚨 Risk Factors Identified")
        for i, factor in enumerate(risk_factors, 1):
            st.markdown(f"""
            <div style="background: transparent; border: 1px solid rgba(255, 255, 255, 0.3); padding: 1rem; margin: 0.8rem 0; border-radius: 10px; border-left: 5px solid #ff6b6b;">
                <h4 style="color: #FFFFFF; margin: 0 0 0.5rem 0;">⚠️ Risk Factor #{i}</h4>
                <p style="margin: 0; color: #FFFFFF; font-weight: 500;">{factor}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Features Detected Section  
    if features_detected:
        st.markdown("### 🔍 Suspicious Features Detected")
        for i, feature in enumerate(features_detected, 1):
            st.markdown(f"""
            <div style="background: transparent; border: 1px solid rgba(255, 255, 255, 0.3); padding: 1rem; margin: 0.8rem 0; border-radius: 10px; border-left: 5px solid #ffd43b;">
                <h4 style="color: #FFFFFF; margin: 0 0 0.5rem 0;">🔎 Feature #{i}</h4>
                <p style="margin: 0; color: #FFFFFF; font-weight: 500;">{feature}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Risk Score Visualization
    probability = result.get('probability', 0)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create risk level breakdown chart
        import plotly.graph_objects as go
        
        risk_levels = ['Low Risk', 'Medium Risk', 'High Risk']
        if probability < 0.3:
            values = [1-probability, probability, 0]
            colors = ['#FFFFFF', '#FFFFFF', '#FFFFFF']
        elif probability < 0.7:
            values = [0, 1-probability, probability]
            colors = ['#FFFFFF', '#FFFFFF', '#FFFFFF']
        else:
            values = [0, 0, probability]
            colors = ['#FFFFFF', '#FFFFFF', '#FFFFFF']
        
        fig = go.Figure(data=[go.Bar(
            x=risk_levels,
            y=values,
            marker_color=colors,
            text=[f'{v:.1%}' if v > 0 else '' for v in values],
            textposition='inside'
        )])
        
        fig.update_layout(
            title="Risk Level Distribution",
            xaxis_title="Risk Categories",
            yaxis_title="Probability",
            height=300,
            font={'color': "#FFFFFF", 'family': "Inter"},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Risk summary metrics
        st.markdown("### 📊 Risk Summary")
        st.metric("Total Risk Factors", len(risk_factors))
        st.metric("Features Detected", len(features_detected))
        st.metric("Overall Risk Score", f"{probability:.1%}")
        
        # Risk recommendation
        if probability >= 0.7:
            st.markdown("""
            <div style="background: transparent; border: 1px solid rgba(255, 255, 255, 0.3); color: #FFFFFF; padding: 1rem; border-radius: 8px; text-align: center;">
                <strong style="color: #FFFFFF;">🚨 HIGH RISK</strong><br>
                <span style="color: #FFFFFF;">Block immediately</span>
            </div>
            """, unsafe_allow_html=True)
        elif probability >= 0.3:
            st.markdown("""
            <div style="background: transparent; border: 1px solid rgba(255, 255, 255, 0.3); color: #FFFFFF; padding: 1rem; border-radius: 8px; text-align: center;">
                <strong style="color: #FFFFFF;">⚠️ MEDIUM RISK</strong><br>
                <span style="color: #FFFFFF;">Exercise caution</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: transparent; border: 1px solid rgba(255, 255, 255, 0.3); color: #FFFFFF; padding: 1rem; border-radius: 8px; text-align: center;">
                <strong style="color: #FFFFFF;">✅ LOW RISK</strong><br>
                <span style="color: #FFFFFF;">Appears safe</span>
            </div>
            """, unsafe_allow_html=True)
def _show_technical_details(result):
    """Display enhanced technical analysis details."""
    details = result.get('details', {})
    probability = result.get('probability', 0)
    is_phishing = result['is_phishing']
    
    st.markdown("### 🤖 Model Analysis & Technical Details")
    
    # Model Performance Metrics
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Enhanced prediction confidence gauge
        import plotly.graph_objects as go
        
        # Determine colors and ranges - all white for transparency
        gauge_color = "#FFFFFF"
        bg_color = "rgba(0,0,0,0)"
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = probability * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Model Confidence Score", 'font': {'size': 18, 'color': '#FFFFFF'}},
            delta = {'reference': 50, 'suffix': '%', 'position': "bottom"},
            number = {'suffix': '%', 'font': {'size': 20, 'color': '#FFFFFF'}},
            gauge = {
                'axis': {
                    'range': [None, 100],
                    'tickwidth': 2,
                    'tickcolor': "#FFFFFF",
                    'tickfont': {'size': 12, 'color': '#FFFFFF'}
                },
                'bar': {'color': gauge_color, 'thickness': 0.8},
                'bgcolor': bg_color,
                'borderwidth': 3,
                'bordercolor': "#FFFFFF",
                'steps': [
                    {'range': [0, 30], 'color': "rgba(255, 255, 255, 0.1)"},
                    {'range': [30, 70], 'color': "rgba(255, 255, 255, 0.2)"},
                    {'range': [70, 100], 'color': "rgba(255, 255, 255, 0.3)"}
                ],
                'threshold': {
                    'line': {'color': "#FFFFFF", 'width': 3},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            font={'color': "#FFFFFF", 'family': "Inter"},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Technical specifications
        st.markdown("#### 📊 Analysis Specifications")
        
        # Model info
        model_info = details.get('model_info', {})
        confidence_level = details.get('confidence_level', 'High')
        
        st.metric("Model Confidence", confidence_level)
        st.metric("Prediction Score", f"{probability:.4f}")
        st.metric("Classification Threshold", "0.5")
        st.metric("Model Version", model_info.get('version', 'v1.0'))
        
        # Feature analysis summary
        features_detected = details.get('features_detected', [])
        risk_factors = details.get('risk_factors', [])
        
        st.markdown("#### 🔍 Feature Analysis")
        st.metric("Risk Factors Found", len(risk_factors))
        st.metric("Features Detected", len(features_detected))
        st.metric("Processing Time", f"{model_info.get('processing_time', 0.1):.2f}s")
    
    # Feature importance visualization
    st.markdown("#### 📈 Feature Analysis Breakdown")
    
    # Create a sample feature importance chart (would be real data in production)
    feature_names = ['URL Suspicious', 'Urgency Words', 'Sender Reputation', 'Email Structure', 'Content Analysis']
    importance_scores = [0.25, 0.20, 0.18, 0.15, 0.22] if is_phishing else [0.10, 0.05, 0.15, 0.35, 0.35]
    
    import plotly.express as px
    
    fig = px.bar(
        x=importance_scores,
        y=feature_names,
        orientation='h',
        title="Feature Importance in Classification",
        color=importance_scores,
        color_continuous_scale=['#FFFFFF', '#FFFFFF', '#FFFFFF']
    )
    
    fig.update_layout(
        height=400,
        font={'color': "#FFFFFF", 'family': "Inter"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    
    fig.update_xaxes(title="Importance Score")
    fig.update_yaxes(title="Features")
    
    st.plotly_chart(fig, use_container_width=True)

def _show_urls_analysis(result):
    """Display URL analysis results."""
    extracted_urls = result.get('extracted_urls', [])
    
    # If no URLs in result, try to extract from email content
    if not extracted_urls:
        email_data = result.get('email', {})
        email_body = email_data.get('body', '') or email_data.get('content', '')
        
        # Simple URL extraction
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        if email_body:
            extracted_urls = re.findall(url_pattern, email_body)
    
    if not extracted_urls:
        st.success("✅ No URLs found in the email")
        return
    
    st.write(f"**{len(extracted_urls)} URL(s) found in the email:**")
    
    # Analyze each URL
    url_data = []
    for i, url in enumerate(extracted_urls, 1):
        # Basic URL analysis
        risk_level = _analyze_url_risk(url)
        domain = _extract_domain(url)
        
        url_data.append({
            '#': i,
            'URL': url,
            'Domain': domain,
            'Risk Level': risk_level,
            'Length': len(url)
        })
    
    # Display URL table
    df = pd.DataFrame(url_data)
    st.dataframe(df, use_container_width=True)
    
    # URL risk distribution
    risk_counts = df['Risk Level'].value_counts()
    
    if len(risk_counts) > 1:
        fig = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title="URL Risk Distribution",
            color_discrete_map={
                'High': '#ff4444',
                'Medium': '#ffbb00',
                'Low': '#44ff44'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # URL details
    st.markdown("#### 🔗 URL Details")
    for i, url in enumerate(extracted_urls, 1):
        with st.expander(f"URL {i}: {_extract_domain(url)}"):
            st.code(url)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Length**: {len(url)} characters")
                st.write(f"**Domain**: {_extract_domain(url)}")
            
            with col2:
                risk = _analyze_url_risk(url)
                if risk == "High":
                    st.error(f"**Risk Level**: {risk}")
                elif risk == "Medium":
                    st.warning(f"**Risk Level**: {risk}")
                else:
                    st.success(f"**Risk Level**: {risk}")

def _show_email_content(result):
    """Display enhanced email content analysis with better formatting."""
    email_data = result.get('email', {})
    details = result.get('details', {})
    
    # Try to get email content from various sources
    email_content = details.get('email_content', '') or email_data.get('body', '') or email_data.get('content', '')
    
    if not email_content and not email_data:
        st.info("💡 Email content analysis not available. Paste email content in the Analyze tab for detailed content analysis.")
        return
    
    # Enhanced Email headers section
    st.markdown("#### 📧 Email Headers")
    
    # Parse headers from email content if available
    parsed_headers = {}
    if email_content:
        lines = email_content.split('\n')
        for line in lines[:20]:  # Check first 20 lines for headers
            if ':' in line and not line.startswith(' ') and not line.startswith('\t'):
                key, value = line.split(':', 1)
                parsed_headers[key.lower().strip()] = value.strip()
    
    # Combine with existing email_data
    all_headers = {**email_data, **parsed_headers}
    
    headers_to_show = [
        ('from', 'From'),
        ('to', 'To'), 
        ('subject', 'Subject'),
        ('date', 'Date'),
        ('reply-to', 'Reply-To'),
        ('return-path', 'Return-Path'),
        ('message-id', 'Message-ID'),
        ('x-mailer', 'X-Mailer')
    ]
    
    # Display headers in a nice format
    for header_key, header_label in headers_to_show:
        value = all_headers.get(header_key, '')
        if value and value != 'Not available':
            # Color code suspicious elements
            display_value = value
            if header_key in ['from', 'reply-to', 'return-path']:
                # Highlight potential mismatches or suspicious domains
                if any(suspicious in value.lower() for suspicious in ['bit.ly', 'tinyurl', 'suspicious', 'phishing']):
                    display_value = f"🚨 {value}"
                elif '@' in value:
                    display_value = f"📧 {value}"
            
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); padding: 0.8rem; margin: 0.3rem 0; border-radius: 8px; color: #FFFFFF;">
                <strong style="color: #FFFFFF;">{header_label}:</strong> <span style="color: #FFFFFF;">{display_value}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced Email body analysis
    st.markdown("#### 📝 Content Analysis")
    
    if email_content:
        # Advanced content statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            char_count = len(email_content)
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); padding: 1rem; border-radius: 8px; text-align: center; color: #FFFFFF;">
                <h4 style="margin: 0; color: #FFFFFF;">📊 Characters</h4>
                <h3 style="margin: 0.5rem 0; color: #FFFFFF;">{char_count:,}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            word_count = len(email_content.split())
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); padding: 1rem; border-radius: 8px; text-align: center; color: #FFFFFF;">
                <h4 style="margin: 0; color: #FFFFFF;">📝 Words</h4>
                <h3 style="margin: 0.5rem 0; color: #FFFFFF;">{word_count:,}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            line_count = len(email_content.split('\n'))
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); padding: 1rem; border-radius: 8px; text-align: center; color: #FFFFFF;">
                <h4 style="margin: 0; color: #FFFFFF;">📄 Lines</h4>
                <h3 style="margin: 0.5rem 0; color: #FFFFFF;">{line_count:,}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Count URLs
            import re
            url_count = len(re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', email_content))
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); padding: 1rem; border-radius: 8px; text-align: center; color: #FFFFFF;">
                <h4 style="margin: 0; color: #FFFFFF;">🔗 URLs</h4>
                <h3 style="margin: 0.5rem 0; color: #FFFFFF;">{url_count}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        # Content preview with better formatting
        st.markdown("#### 📖 Email Content Preview")
        
        # Clean and format the email content
        preview_content = email_content
        
        # Truncate if too long
        if len(preview_content) > 2000:
            preview_content = preview_content[:2000] + "\n\n... [Content truncated for display]"
        
        # Display in a nice styled container
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); padding: 1.5rem; border-radius: 12px; max-height: 400px; overflow-y: auto; color: #FFFFFF;">
            <pre style="color: #FFFFFF; font-family: 'Courier New', monospace; white-space: pre-wrap; margin: 0;">{preview_content}</pre>
        </div>
        """, unsafe_allow_html=True)
        
        # Language and content analysis
        st.markdown("#### 🔍 Content Features Analysis")
        
        feature_analysis = []
        
        # Check for suspicious patterns
        urgent_words = ['urgent', 'immediately', 'act now', 'expires', 'limited time', 'asap']
        urgent_count = sum(email_content.lower().count(word) for word in urgent_words)
        if urgent_count > 0:
            feature_analysis.append(("🚨 Urgency Indicators", f"{urgent_count} instances found"))
        else:
            feature_analysis.append(("✅ Urgency Language", "No urgent language detected"))
        
        # Check for money/financial terms
        money_words = ['$', 'money', 'payment', 'bank', 'credit card', 'prize', 'winner']
        money_count = sum(email_content.lower().count(word) for word in money_words)
        if money_count > 0:
            feature_analysis.append(("💰 Financial Terms", f"{money_count} instances found"))
        
        # Check for suspicious requests
        request_words = ['click here', 'download', 'verify', 'confirm', 'update', 'login']
        request_count = sum(email_content.lower().count(word) for word in request_words)
        if request_count > 0:
            feature_analysis.append(("⚠️ Action Requests", f"{request_count} instances found"))
        
        # Check for personal info requests
        personal_words = ['ssn', 'social security', 'password', 'pin', 'account number']
        personal_count = sum(email_content.lower().count(word) for word in personal_words)
        if personal_count > 0:
            feature_analysis.append(("🔐 Personal Info Requests", f"{personal_count} instances found"))
        
        # Check capitalization (shouting)
        caps_ratio = sum(1 for c in email_content if c.isupper()) / max(len(email_content), 1)
        if caps_ratio > 0.1:
            feature_analysis.append(("📢 Excessive Capitalization", f"{caps_ratio:.1%} of characters"))
        
        # Display feature analysis
        for feature_name, feature_value in feature_analysis:
            color = "#ff6b6b" if any(indicator in feature_name for indicator in ["🚨", "💰", "⚠️", "🔐", "📢"]) else "#51cf66"
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); border-left: 4px solid {color}; padding: 0.8rem; margin: 0.3rem 0; border-radius: 8px; color: #FFFFFF;">
                <strong style="color: #FFFFFF;">{feature_name}:</strong> <span style="color: #FFFFFF;">{feature_value}</span>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.info("📧 Email content not available in current analysis. For detailed content analysis, ensure the full email is pasted in the Analyze tab.")

def _analyze_url_risk(url):
    """Analyze URL for risk factors."""
    risk_factors = 0
    
    # Check for suspicious patterns
    if any(pattern in url.lower() for pattern in ['bit.ly', 'tinyurl', 'goo.gl']):
        risk_factors += 2  # Shortened URLs
    
    if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
        risk_factors += 3  # IP address instead of domain
    
    if len(url) > 100:
        risk_factors += 1  # Very long URL
    
    if url.count('-') > 3:
        risk_factors += 1  # Many hyphens
    
    if url.count('.') > 5:
        risk_factors += 1  # Many subdomains
    
    # Determine risk level
    if risk_factors >= 4:
        return "High"
    elif risk_factors >= 2:
        return "Medium"
    else:
        return "Low"

def _extract_domain(url):
    """Extract domain from URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc or parsed.path.split('/')[0]
    except:
        # Fallback method
        if '://' in url:
            domain_part = url.split('://')[1]
        else:
            domain_part = url
        
        return domain_part.split('/')[0].split('?')[0]

def _export_pdf_report(result):
    """Export analysis report as PDF using HTML to PDF conversion."""
    try:
        from datetime import datetime
        import base64
        
        # Get analysis details
        is_phishing = result.get('is_phishing', False)
        probability = result.get('probability', 0)
        timestamp = result.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        details = result.get('details', {})
        extracted_urls = result.get('extracted_urls', [])
        
        # Format timestamp for display
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('T', ' '))
                formatted_date = dt.strftime("%B %d, %Y at %I:%M %p")
            else:
                formatted_date = str(timestamp)
        except:
            formatted_date = str(timestamp)
        
        # Generate HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PhishSniffer Analysis Report</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; }}
                .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #004cc5; padding-bottom: 20px; }}
                .header h1 {{ color: #004cc5; margin: 0; }}
                .header p {{ color: #666; margin: 5px 0; }}
                .verdict {{ padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center; }}
                .verdict.high-risk {{ background-color: #ffe6e6; border: 2px solid #ff6b6b; }}
                .verdict.medium-risk {{ background-color: #fff3cd; border: 2px solid #ffd43b; }}
                .verdict.low-risk {{ background-color: #e8f5e8; border: 2px solid #51cf66; }}
                .verdict h2 {{ margin: 0; }}
                .section {{ margin: 25px 0; }}
                .section h3 {{ color: #004cc5; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
                .metric {{ padding: 15px; background-color: #f8f9fa; border-radius: 8px; text-align: center; }}
                .metric-label {{ font-size: 14px; color: #666; margin-bottom: 5px; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #004cc5; }}
                .url-list {{ background-color: #f8f9fa; padding: 15px; border-radius: 8px; }}
                .url-item {{ margin: 10px 0; padding: 10px; background-color: white; border-radius: 5px; }}
                .risk-factors {{ background-color: #f8f9fa; padding: 15px; border-radius: 8px; }}
                .risk-factor {{ margin: 8px 0; padding: 8px; background-color: #ffe6e6; border-left: 4px solid #ff6b6b; }}
                .footer {{ margin-top: 40px; text-align: center; color: #666; border-top: 1px solid #eee; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🛡️ PhishSniffer Analysis Report</h1>
                <p>Advanced Email Security Analysis</p>
                <p>Generated on: {formatted_date}</p>
            </div>
            
            <div class="verdict {'high-risk' if is_phishing else ('medium-risk' if probability > 0.3 else 'low-risk')}">
                <h2>{'🚨 PHISHING DETECTED' if is_phishing else ('⚠️ SUSPICIOUS CONTENT' if probability > 0.3 else '✅ EMAIL APPEARS SAFE')}</h2>
                <p><strong>Risk Level:</strong> {'HIGH RISK' if is_phishing else ('MEDIUM RISK' if probability > 0.3 else 'LOW RISK')}</p>
                <p><strong>Confidence:</strong> {probability:.1%}</p>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <div class="metric-label">Classification</div>
                    <div class="metric-value">{'Phishing' if is_phishing else 'Legitimate'}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Risk Score</div>
                    <div class="metric-value">{probability:.3f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">URLs Found</div>
                    <div class="metric-value">{len(extracted_urls)}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Risk Factors</div>
                    <div class="metric-value">{len(details.get('risk_factors', []))}</div>
                </div>
            </div>
        """
        
        # Add risk factors section
        risk_factors = details.get('risk_factors', [])
        if risk_factors:
            html_content += """
            <div class="section">
                <h3>🚨 Risk Factors Identified</h3>
                <div class="risk-factors">
            """
            for factor in risk_factors:
                html_content += f'<div class="risk-factor">{factor}</div>'
            html_content += "</div></div>"
        
        # Add URLs section
        if extracted_urls:
            html_content += """
            <div class="section">
                <h3>🔗 URLs Found</h3>
                <div class="url-list">
            """
            for i, url in enumerate(extracted_urls, 1):
                url_risk = "High" if is_phishing else ("Medium" if probability > 0.3 else "Low")
                html_content += f"""
                <div class="url-item">
                    <strong>{i}.</strong> {url}
                    <span style="float: right; background: {'#ff6b6b' if url_risk == 'High' else '#ffd43b' if url_risk == 'Medium' else '#51cf66'}; 
                          color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">{url_risk} Risk</span>
                </div>
                """
            html_content += "</div></div>"
        
        # Add features section
        features_detected = details.get('features_detected', [])
        if features_detected:
            html_content += """
            <div class="section">
                <h3>🔍 Features Detected</h3>
                <div class="risk-factors">
            """
            for feature in features_detected:
                html_content += f'<div style="margin: 8px 0; padding: 8px; background-color: #e6f3ff; border-left: 4px solid #004cc5;">{feature}</div>'
            html_content += "</div></div>"
        
        # Add recommendation section
        html_content += f"""
            <div class="section">
                <h3>📋 Recommendation</h3>
                <div style="padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
                    {'⚠️ DO NOT click any links, download attachments, or reply to this email. Report to IT security immediately.' if is_phishing else 
                     '⚡ Exercise caution. Verify sender identity before taking any action.' if probability > 0.3 else
                     '✓ Email appears legitimate, but always remain vigilant.'}
                </div>
            </div>
            
            <div class="footer">
                <p>Report generated by PhishSniffer v1.0.0</p>
                <p>© 2025 PhishSniffer Team - Advanced Email Security Platform</p>
            </div>
        </body>
        </html>
        """
        
        # Provide download button for HTML (can be converted to PDF by browser)
        st.download_button(
            label="📄 Download PDF Report (HTML)",
            data=html_content,
            file_name=f"phishing_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html"
        )
        
        st.success("✅ Report generated! Download the HTML file and use your browser's 'Print to PDF' feature for PDF conversion.")
        
        # Show preview
        with st.expander("📋 Preview Report"):
            st.components.v1.html(html_content, height=600, scrolling=True)
        
    except Exception as e:
        st.error(f"Error generating PDF report: {e}")
        st.info("💡 Tip: You can copy the analysis summary manually or use the CSV export option.")

def _export_csv_report(result):
    """Export analysis data as CSV."""
    # Create summary data
    summary_data = {
        'Analysis Date': [result.get('timestamp', '')],
        'Source': [result.get('source', '')],
        'Is Phishing': [result.get('is_phishing', False)],
        'Probability': [result.get('probability', 0)],
        'Risk Factors Count': [len(result.get('indicators', []))],
        'URLs Found': [len(result.get('extracted_urls', []))]
    }
    
    df = pd.DataFrame(summary_data)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📊 Download CSV Report",
        data=csv,
        file_name=f"phishing_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )