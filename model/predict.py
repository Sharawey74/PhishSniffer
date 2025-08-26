"""
Prediction logic for phishing email detection.
Loads trained models and provides prediction interface.
"""

import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class PhishingPredictor:
    """Main prediction class for phishing email detection."""
    
    def __init__(self, model_dir='trained_models'):
        self.model_dir = model_dir
        self.model = None
        self.feature_extractor = None
        self.model_metadata = None
        self.threshold = 0.5  # Default threshold for classification
    
    def load_model(self, model_name=None):
        """Load a trained model and feature extractor."""
        try:
            if not os.path.exists(self.model_dir):
                print(f"⚠️ Model directory not found: {self.model_dir}")
                return self._create_fallback_model()
            
            if model_name is None:
                # Find the most recent model
                model_files = [f for f in os.listdir(self.model_dir) 
                             if f.endswith('.joblib') and not 'feature_extractor' in f]
                if not model_files:
                    print("⚠️ No trained models found, creating fallback model")
                    return self._create_fallback_model()
                
                # Get the most recent model based on filename timestamp
                model_files.sort(reverse=True)
                model_name = model_files[0].replace('.joblib', '')
            
            # Load model
            model_path = os.path.join(self.model_dir, f"{model_name}.joblib")
            if not os.path.exists(model_path):
                print(f"⚠️ Model not found: {model_path}, creating fallback")
                return self._create_fallback_model()
            
            self.model = joblib.load(model_path)
            print(f"✓ Loaded model: {model_path}")
            
            # Load feature extractor
            feature_extractor_path = os.path.join(self.model_dir, f"{model_name}_feature_extractor.joblib")
            if os.path.exists(feature_extractor_path):
                self.feature_extractor = joblib.load(feature_extractor_path)
                print(f"✓ Loaded feature extractor: {feature_extractor_path}")
            else:
                print(f"⚠ Feature extractor not found: {feature_extractor_path}")
            
            # Load metadata
            metadata_path = os.path.join(self.model_dir, f"{model_name}_metadata.json")
            if os.path.exists(metadata_path):
                import json
                with open(metadata_path, 'r') as f:
                    self.model_metadata = json.load(f)
                print(f"✓ Loaded metadata: {metadata_path}")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error loading model: {e}")
            return self._create_fallback_model()
    
    def _create_fallback_model(self):
        """Create a simple fallback model for demo purposes when trained model is not available."""
        print("🔧 Creating fallback model for cloud deployment...")
        
        # Create a simple rule-based model
        class FallbackModel:
            def predict(self, features):
                """Simple rule-based prediction."""
                if hasattr(features, 'shape') and len(features.shape) > 1:
                    predictions = []
                    for i in range(features.shape[0]):
                        # Simple rule-based scoring
                        score = np.mean(features[i]) if features[i].sum() > 0 else 0.1
                        predictions.append(min(score, 1.0))
                    return np.array(predictions)
                else:
                    return np.array([0.3])  # Default low risk
            
            def predict_proba(self, features):
                """Return probabilities for fallback model."""
                predictions = self.predict(features)
                # Convert to probability matrix [legit_prob, phishing_prob]
                result = np.column_stack([1 - predictions, predictions])
                return result
        
        self.model = FallbackModel()
        self.feature_extractor = None  # Will use legacy features
        self.model_metadata = {
            "model_type": "fallback",
            "description": "Simple rule-based fallback model for cloud deployment"
        }
        
        print("✅ Fallback model created successfully")
        return True
    
    def predict(self, texts, return_proba=True):
        """Predict whether emails are phishing or legitimate."""
        if self.model is None:
            raise ValueError("No model loaded. Call load_model() first.")
        
        if isinstance(texts, str):
            texts = [texts]
        
        # Extract features
        if self.feature_extractor is not None:
            features = self.feature_extractor.transform(texts)
        else:
            # Fallback to legacy feature extraction
            features = self._extract_legacy_features(texts)
        
        # Get predictions
        predictions = self.model.predict(features)
        
        results = {
            'predictions': predictions,
            'is_phishing': predictions >= self.threshold
        }
        
        if return_proba and hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(features)
            results['probabilities'] = probabilities[:, 1] if probabilities.shape[1] > 1 else probabilities
        elif return_proba and hasattr(self.model, 'decision_function'):
            scores = self.model.decision_function(features)
            # Convert to probabilities using sigmoid
            results['probabilities'] = 1 / (1 + np.exp(-scores))
        
        return results
    
    def predict_single(self, text, return_details=True):
        """Predict a single email with detailed analysis."""
        result = self.predict([text], return_proba=True)
        
        single_result = {
            'text': text,
            'is_phishing': bool(result['is_phishing'][0]),
            'prediction': float(result['predictions'][0]),
            'timestamp': datetime.now().isoformat()
        }
        
        if 'probabilities' in result:
            single_result['probability'] = float(result['probabilities'][0])
        
        if return_details:
            single_result['details'] = self._generate_prediction_details(text, single_result)
        
        return single_result
    
    def _generate_prediction_details(self, text, prediction_result):
        """Generate detailed analysis of the prediction."""
        details = {
            'features_detected': [],
            'risk_factors': [],
            'confidence_level': 'Low'
        }
        
        text_lower = text.lower()
        
        # Check for various risk factors
        if prediction_result.get('probability', 0) > 0.8:
            details['confidence_level'] = 'High'
        elif prediction_result.get('probability', 0) > 0.6:
            details['confidence_level'] = 'Medium'
        
        # URL analysis
        import re
        urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)
        if urls:
            details['features_detected'].append(f"Contains {len(urls)} URL(s)")
            
            # Check for shortened URLs
            short_domains = ['bit.ly', 'tinyurl', 'goo.gl', 't.co']
            if any(domain in url for url in urls for domain in short_domains):
                details['risk_factors'].append("Contains shortened URLs")
        
        # Urgency keywords
        urgency_words = ['urgent', 'immediately', 'expires', 'act now', 'limited time']
        found_urgency = [word for word in urgency_words if word in text_lower]
        if found_urgency:
            details['risk_factors'].append(f"Urgency language: {', '.join(found_urgency)}")
        
        # Sensitive data requests
        sensitive_words = ['password', 'credit card', 'ssn', 'login']
        found_sensitive = [word for word in sensitive_words if word in text_lower]
        if found_sensitive:
            details['risk_factors'].append(f"Requests sensitive data: {', '.join(found_sensitive)}")
        
        # Money/financial terms
        money_words = ['money', 'payment', 'prize', 'reward', 'gift card']
        found_money = [word for word in money_words if word in text_lower]
        if found_money:
            details['features_detected'].append(f"Financial terms: {', '.join(found_money)}")
        
        return details
    
    def _extract_legacy_features(self, texts):
        """Legacy feature extraction for backward compatibility."""
        features = []
        
        for text in texts:
            text_features = self._get_legacy_text_features(str(text))
            features.append(text_features)
        
        return np.array(features)
    
    def _get_legacy_text_features(self, text):
        """Extract legacy features from text."""
        import re
        
        if pd.isna(text) or text == "":
            return np.zeros(10)
        
        text = str(text).lower()
        features = []
        
        # Feature 1: Suspicious senders
        suspicious_senders = ['paypal', 'bank', 'account', 'security', 'amazon']
        features.append(int(any(sender in text[:500] for sender in suspicious_senders)))
        
        # Feature 2: URLs
        features.append(int(bool(re.search(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text))))
        
        # Feature 3: Shortened URLs
        short_domains = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly']
        features.append(int(any(domain in text for domain in short_domains)))
        
        # Feature 4: IP URLs
        features.append(int(bool(re.search(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text))))
        
        # Feature 5: Urgency words
        urgency_words = ['urgent', 'immediately', 'alert', 'expires']
        features.append(int(any(word in text for word in urgency_words)))
        
        # Feature 6: Sensitive requests
        sensitive_words = ['password', 'credit card', 'ssn', 'login']
        features.append(int(any(word in text for word in sensitive_words)))
        
        # Feature 7: Attachments
        attachment_words = ['attach', 'document', 'file', 'pdf']
        features.append(int(any(word in text for word in attachment_words)))
        
        # Feature 8: Money terms
        money_terms = ['$', 'money', 'payment', 'prize', 'reward']
        features.append(int(any(term in text for term in money_terms)))
        
        # Feature 9: Threats
        threat_terms = ['suspended', 'terminated', 'closed', 'fraud']
        features.append(int(any(term in text for term in threat_terms)))
        
        # Feature 10: Offers
        offer_terms = ['won', 'prize', 'gift', 'reward', 'congratulations']
        features.append(int(any(term in text for term in offer_terms)))
        
        return np.array(features, dtype=float)
    
    def set_threshold(self, threshold):
        """Set the classification threshold."""
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        self.threshold = threshold
        print(f"✓ Classification threshold set to: {threshold}")
    
    def get_model_info(self):
        """Get information about the loaded model."""
        if self.model is None:
            return "No model loaded"
        
        info = {
            'model_type': type(self.model).__name__,
            'threshold': self.threshold,
            'has_feature_extractor': self.feature_extractor is not None,
            'metadata': self.model_metadata
        }
        
        return info

# Legacy functions for backward compatibility
def run_model(app, features):
    """Legacy function - run the machine learning model on the features"""
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
        import traceback
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