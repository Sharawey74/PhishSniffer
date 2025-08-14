import numpy as np
import traceback
from model.features import prepare_features_for_model

def run_model(app, features):
    """Run the machine learning model on the features"""
    try:
        # Check if model is loaded
        if app.loaded_model is None:
            print("No model loaded")
            return 0.5  # Default value if no model

        # Ensure features have correct shape
        if features.shape[1] != app.model_feature_count:
            print(f"Feature count mismatch. Expected {app.model_feature_count}, got {features.shape[1]}")
            # Resize features if needed
            new_features = np.zeros((1, app.model_feature_count))
            # Copy as many features as we can
            common_size = min(features.shape[1], app.model_feature_count)
            new_features[0, :common_size] = features[0, :common_size]
            features = new_features

        # Run prediction if model has the predict method
        if hasattr(app.loaded_model, 'predict_proba'):
            # Get probability of phishing class
            prediction = app.loaded_model.predict_proba(features)
            return float(prediction[0][1])  # Probability of phishing (class 1)
        elif hasattr(app.loaded_model, 'predict'):
            # Get binary prediction
            prediction = app.loaded_model.predict(features)
            return float(prediction[0])  # Convert to float for safety
        else:
            # Fallback if model doesn't have predict method
            print("Model doesn't have predict method")
            return 0.5  # Default value

    except Exception as e:
        print(f"Error running model: {str(e)}")
        traceback.print_exc()
        return 0.5  # Default value in case of error

def generate_suspicious_indicators(features):
    """Generate list of suspicious indicators based on features"""
    indicators = []

    # Sender indicators
    if features.get('sender_domain_mismatch', False):
        indicators.append({
            'type': 'critical',
            'name': 'Sender domain mismatch',
            'description': "The email's From, Reply-To, or Return-Path addresses use different domains, which is a common phishing tactic."
        })

    if features.get('sender_display_name_mismatch', False):
        indicators.append({
            'type': 'critical',
            'name': 'Display name spoofing',
            'description': "The sender's display name tries to impersonate a trusted organization that doesn't match the actual email domain."
        })

    if features.get('sender_has_suspicious_words', False):
        indicators.append({
            'type': 'warning',
            'name': 'Suspicious sender name',
            'description': "The sender's name contains terms commonly used in phishing attempts, like 'security', 'support', or 'admin'."
        })

    # URL indicators
    if features.get('has_shortened_urls', False):
        indicators.append({
            'type': 'critical',
            'name': 'Shortened URLs',
            'description': "The email contains shortened URLs that hide the actual destination, a common phishing tactic."
        })

    if features.get('has_ip_urls', False):
        indicators.append({
            'type': 'critical',
            'name': 'IP address URLs',
            'description': "The email contains links with raw IP addresses instead of domain names, which is highly suspicious."
        })

    if features.get('has_suspicious_tlds', False):
        indicators.append({
            'type': 'warning',
            'name': 'Suspicious URL domains',
            'description': "The email contains URLs with suspicious or uncommon top-level domains often used in phishing."
        })

    if features.get('has_url_mismatch', False):
        indicators.append({
            'type': 'critical',
            'name': 'URL display mismatch',
            'description': "The email contains links where the visible text differs from the actual URL destination."
        })

    # Content indicators
    if features.get('subject_has_urgency', False) or features.get('body_has_urgency', False):
        indicators.append({
            'type': 'warning',
            'name': 'Creates false urgency',
            'description': "The email creates a false sense of urgency to pressure you into taking immediate action without thinking."
        })

    if features.get('requests_sensitive_data', False):
        indicators.append({
            'type': 'critical',
            'name': 'Requests sensitive information',
            'description': "The email asks for passwords, account details, or other sensitive personal information."
        })

    if features.get('has_suspicious_claims', False):
        indicators.append({
            'type': 'warning',
            'name': 'Suspicious claims or offers',
            'description': "The email contains claims about prizes, rewards, or offers that are likely fraudulent."
        })

    if features.get('has_poor_grammar', False):
        indicators.append({
            'type': 'info',
            'name': 'Poor grammar or spelling',
            'description': "The email contains grammatical errors or unusual phrasing often seen in phishing attempts."
        })

    if features.get('has_threatening_language', False):
        indicators.append({
            'type': 'warning',
            'name': 'Contains threats or warnings',
            'description': "The email threatens negative consequences if you don't take immediate action."
        })

    return indicators