"""
Streamlit suspicious URLs management interface.
Displays and manages detected suspicious URLs.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import re

from storage.urls import save_suspicious_urls

def show_urls_tab(app):
    """Show the suspicious URLs management interface."""
    st.header("🔗 Suspicious URLs")
    
    # Load current URLs
    if not hasattr(st.session_state, 'suspicious_urls') or st.session_state.suspicious_urls is None:
        st.session_state.suspicious_urls = []
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_urls = len(st.session_state.suspicious_urls)
        st.metric("Total URLs", total_urls)
    
    with col2:
        high_risk = len([url for url in st.session_state.suspicious_urls if url.get('risk_level') == 'High'])
        st.metric("High Risk", high_risk)
    
    with col3:
        recent_urls = len([url for url in st.session_state.suspicious_urls 
                          if _is_recent(url.get('date_added', ''))])
        st.metric("Added Today", recent_urls)
    
    with col4:
        unique_domains = len(set([_extract_domain(url.get('url', '')) 
                                for url in st.session_state.suspicious_urls]))
        st.metric("Unique Domains", unique_domains)
    
    if not st.session_state.suspicious_urls:
        st.info("No suspicious URLs found yet. URLs will appear here after email analysis.")
        return
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 URL List", "📊 Analytics", "🔍 Search & Filter", "⚙️ Management"])
    
    with tab1:
        _show_url_list()
    
    with tab2:
        _show_analytics()
    
    with tab3:
        _show_search_filter()
    
    with tab4:
        _show_management()

def _show_url_list():
    """Display the main URL list."""
    st.subheader("Detected Suspicious URLs")
    
    if not st.session_state.suspicious_urls:
        st.info("No URLs to display")
        return
    
    # Create DataFrame
    df = pd.DataFrame(st.session_state.suspicious_urls)
    
    # Add domain column
    df['Domain'] = df['url'].apply(_extract_domain)
    
    # Add risk score column
    df['Risk Score'] = df['risk_level'].map({'High': 3, 'Medium': 2, 'Low': 1})
    
    # Sort by date added (newest first)
    df = df.sort_values('date_added', ascending=False)
    
    # Display options
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write(f"**Showing {len(df)} URLs**")
    
    with col2:
        show_full_urls = st.checkbox("Show full URLs", help="Display complete URLs instead of truncated versions")
    
    # Process URLs for display
    display_df = df.copy()
    
    if not show_full_urls:
        display_df['url'] = display_df['url'].apply(lambda x: x[:50] + '...' if len(x) > 50 else x)
    
    # Select columns to display
    display_columns = ['url', 'Domain', 'risk_level', 'source', 'date_added']
    display_df = display_df[display_columns]
    display_df.columns = ['URL', 'Domain', 'Risk Level', 'Source', 'Date Added']
    
    # Style the dataframe
    def color_risk_level(val):
        color = ''
        if val == 'High':
            color = 'background-color: #ffebee'
        elif val == 'Medium':
            color = 'background-color: #fff8e1'
        elif val == 'Low':
            color = 'background-color: #e8f5e8'
        return color
    
    styled_df = display_df.style.applymap(color_risk_level, subset=['Risk Level'])
    st.dataframe(styled_df, use_container_width=True, height=400)
    
    # URL details section
    st.subheader("URL Details")
    
    if len(df) > 0:
        # Select URL for details
        url_options = [f"{i+1}. {_extract_domain(url)}" for i, url in enumerate(df['url'].tolist())]
        selected_idx = st.selectbox("Select URL for details:", range(len(url_options)), 
                                  format_func=lambda x: url_options[x])
        
        if selected_idx is not None:
            selected_url = df.iloc[selected_idx]
            _show_url_details(selected_url)

def _show_url_details(url_data):
    """Show detailed information about a specific URL."""
    url = url_data['url']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Basic Information**")
        st.write(f"**URL:** {url}")
        st.write(f"**Domain:** {_extract_domain(url)}")
        st.write(f"**Risk Level:** {url_data['risk_level']}")
        st.write(f"**Source:** {url_data['source']}")
        st.write(f"**Date Added:** {url_data['date_added']}")
    
    with col2:
        st.write("**URL Analysis**")
        
        # URL length analysis
        url_length = len(url)
        st.write(f"**Length:** {url_length} characters")
        
        if url_length > 100:
            st.warning("⚠️ Very long URL (suspicious)")
        elif url_length > 50:
            st.info("ℹ️ Moderately long URL")
        else:
            st.success("✅ Normal URL length")
        
        # Domain analysis
        domain = _extract_domain(url)
        subdomain_count = domain.count('.') - 1
        
        st.write(f"**Subdomains:** {subdomain_count}")
        
        if subdomain_count > 3:
            st.warning("⚠️ Many subdomains (suspicious)")
        elif subdomain_count > 1:
            st.info("ℹ️ Multiple subdomains")
        else:
            st.success("✅ Simple domain structure")
        
        # Check for suspicious patterns
        suspicious_patterns = []
        
        if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
            suspicious_patterns.append("Uses IP address instead of domain")
        
        if any(pattern in url.lower() for pattern in ['bit.ly', 'tinyurl', 'goo.gl', 't.co']):
            suspicious_patterns.append("URL shortener detected")
        
        if url.count('-') > 3:
            suspicious_patterns.append("Many hyphens in URL")
        
        if suspicious_patterns:
            st.write("**Suspicious Patterns:**")
            for pattern in suspicious_patterns:
                st.warning(f"⚠️ {pattern}")
        else:
            st.success("✅ No obvious suspicious patterns")
    
    # Action buttons
    st.write("**Actions**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚫 Block URL", key=f"block_{url_data.name}"):
            st.success("URL would be added to blocklist")
    
    with col2:
        if st.button("✅ Mark Safe", key=f"safe_{url_data.name}"):
            # Update risk level
            idx = next(i for i, u in enumerate(st.session_state.suspicious_urls) if u['url'] == url)
            st.session_state.suspicious_urls[idx]['risk_level'] = 'Low'
            save_suspicious_urls("data/suspicious_urls.json", st.session_state.suspicious_urls)
            st.success("URL marked as safe")
            st.rerun()
    
    with col3:
        if st.button("🗑️ Remove", key=f"remove_{url_data.name}"):
            # Remove URL
            st.session_state.suspicious_urls = [u for u in st.session_state.suspicious_urls if u['url'] != url]
            save_suspicious_urls("data/suspicious_urls.json", st.session_state.suspicious_urls)
            st.success("URL removed")
            st.rerun()

def _show_analytics():
    """Show URL analytics and visualizations."""
    st.subheader("URL Analytics")
    
    if not st.session_state.suspicious_urls:
        st.info("No data available for analytics")
        return
    
    df = pd.DataFrame(st.session_state.suspicious_urls)
    
    # Risk level distribution
    col1, col2 = st.columns(2)
    
    with col1:
        risk_counts = df['risk_level'].value_counts()
        fig_pie = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title="Risk Level Distribution",
            color_discrete_map={
                'High': '#ff4444',
                'Medium': '#ffbb00',
                'Low': '#44ff44'
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Source distribution
        source_counts = df['source'].value_counts()
        fig_bar = px.bar(
            x=source_counts.index,
            y=source_counts.values,
            title="URLs by Source",
            labels={'x': 'Source', 'y': 'Count'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Timeline analysis
    st.subheader("Timeline Analysis")
    
    # Convert date_added to datetime
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df = df.dropna(subset=['date_added'])
    
    if len(df) > 0:
        # Group by date
        daily_counts = df.groupby(df['date_added'].dt.date).size()
        
        fig_timeline = px.line(
            x=daily_counts.index,
            y=daily_counts.values,
            title="URLs Detected Over Time",
            labels={'x': 'Date', 'y': 'URLs Detected'}
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Domain analysis
    st.subheader("Domain Analysis")
    
    df['domain'] = df['url'].apply(_extract_domain)
    domain_counts = df['domain'].value_counts().head(10)
    
    if len(domain_counts) > 0:
        fig_domains = px.bar(
            x=domain_counts.values,
            y=domain_counts.index,
            orientation='h',
            title="Top 10 Domains",
            labels={'x': 'Count', 'y': 'Domain'}
        )
        st.plotly_chart(fig_domains, use_container_width=True)
    
    # Risk metrics
    st.subheader("Risk Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_url_length = df['url'].str.len().mean()
        st.metric("Average URL Length", f"{avg_url_length:.0f} chars")
    
    with col2:
        high_risk_pct = (df['risk_level'] == 'High').mean() * 100
        st.metric("High Risk URLs", f"{high_risk_pct:.1f}%")
    
    with col3:
        unique_domains = df['domain'].nunique()
        st.metric("Unique Domains", unique_domains)

def _show_search_filter():
    """Show search and filter interface."""
    st.subheader("Search & Filter URLs")
    
    if not st.session_state.suspicious_urls:
        st.info("No URLs to search")
        return
    
    df = pd.DataFrame(st.session_state.suspicious_urls)
    df['domain'] = df['url'].apply(_extract_domain)
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Risk level filter
        risk_levels = ['All'] + list(df['risk_level'].unique())
        selected_risk = st.selectbox("Risk Level", risk_levels)
    
    with col2:
        # Source filter
        sources = ['All'] + list(df['source'].unique())
        selected_source = st.selectbox("Source", sources)
    
    with col3:
        # Date range filter
        date_range = st.selectbox("Date Range", [
            "All Time", "Last 24 Hours", "Last Week", "Last Month"
        ])
    
    # Search box
    search_term = st.text_input("Search URLs or domains:", placeholder="Enter search term...")
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_risk != 'All':
        filtered_df = filtered_df[filtered_df['risk_level'] == selected_risk]
    
    if selected_source != 'All':
        filtered_df = filtered_df[filtered_df['source'] == selected_source]
    
    # Date filtering
    if date_range != "All Time":
        now = datetime.now()
        filtered_df['date_added'] = pd.to_datetime(filtered_df['date_added'], errors='coerce')
        
        if date_range == "Last 24 Hours":
            cutoff = now - pd.Timedelta(days=1)
        elif date_range == "Last Week":
            cutoff = now - pd.Timedelta(weeks=1)
        elif date_range == "Last Month":
            cutoff = now - pd.Timedelta(days=30)
        
        filtered_df = filtered_df[filtered_df['date_added'] >= cutoff]
    
    # Search filtering
    if search_term:
        mask = (
            filtered_df['url'].str.contains(search_term, case=False, na=False) |
            filtered_df['domain'].str.contains(search_term, case=False, na=False) |
            filtered_df['source'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    # Display results
    st.write(f"**Found {len(filtered_df)} URLs matching your criteria**")
    
    if len(filtered_df) > 0:
        # Display filtered results
        display_columns = ['url', 'domain', 'risk_level', 'source', 'date_added']
        display_df = filtered_df[display_columns].copy()
        display_df.columns = ['URL', 'Domain', 'Risk Level', 'Source', 'Date Added']
        
        st.dataframe(display_df, use_container_width=True)
        
        # Export filtered results
        if st.button("📊 Export Filtered Results"):
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"suspicious_urls_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No URLs match your search criteria")

def _show_management():
    """Show URL management interface."""
    st.subheader("URL Management")
    
    # Bulk operations
    st.write("**Bulk Operations**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Clear All URLs", type="secondary"):
            if st.session_state.get('confirm_clear_all', False):
                st.session_state.suspicious_urls = []
                # We'll need to get app.urls_file from somewhere, for now use a default
                st.success("All URLs cleared")
                st.session_state.confirm_clear_all = False
                st.rerun()
            else:
                st.session_state.confirm_clear_all = True
                st.warning("Click again to confirm clearing all URLs")
    
    with col2:
        if st.button("🗑️ Remove Low Risk URLs"):
            original_count = len(st.session_state.suspicious_urls)
            st.session_state.suspicious_urls = [
                url for url in st.session_state.suspicious_urls 
                if url.get('risk_level') != 'Low'
            ]
            removed_count = original_count - len(st.session_state.suspicious_urls)
            st.success(f"Removed {removed_count} low risk URLs")
            st.rerun()
    
    with col3:
        if st.button("📤 Export All URLs"):
            if st.session_state.suspicious_urls:
                df = pd.DataFrame(st.session_state.suspicious_urls)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download All URLs CSV",
                    data=csv,
                    file_name=f"all_suspicious_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No URLs to export")
    
    # Manual URL addition
    st.write("**Add URL Manually**")
    
    with st.form("add_url_form"):
        new_url = st.text_input("URL:", placeholder="https://example.com/suspicious-link")
        new_risk = st.selectbox("Risk Level:", ["High", "Medium", "Low"])
        new_source = st.text_input("Source:", value="Manual Entry")
        
        if st.form_submit_button("Add URL"):
            if new_url:
                # Validate URL format
                if not new_url.startswith(('http://', 'https://')):
                    new_url = 'http://' + new_url
                
                # Check if URL already exists
                if any(url['url'] == new_url for url in st.session_state.suspicious_urls):
                    st.warning("URL already exists in the list")
                else:
                    new_entry = {
                        'url': new_url,
                        'source': new_source,
                        'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'risk_level': new_risk
                    }
                    st.session_state.suspicious_urls.append(new_entry)
                    st.success("URL added successfully")
                    st.rerun()
            else:
                st.error("Please enter a URL")
    
    # Statistics
    st.write("**Statistics**")
    
    if st.session_state.suspicious_urls:
        df = pd.DataFrame(st.session_state.suspicious_urls)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Risk Level Distribution:**")
            risk_counts = df['risk_level'].value_counts()
            for risk, count in risk_counts.items():
                percentage = (count / len(df)) * 100
                st.write(f"- {risk}: {count} ({percentage:.1f}%)")
        
        with col2:
            st.write("**Source Distribution:**")
            source_counts = df['source'].value_counts()
            for source, count in source_counts.items():
                percentage = (count / len(df)) * 100
                st.write(f"- {source}: {count} ({percentage:.1f}%)")

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

def _is_recent(date_str):
    """Check if a date string is from today."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return date_obj.date() == datetime.now().date()
    except:
        return False