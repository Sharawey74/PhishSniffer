import os
import json
import re
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
import traceback
from datetime import datetime

def retrain_model_with_feedback(app):
    """Retrain the model incorporating user feedback"""
    try:
        app.update_status("Retraining model with feedback...", "info")
        
        # Load all feedback samples
        feedback_dir = os.path.join(app.data_dir, "feedback")
        phishing_dir = os.path.join(feedback_dir, "phishing")
        safe_dir = os.path.join(feedback_dir, "safe")
        
        # Check if we have feedback data
        has_phishing = os.path.exists(phishing_dir) and len(os.listdir(phishing_dir)) > 0
        has_safe = os.path.exists(safe_dir) and len(os.listdir(safe_dir)) > 0
        
        if not has_phishing and not has_safe:
            app.update_status("No feedback data available for retraining", "warning")
            return False
            
        # Load existing model
        if not app.loaded_model:
            model_path = os.path.join(app.models_dir, "phishing_detector_model.joblib")
            if os.path.exists(model_path):
                app.loaded_model = joblib.load(model_path)
            else:
                app.update_status("No existing model to update", "error")
                return False
        
        # Extract features and labels from feedback
        X_feedback = []
        y_feedback = []
        
        # Process phishing samples
        if has_phishing:
            print(f"Processing {len(os.listdir(phishing_dir))} phishing samples")
            for filename in os.listdir(phishing_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(phishing_dir, filename)
                    try:
                        with open(file_path, 'r') as file:
                            sample = json.load(file)
                            features = extract_features_from_sample(sample)
                            if features is not None:
                                X_feedback.append(features)
                                y_feedback.append(1)  # Phishing
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
                        traceback.print_exc()
                        continue
        
        # Process safe samples
        if has_safe:
            print(f"Processing {len(os.listdir(safe_dir))} safe samples")
            for filename in os.listdir(safe_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(safe_dir, filename)
                    try:
                        with open(file_path, 'r') as file:
                            sample = json.load(file)
                            features = extract_features_from_sample(sample)
                            if features is not None:
                                X_feedback.append(features)
                                y_feedback.append(0)  # Safe
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
                        traceback.print_exc()
                        continue
        
        # If we have feedback samples, update model
        if len(X_feedback) > 0:
            print(f"Retraining model with {len(X_feedback)} feedback samples")
            
            # Convert to numpy arrays
            X_feedback = np.array(X_feedback)
            y_feedback = np.array(y_feedback)
            
            # Get a copy of the existing model's data if available
            try:
                if hasattr(app.loaded_model, 'estimators_'):
                    # If we're using the same model type (Random Forest), increase weight of feedback samples
                    # by duplicating them to ensure they have strong influence
                    X_feedback = np.vstack([X_feedback, X_feedback, X_feedback])
                    y_feedback = np.hstack([y_feedback, y_feedback, y_feedback])
            except:
                pass
                
            # Create new model with enhanced parameters
            feedback_model = RandomForestClassifier(
                n_estimators=100,  # More estimators for better accuracy
                max_depth=10,      # Allow deeper trees for complex patterns
                min_samples_split=2,
                random_state=42,
                class_weight='balanced'  # Handle class imbalance
            )
            
            # Train on feedback data
            feedback_model.fit(X_feedback, y_feedback)
            
            # Apply special rules to ensure recognition of common phishing patterns
            add_special_phishing_rules(app)
            
            # Save updated model
            model_path = os.path.join(app.models_dir, "phishing_detector_model.joblib")
            joblib.dump(feedback_model, model_path)
            
            # Update app's model
            app.loaded_model = feedback_model
            
            # Lower the phishing threshold to catch more potential threats
            threshold_file = os.path.join(app.config_dir, "detection_threshold.json")
            try:
                with open(threshold_file, 'w') as f:
                    json.dump({"threshold": 0.4}, f)  # Lower threshold to 40%
            except:
                pass
            
            # Update metadata
            app.model_metadata["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            app.model_metadata["feedback_samples_used"] = len(X_feedback)
            app.model_metadata["last_feedback_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            metadata_path = os.path.join(app.models_dir, "model_metadata.json")
            with open(metadata_path, 'w') as file:
                json.dump(app.model_metadata, file, indent=2)
            
            app.update_status(f"Model updated with {len(X_feedback)} feedback samples", "success")
            return True
        else:
            app.update_status("No valid feedback samples found", "warning")
            return False
            
    except Exception as e:
        print(f"Error retraining model: {e}")
        traceback.print_exc()
        app.update_status("Error retraining model", "error")
        return False

def add_special_phishing_rules(app):
    """Add special rules to catch common phishing patterns"""
    rules_file = os.path.join(app.config_dir, "phishing_rules.json")
    
    # Define rules that will override model predictions
    phishing_rules = {
        "rules": [
            {
                "name": "gift_card_scam",
                "description": "Catches gift card scams",
                "conditions": {
                    "subject_contains": ["gift card", "reward", "prize", "won"],
                    "sender_domain_not": ["amazon.com", "paypal.com", "apple.com"],
                    "action": "mark_phishing"
                }
            },
            {
                "name": "domain_mismatch",
                "description": "Detects when From/Reply-To/Return-Path domains don't match",
                "conditions": {
                    "domains_match": False,
                    "action": "mark_phishing"
                }
            },
            {
                "name": "shortened_url",
                "description": "Flags emails with shortened URLs",
                "conditions": {
                    "has_shortened_url": True,
                    "action": "increase_score",
                    "increase_by": 0.3
                }
            }
        ],
        "version": "1.0.0"
    }
    
    # Save rules
    try:
        os.makedirs(os.path.dirname(rules_file), exist_ok=True)
        with open(rules_file, 'w') as file:
            json.dump(phishing_rules, file, indent=2)
    except Exception as e:
        print(f"Error saving phishing rules: {e}")

def extract_features_from_sample(sample):
    """Extract features from a feedback sample"""
    try:
        # Initialize feature vector (10 features)
        features = np.zeros(10)
        
        # Check if this is the Amazon gift card phishing email
        if "email_content" in sample:
            email_content = sample["email_content"].lower()
            subject = sample.get("subject", "").lower()
            
            # Feature 1: Check for suspicious sender/domain patterns
            suspicious_senders = ['amazon', 'paypal', 'bank', 'account', 'security']
            features[0] = 1 if any(sender in email_content[:500] for sender in suspicious_senders) else 0
            
            # Feature 2: Contains URLs
            features[1] = 1 if "http" in email_content else 0
            
            # Feature 3: Contains shortened URLs (higher weight)
            short_domains = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly']
            features[2] = 2 if any(domain in email_content for domain in short_domains) else 0
            
            # Feature 4: Contains IP-based URLs
            features[3] = 1 if re.search(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', email_content) else 0
            
            # Feature 5: Contains urgency words
            urgency_words = ['urgent', 'immediately', 'alert', 'expires', 'act now', 'limited time']
            features[4] = 1 if any(word in email_content for word in urgency_words) else 0
            
            # Feature 6: Requests sensitive data
            sensitive_words = ['password', 'credit card', 'login', 'ssn', 'credentials']
            features[5] = 1 if any(word in email_content for word in sensitive_words) else 0
            
            # Feature 7: Contains attachment mentions
            attachment_words = ['attach', 'document', 'file', 'pdf', 'invoice']
            features[6] = 1 if any(word in email_content for word in attachment_words) else 0
            
            # Feature 8: Contains financial terms
            money_terms = ['$', 'dollar', 'money', 'payment', 'gift card']
            features[7] = 1 if any(term in email_content for term in money_terms) else 0
            
            # Feature 9: Contains threatening language
            threat_terms = ['suspended', 'terminated', 'unusual activity', 'suspicious']
            features[8] = 1 if any(term in email_content for term in threat_terms) else 0
            
            # Feature 10: Contains suspicious offers/claims (higher weight)
            offer_terms = ['won', 'prize', 'gift card', 'reward', 'congratulations']
            features[9] = 2 if any(term in email_content for term in offer_terms) else 0
            
            # Special case for domain mismatch - add extra weight
            if "from" in sample and "reply_to" in sample and sample["from"] != sample["reply_to"]:
                features[0] += 1  # Increase sender suspiciousness
            
            return features
            
        # Try to get pre-extracted features if text analysis fails
        elif "features" in sample and isinstance(sample["features"], dict):
            # Extract standard features from the stored features
            if "sender_domain_mismatch" in sample["features"]:
                features[0] = 2 if sample["features"]["sender_domain_mismatch"] else 0
                
            if "has_urls" in sample["features"]:
                features[1] = 1 if sample["features"]["has_urls"] else 0
                
            if "has_shortened_urls" in sample["features"]:
                features[2] = 2 if sample["features"]["has_shortened_urls"] else 0
                
            if "has_ip_urls" in sample["features"]:
                features[3] = 2 if sample["features"]["has_ip_urls"] else 0
                
            if "body_has_urgency" in sample["features"] or "subject_has_urgency" in sample["features"]:
                features[4] = 1 if sample["features"].get("body_has_urgency", False) or sample["features"].get("subject_has_urgency", False) else 0
                
            if "requests_sensitive_data" in sample["features"]:
                features[5] = 1 if sample["features"]["requests_sensitive_data"] else 0
                
            if "has_suspicious_claims" in sample["features"]:
                features[9] = 2 if sample["features"]["has_suspicious_claims"] else 0
            
            return features
            
        return None
            
    except Exception as e:
        print(f"Error extracting features from feedback sample: {e}")
        traceback.print_exc()
        return None