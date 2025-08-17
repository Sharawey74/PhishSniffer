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
    """Show the analysis report interface."""
    st.header("📊 Analysis Report")
    
    # Check if we have analysis results
    if not st.session_state.analysis_results:
        st.info("No analysis results available. Please analyze an email first.")
        
        if st.button("🔍 Go to Analysis"):
            st.session_state.current_tab = "Analyze"
            st.rerun()
        return
    
    result = st.session_state.analysis_results
    
    # Report header
    st.subheader("📧 Email Analysis Summary")
    
    # Basic information
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Analysis Date", result.get('timestamp', 'Unknown'))
    
    with col2:
        st.metric("Source", result.get('source', 'Unknown'))
    
    with col3:
        confidence = result.get('probability', 0)
        st.metric("Confidence Score", f"{confidence:.1%}")
    
    # Main verdict with styling
    probability = result.get('probability', 0)
    is_phishing = result['is_phishing']
    
    if is_phishing:
        st.markdown(f"""
        <div class="alert-danger">
            <h2>🚨 PHISHING EMAIL DETECTED</h2>
            <p><strong>Risk Assessment:</strong> HIGH RISK</p>
            <p><strong>Phishing Probability:</strong> {probability:.1%}</p>
            <p><strong>Action Required:</strong> Do NOT interact with this email</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="alert-success">
            <h2>✅ EMAIL APPEARS LEGITIMATE</h2>
            <p><strong>Risk Assessment:</strong> LOW RISK</p>
            <p><strong>Legitimate Probability:</strong> {(1-probability):.1%}</p>
            <p><strong>Recommendation:</strong> Exercise normal caution</p>
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
    """Display risk factors and suspicious indicators."""
    indicators = result.get('indicators', [])
    features = result.get('features', {})
    
    if not indicators:
        st.success("✅ No significant risk factors detected")
        return
    
    st.write("**Suspicious Indicators Found:**")
    
    # Categorize indicators by severity
    critical_indicators = [i for i in indicators if i.get('severity') == 'Critical']
    high_indicators = [i for i in indicators if i.get('severity') == 'High']
    medium_indicators = [i for i in indicators if i.get('severity') == 'Medium']
    low_indicators = [i for i in indicators if i.get('severity') == 'Low']
    
    # Display critical indicators
    if critical_indicators:
        st.markdown("#### 🔴 Critical Risk Factors")
        for indicator in critical_indicators:
            st.error(f"**{indicator['name']}**: {indicator['description']}")
    
    # Display high indicators
    if high_indicators:
        st.markdown("#### 🟠 High Risk Factors")
        for indicator in high_indicators:
            st.warning(f"**{indicator['name']}**: {indicator['description']}")
    
    # Display medium indicators
    if medium_indicators:
        st.markdown("#### 🟡 Medium Risk Factors")
        for indicator in medium_indicators:
            st.info(f"**{indicator['name']}**: {indicator['description']}")
    
    # Display low indicators
    if low_indicators:
        st.markdown("#### 🔵 Low Risk Factors")
        for indicator in low_indicators:
            st.write(f"**{indicator['name']}**: {indicator['description']}")
    
    # Risk factor chart
    if indicators:
        severity_counts = {
            'Critical': len(critical_indicators),
            'High': len(high_indicators),
            'Medium': len(medium_indicators),
            'Low': len(low_indicators)
        }
        
        # Remove zero counts
        severity_counts = {k: v for k, v in severity_counts.items() if v > 0}
        
        if severity_counts:
            fig = px.bar(
                x=list(severity_counts.keys()),
                y=list(severity_counts.values()),
                title="Risk Factors by Severity",
                color=list(severity_counts.keys()),
                color_discrete_map={
                    'Critical': '#ff4444',
                    'High': '#ff8800',
                    'Medium': '#ffbb00',
                    'Low': '#4488ff'
                }
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

def _show_technical_details(result):
    """Display technical analysis details."""
    features = result.get('features', {})
    probability = result.get('probability', 0)
    
    # Model prediction details
    st.markdown("#### 🤖 Model Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Prediction confidence gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = probability * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Phishing Probability (%)"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "red" if probability > 0.5 else "green"},
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
        # Key metrics
        st.metric("Model Confidence", f"{probability:.3f}")
        st.metric("Classification", "Phishing" if result['is_phishing'] else "Legitimate")
        st.metric("Threshold Used", "0.5")
        
        # Feature summary
        total_features = len(features)
        st.metric("Features Analyzed", total_features)
    
    # Feature analysis
    if features:
        st.markdown("#### 📊 Feature Analysis")
        
        # Convert features to displayable format
        feature_data = []
        for key, value in features.items():
            if isinstance(value, (int, float, bool)):
                feature_data.append({
                    'Feature': key.replace('_', ' ').title(),
                    'Value': str(value),
                    'Type': type(value).__name__
                })
        
        if feature_data:
            df = pd.DataFrame(feature_data)
            st.dataframe(df, use_container_width=True)
    
    # Model information
    st.markdown("#### ℹ️ Model Information")
    st.info("""
    **Model Type**: Random Forest Classifier  
    **Training Data**: Phishing email datasets (CEAS, Nigerian Fraud, etc.)  
    **Features**: TF-IDF text features, sender analysis, URL patterns  
    **Accuracy**: ~95% on validation data
    """)
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