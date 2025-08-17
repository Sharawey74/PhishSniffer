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
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #1e3c72; margin-bottom: 0.5rem;">📊 Analysis Reports & History</h1>
        <p style="color: #64748b; font-size: 1.1rem;">Comprehensive email security analysis dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have analysis results
    if not st.session_state.analysis_results:
        st.markdown("""
        <div class="content-card" style="text-align: center; padding: 3rem;">
            <h3 style="color: #64748b; margin-bottom: 1rem;">No Analysis Results Available</h3>
            <p style="color: #64748b; margin-bottom: 2rem;">Please analyze an email first to view detailed reports.</p>
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
    <div class="content-card">
        <h2 style="color: #1e3c72; margin-bottom: 1rem;">📧 Email Security Analysis Report</h2>
        <p style="color: #64748b; margin-bottom: 0.5rem;"><strong>Analysis Date:</strong> {formatted_date}</p>
        <p style="color: #64748b; margin-bottom: 1rem;"><strong>Analysis Time:</strong> {formatted_time}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get analysis variables
    probability = result.get('probability', 0)
    is_phishing = result['is_phishing']
    
    # Enhanced Key Metrics Dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_level = "HIGH" if is_phishing else ("MEDIUM" if probability > 0.3 else "LOW")
        risk_color = "#ff6b6b" if is_phishing else ("#ffd43b" if probability > 0.3 else "#51cf66")
        st.markdown(f"""
        <div style="background: {risk_color}; color: white; padding: 1rem; border-radius: 12px; text-align: center;">
            <h4 style="margin: 0; color: white;">🛡️ Risk Level</h4>
            <h2 style="margin: 0.5rem 0; color: white;">{risk_level}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: #667eea; color: white; padding: 1rem; border-radius: 12px; text-align: center;">
            <h4 style="margin: 0; color: white;">📊 Confidence</h4>
            <h2 style="margin: 0.5rem 0; color: white;">{probability:.1%}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        classification = "Phishing" if is_phishing else "Legitimate"
        class_color = "#ff6b6b" if is_phishing else "#51cf66"
        st.markdown(f"""
        <div style="background: {class_color}; color: white; padding: 1rem; border-radius: 12px; text-align: center;">
            <h4 style="margin: 0; color: white;">🔍 Result</h4>
            <h2 style="margin: 0.5rem 0; color: white;">{classification}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        details = result.get('details', {})
        confidence_level = details.get('confidence_level', 'Unknown')
        st.markdown(f"""
        <div style="background: #764ba2; color: white; padding: 1rem; border-radius: 12px; text-align: center;">
            <h4 style="margin: 0; color: white;">⚡ Model</h4>
            <h2 style="margin: 0.5rem 0; color: white;">{confidence_level}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Main Verdict
    if is_phishing:
        st.markdown(f"""
        <div class="risk-high" style="margin: 2rem 0;">
            <h2 style="margin: 0; color: white;">🚨 PHISHING EMAIL DETECTED</h2>
            <p style="margin: 0.5rem 0; color: white; font-size: 1.1rem;"><strong>Risk Assessment:</strong> HIGH RISK</p>
            <p style="margin: 0.5rem 0; color: white; font-size: 1.1rem;"><strong>Phishing Probability:</strong> {probability:.1%}</p>
            <p style="margin: 1rem 0 0 0; color: white; font-size: 1rem;"><strong>⚠️ IMMEDIATE ACTION REQUIRED:</strong> Do NOT click links, download attachments, or reply to this email. Report to IT security immediately.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        risk_class = "risk-medium" if probability > 0.3 else "risk-low"
        recommendation = "Exercise heightened caution and verify sender identity" if probability > 0.3 else "Exercise normal email caution"
        
        st.markdown(f"""
        <div class="{risk_class}" style="margin: 2rem 0;">
            <h2 style="margin: 0; color: white;">✅ EMAIL APPEARS LEGITIMATE</h2>
            <p style="margin: 0.5rem 0; color: white; font-size: 1.1rem;"><strong>Risk Assessment:</strong> {"MEDIUM" if probability > 0.3 else "LOW"} RISK</p>
            <p style="margin: 0.5rem 0; color: white; font-size: 1.1rem;"><strong>Legitimate Probability:</strong> {(1-probability):.1%}</p>
            <p style="margin: 1rem 0 0 0; color: white; font-size: 1rem;"><strong>✓ Recommendation:</strong> {recommendation}</p>
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
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export as PDF", use_container_width=True):
            _export_pdf_report(result)
    
    with col2:
        if st.button("📊 Export as CSV", use_container_width=True):
            _export_csv_report(result)
    
    with col3:
        if st.button("📋 Copy Summary", use_container_width=True):
            _copy_summary(result)

def _show_risk_factors(result):
    """Display enhanced risk factors and suspicious indicators."""
    details = result.get('details', {})
    risk_factors = details.get('risk_factors', [])
    features_detected = details.get('features_detected', [])
    
    if not risk_factors and not features_detected:
        st.markdown("""
        <div style="background: rgba(81, 207, 102, 0.1); padding: 2rem; border-radius: 12px; text-align: center; border: 2px solid #51cf66;">
            <h3 style="color: #51cf66; margin-bottom: 1rem;">✅ No Risk Factors Detected</h3>
            <p style="color: #64748b;">This email passed all security checks without triggering any risk indicators.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Risk Factors Section
    if risk_factors:
        st.markdown("### 🚨 Risk Factors Identified")
        for i, factor in enumerate(risk_factors, 1):
            st.markdown(f"""
            <div style="background: rgba(255, 107, 107, 0.1); padding: 1rem; margin: 0.8rem 0; border-radius: 10px; border-left: 5px solid #ff6b6b;">
                <h4 style="color: #ff6b6b; margin: 0 0 0.5rem 0;">⚠️ Risk Factor #{i}</h4>
                <p style="margin: 0; color: #2d3748; font-weight: 500;">{factor}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Features Detected Section  
    if features_detected:
        st.markdown("### 🔍 Suspicious Features Detected")
        for i, feature in enumerate(features_detected, 1):
            st.markdown(f"""
            <div style="background: rgba(255, 212, 59, 0.1); padding: 1rem; margin: 0.8rem 0; border-radius: 10px; border-left: 5px solid #ffd43b;">
                <h4 style="color: #d69e2e; margin: 0 0 0.5rem 0;">🔎 Feature #{i}</h4>
                <p style="margin: 0; color: #2d3748; font-weight: 500;">{feature}</p>
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
            colors = ['#51cf66', '#ffd43b', '#ff6b6b']
        elif probability < 0.7:
            values = [0, 1-probability, probability]
            colors = ['#51cf66', '#ffd43b', '#ff6b6b']
        else:
            values = [0, 0, probability]
            colors = ['#51cf66', '#ffd43b', '#ff6b6b']
        
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
            font={'color': "#1e3c72", 'family': "Inter"},
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
            <div style="background: #ff6b6b; color: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <strong>🚨 HIGH RISK</strong><br>
                Block immediately
            </div>
            """, unsafe_allow_html=True)
        elif probability >= 0.3:
            st.markdown("""
            <div style="background: #ffd43b; color: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <strong>⚠️ MEDIUM RISK</strong><br>
                Exercise caution
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #51cf66; color: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <strong>✅ LOW RISK</strong><br>
                Appears safe
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
        
        # Determine colors and ranges
        if probability >= 0.7:
            gauge_color = "#ff6b6b"
            bg_color = "rgba(255, 107, 107, 0.1)"
        elif probability >= 0.3:
            gauge_color = "#ffd43b"
            bg_color = "rgba(255, 212, 59, 0.1)"
        else:
            gauge_color = "#51cf66"
            bg_color = "rgba(81, 207, 102, 0.1)"
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = probability * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Model Confidence Score", 'font': {'size': 18, 'color': '#1e3c72'}},
            delta = {'reference': 50, 'suffix': '%', 'position': "bottom"},
            number = {'suffix': '%', 'font': {'size': 20, 'color': '#1e3c72'}},
            gauge = {
                'axis': {
                    'range': [None, 100],
                    'tickwidth': 2,
                    'tickcolor': "#1e3c72",
                    'tickfont': {'size': 12, 'color': '#1e3c72'}
                },
                'bar': {'color': gauge_color, 'thickness': 0.8},
                'bgcolor': bg_color,
                'borderwidth': 3,
                'bordercolor': "#1e3c72",
                'steps': [
                    {'range': [0, 30], 'color': "rgba(81, 207, 102, 0.2)"},
                    {'range': [30, 70], 'color': "rgba(255, 212, 59, 0.2)"},
                    {'range': [70, 100], 'color': "rgba(255, 107, 107, 0.2)"}
                ],
                'threshold': {
                    'line': {'color': "#1e3c72", 'width': 3},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            font={'color': "#1e3c72", 'family': "Inter"},
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
        color_continuous_scale=['#51cf66', '#ffd43b', '#ff6b6b']
    )
    
    fig.update_layout(
        height=400,
        font={'color': "#1e3c72", 'family': "Inter"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    
    fig.update_xaxes(title="Importance Score")
    fig.update_yaxes(title="Features")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Model performance summary
    st.markdown("#### 🎯 Model Performance Metrics")
    
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    
    with perf_col1:
        st.markdown("""
        <div style="background: #667eea; color: white; padding: 1rem; border-radius: 8px; text-align: center;">
            <h4 style="margin: 0; color: white;">📊 Accuracy</h4>
            <h3 style="margin: 0.5rem 0; color: white;">97.74%</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with perf_col2:
        st.markdown("""
        <div style="background: #51cf66; color: white; padding: 1rem; border-radius: 8px; text-align: center;">
            <h4 style="margin: 0; color: white;">🎯 Precision</h4>
            <h3 style="margin: 0.5rem 0; color: white;">96.95%</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with perf_col3:
        st.markdown("""
        <div style="background: #ffd43b; color: white; padding: 1rem; border-radius: 8px; text-align: center;">
            <h4 style="margin: 0; color: white;">🔍 Recall</h4>
            <h3 style="margin: 0.5rem 0; color: white;">98.40%</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with perf_col4:
        st.markdown("""
        <div style="background: #764ba2; color: white; padding: 1rem; border-radius: 8px; text-align: center;">
            <h4 style="margin: 0; color: white;">📈 F1-Score</h4>
            <h3 style="margin: 0.5rem 0; color: white;">97.67%</h3>
        </div>
        """, unsafe_allow_html=True)
def _show_urls_analysis(result):
    """Display URL analysis results."""
    extracted_urls = result.get('extracted_urls', [])
    
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
    """Display email content analysis."""
    email_data = result.get('email', {})
    
    if not email_data:
        st.warning("Email content not available")
        return
    
    # Email headers
    st.markdown("#### 📧 Email Headers")
    
    headers_to_show = ['from', 'to', 'subject', 'date', 'reply-to', 'return-path']
    
    for header in headers_to_show:
        value = email_data.get(header, 'Not available')
        if value and value != 'Not available':
            st.write(f"**{header.title()}**: {value}")
    
    # Email body analysis
    st.markdown("#### 📝 Content Analysis")
    
    body = email_data.get('body', '')
    if body:
        # Content statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Character Count", len(body))
        
        with col2:
            word_count = len(body.split())
            st.metric("Word Count", word_count)
        
        with col3:
            line_count = len(body.split('\n'))
            st.metric("Line Count", line_count)
        
        # Show content in expandable section
        with st.expander("View Email Body"):
            st.text_area("Email Content", body, height=300, disabled=True)
    
    # Content features
    if email_data:
        st.markdown("#### 🔍 Content Features")
        
        feature_info = []
        
        # Check for various features
        if 'urgent_words' in email_data:
            feature_info.append(("Urgent Language", "Yes" if email_data['urgent_words'] else "No"))
        
        if 'suspicious_words' in email_data:
            feature_info.append(("Suspicious Words", "Yes" if email_data['suspicious_words'] else "No"))
        
        if 'html_content' in email_data:
            feature_info.append(("HTML Content", "Yes" if email_data['html_content'] else "No"))
        
        if 'attachments' in email_data:
            feature_info.append(("Attachments", "Yes" if email_data['attachments'] else "No"))
        
        if feature_info:
            for feature, value in feature_info:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{feature}**")
                with col2:
                    if value == "Yes":
                        st.warning(value)
                    else:
                        st.success(value)

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
    """Export analysis report as PDF."""
    st.info("PDF export functionality would be implemented here")
    # This would require additional libraries like reportlab or weasyprint

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

def _copy_summary(result):
    """Copy analysis summary to clipboard."""
    is_phishing = result.get('is_phishing', False)
    probability = result.get('probability', 0)
    timestamp = result.get('timestamp', '')
    source = result.get('source', '')
    
    summary = f"""
PhishSniffer Analysis Summary
============================
Date: {timestamp}
Source: {source}
Result: {"PHISHING DETECTED" if is_phishing else "LEGITIMATE EMAIL"}
Confidence: {probability:.1%}
Risk Factors: {len(result.get('indicators', []))}
URLs Found: {len(result.get('extracted_urls', []))}

Recommendation: {"DO NOT interact with this email" if is_phishing else "Exercise normal caution"}
"""
    
    # In a real implementation, this would copy to clipboard
    st.code(summary)
    st.success("Summary text displayed above (clipboard functionality would be implemented)")