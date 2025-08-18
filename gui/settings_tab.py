"""
Streamlit settings and configuration interface.
Model information, training controls, and app settings.
"""

import streamlit as st
import pandas as pd
import os
import traceback
import webbrowser
from datetime import datetime

def show_settings_tab(app):
    """Show the settings and configuration interface."""
    st.header("⚙️ Settings & Configuration")
    
    # Two-column layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        _show_model_information(app)
        _show_feedback_history(app)
    
    with col2:
        _show_about_section(app)
        _show_app_settings(app)

def _show_model_information(app):
    """Display model information and training controls."""
    st.subheader("🤖 Model Information")
    
    # Model metadata
    model_metadata = getattr(app, 'model_metadata', {})
    
    # Display model details in a nice format
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("**Model Type:**")
        st.write("**Version:**")
        st.write("**Last Updated:**")
        st.write("**Features Used:**")
        st.write("**Training Data:**")
    
    with col2:
        st.write(model_metadata.get("model_type", "Random Forest Classifier"))
        st.write(model_metadata.get("version", "2.0.0"))
        st.write(model_metadata.get("last_updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        st.write(str(model_metadata.get("features_used", 10)))
        st.write(str(model_metadata.get("training_data_size", "Custom datasets")))
    
    # Training controls
    st.write("**Model Training Controls**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Train New Model", type="secondary"):
            _train_new_model(app)
    
    with col2:
        if st.button("📚 Incorporate Feedback", type="secondary"):
            _retrain_with_feedback(app)

def _show_feedback_history(app):
    """Display feedback history."""
    st.subheader("📝 Feedback History")
    
    feedback_file = os.path.join(getattr(app, 'data_dir', 'data'), "feedback", "feedback_log.csv")
    
    if not os.path.exists(feedback_file):
        st.info("No feedback history available yet.")
        return
    
    try:
        df = pd.read_csv(feedback_file)
        
        if len(df) == 0:
            st.info("No feedback records found.")
            return
        
        # Display recent feedback (last 10 entries)
        recent_feedback = df.tail(10).iloc[::-1]  # Most recent first
        
        # Format the dataframe for display
        display_df = recent_feedback[['timestamp', 'original_classification', 'user_feedback', 'source']].copy()
        display_df.columns = ['Timestamp', 'Original', 'Feedback', 'Source']
        
        st.dataframe(display_df, use_container_width=True)
        
        # Summary statistics
        st.write("**Feedback Summary:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_feedback = len(df)
            st.metric("Total Feedback", total_feedback)
        
        with col2:
            if 'user_feedback' in df.columns:
                spam_feedback = (df['user_feedback'] == 'spam').sum()
                st.metric("Marked as Spam", spam_feedback)
        
        with col3:
            if 'user_feedback' in df.columns:
                ham_feedback = (df['user_feedback'] == 'ham').sum()
                st.metric("Marked as Ham", ham_feedback)
        
        # Refresh button
        if st.button("🔄 Refresh Feedback History"):
            st.rerun()
    
    except Exception as e:
        st.error(f"Error loading feedback history: {str(e)}")

def _show_about_section(app):
    """Display about information."""
    st.subheader("ℹ️ About PhishSniffer")
    
    # App info with nice formatting
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <div style="font-size: 48px;">🛡️</div>
        <h3>PhishSniffer</h3>
        <p style="color: #666;">Version 1.0.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("""
    **Advanced email security tool** that uses machine learning to detect phishing attempts. 
    Analyze emails, track suspicious URLs, and protect yourself from cyber threats.
    """)
    
    # Features list
    st.write("**Key Features:**")
    features = [
        "🔍 Email content analysis",
        "🌐 URL reputation checking", 
        "🤖 Machine learning detection",
        "📊 Risk assessment reporting",
        "📈 Analytics and insights",
        "💾 Feedback learning system"
    ]
    
    for feature in features:
        st.write(f"• {feature}")
    
    # Links
    st.write("**Links:**")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📖 Documentation"):
            webbrowser.open("https://github.com/Sharawey74/phishing-detector")
    
    with col2:
        if st.button("🐛 Report Issue"):
            webbrowser.open("https://github.com/Sharawey74/phishing-detector/issues")
    
    # Copyright
    current_user = getattr(app, 'current_user', 'PhishSniffer Team')
    st.caption(f"© 2025 {current_user}")

def _show_app_settings(app):
    """Display application settings."""
    st.subheader("🔧 Application Settings")
    
    # Detection settings
    st.write("**Detection Settings**")
    
    # Risk threshold
    risk_threshold = st.slider(
        "Risk Threshold",
        min_value=0.1,
        max_value=0.9,
        value=0.5,
        step=0.1,
        help="Adjust the sensitivity of phishing detection"
    )
    
    # Auto-save settings
    auto_save = st.checkbox(
        "Auto-save analysis results",
        value=True,
        help="Automatically save email analysis results"
    )
    
    # URL checking
    url_checking = st.checkbox(
        "Enable URL reputation checking",
        value=True,
        help="Check URLs against reputation databases"
    )
    
    # Data management
    st.write("**Data Management**")
    
    # Clear data options
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Analysis History", type="secondary"):
            if st.session_state.get('confirm_clear_history', False):
                # Clear analysis history
                _clear_analysis_history(app)
                st.success("Analysis history cleared")
                st.session_state.confirm_clear_history = False
            else:
                st.session_state.confirm_clear_history = True
                st.warning("Click again to confirm")
    
    with col2:
        if st.button("📤 Export All Data", type="secondary"):
            _export_app_data(app)
    
    # Save settings
    if st.button("💾 Save Settings", type="primary"):
        _save_app_settings(app, {
            'risk_threshold': risk_threshold,
            'auto_save': auto_save,
            'url_checking': url_checking
        })
        st.success("Settings saved successfully!")

def _train_new_model(app):
    """Train a new model."""
    with st.spinner("Training new model... This may take a few minutes."):
        try:
            from model.training import train_custom_model
            
            # Create a placeholder for progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Initializing training process...")
            progress_bar.progress(20)
            
            # Train the model
            result = train_custom_model(app)
            progress_bar.progress(80)
            
            if result:
                status_text.text("Training completed successfully!")
                progress_bar.progress(100)
                st.success("Model training completed successfully!")
                
                # Update app metadata
                if hasattr(app, 'model_metadata'):
                    app.model_metadata['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                st.rerun()
            else:
                st.error("Model training failed. Please check the logs.")
                
        except Exception as e:
            st.error(f"Error during model training: {str(e)}")
            st.write("Please check that all required datasets are available.")

def _retrain_with_feedback(app):
    """Retrain model with user feedback."""
    with st.spinner("Incorporating feedback into model..."):
        try:
            from model.model_feedback import retrain_model_with_feedback
            
            result = retrain_model_with_feedback(app)
            
            if result:
                st.success("Model updated successfully with user feedback!")
                
                # Show feedback stats if available
                if hasattr(app, 'model_metadata') and "feedback_samples_used" in app.model_metadata:
                    feedback_count = app.model_metadata["feedback_samples_used"]
                    st.info(f"Used {feedback_count} feedback samples for model improvement.")
                
                st.rerun()
            else:
                st.warning("Unable to update model with feedback. Please ensure you have provided feedback samples.")
                
        except Exception as e:
            st.error(f"Error during model retraining: {str(e)}")

def _clear_analysis_history(app):
    """Clear analysis history."""
    try:
        # Clear session state
        if hasattr(st.session_state, 'analysis_results'):
            st.session_state.analysis_results = []
        
        # Clear analysis history file if it exists
        analysis_file = os.path.join(getattr(app, 'data_dir', 'data'), 'analysis_history.json')
        if os.path.exists(analysis_file):
            os.remove(analysis_file)
            
    except Exception as e:
        st.error(f"Error clearing analysis history: {str(e)}")

def _export_app_data(app):
    """Export all application data."""
    try:
        import zipfile
        from io import BytesIO
        
        # Create a zip file in memory
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Export analysis history
            analysis_file = os.path.join(getattr(app, 'data_dir', 'data'), 'analysis_history.json')
            if os.path.exists(analysis_file):
                zip_file.write(analysis_file, 'analysis_history.json')
            
            # Export suspicious URLs
            urls_file = os.path.join(getattr(app, 'data_dir', 'data'), 'suspicious_urls.json')
            if os.path.exists(urls_file):
                zip_file.write(urls_file, 'suspicious_urls.json')
            
            # Export feedback history
            feedback_file = os.path.join(getattr(app, 'data_dir', 'data'), 'feedback', 'feedback_log.csv')
            if os.path.exists(feedback_file):
                zip_file.write(feedback_file, 'feedback_log.csv')
        
        zip_buffer.seek(0)
        
        # Provide download
        st.download_button(
            label="📥 Download Export",
            data=zip_buffer.getvalue(),
            file_name=f"phishsniffer_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip"
        )
        
    except Exception as e:
        st.error(f"Error exporting data: {str(e)}")

def _save_app_settings(app, settings):
    """Save application settings."""
    try:
        import json
        
        settings_file = os.path.join(getattr(app, 'data_dir', 'data'), 'settings.json')
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
            
        # Update app settings if the app object has them
        if hasattr(app, 'settings'):
            app.settings.update(settings)
            
    except Exception as e:
        st.error(f"Error saving settings: {str(e)}")

def _load_app_settings(app):
    """Load application settings."""
    try:
        import json
        
        settings_file = os.path.join(getattr(app, 'data_dir', 'data'), 'settings.json')
        
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                
            if hasattr(app, 'settings'):
                app.settings.update(settings)
            else:
                app.settings = settings
                
            return settings
        
        return {}
        
    except Exception as e:
        print(f"Error loading settings: {str(e)}")
        return {}