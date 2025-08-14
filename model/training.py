import os
import re
import joblib
import json
import numpy as np
import pandas as pd
import traceback
from sklearn.ensemble import RandomForestClassifier

def train_custom_model(app):
    """Train a custom phishing detection model using the specified datasets"""
    try:
        app.update_status("Training custom model...", "info")

        # Define dataset paths
        dataset_paths = [
            r"resources\CEAS_08.csv",
            r"resources\Nigerian_Fraud.csv",
            r"resources\Nazario.csv",
        ]

        # Initialize empty datasets
        all_data = []
        all_labels = []

        # Load and process each dataset
        for dataset_path in dataset_paths:
            try:
                print(f"Processing dataset: {os.path.basename(dataset_path)}")

                # Load CSV file with proper settings to handle mixed data types
                df = pd.read_csv(dataset_path, encoding='latin1', on_bad_lines='skip', low_memory=False)

                # Check which columns exist
                headers = df.columns.tolist()

                # Extract email text depending on available columns
                text_column = None
                for possible_column in ['body', 'content', 'text', 'email', 'message']:
                    if possible_column in headers:
                        text_column = possible_column
                        break

                if text_column is None:
                    # Use first string column found
                    text_columns = [col for col in headers if df[col].dtype == 'object']
                    if text_columns:
                        text_column = text_columns[0]
                    else:
                        print(f"No text column found in {dataset_path}")
                        continue

                # Get the text data
                texts = df[text_column].fillna('').astype(str)

                # Extract label depending on available columns
                label_column = None
                for possible_column in ['label', 'is_phishing', 'phishing', 'class', 'spam', 'is_spam']:
                    if possible_column in headers:
                        label_column = possible_column
                        break

                if label_column is None:
                    # Use filename to determine labels (assuming Nigerian_Fraud and Nazario are phishing)
                    if 'Nigerian_Fraud' in dataset_path or 'Nazario' in dataset_path:
                        labels = pd.Series([1] * len(texts))  # All phishing
                    else:
                        # Try to find binary column
                        binary_cols = [col for col in headers if
                                      set(pd.unique(df[col].dropna())) <= {0, 1, 0.0, 1.0}]
                        if binary_cols:
                            label_column = binary_cols[0]
                            labels = df[label_column]
                        else:
                            print(f"No label column found in {dataset_path}")
                            continue
                else:
                    labels = df[label_column]

                # Process each sample
                processed_count = 0
                for i, (text, label) in enumerate(zip(texts, labels)):
                    try:
                        # Skip NaN values
                        if pd.isna(label):
                            continue

                        # Skip empty texts
                        if not text or pd.isna(text) or len(str(text).strip()) == 0:
                            continue

                        # Extract features
                        features = extract_features_from_text(text)

                        # Skip if feature extraction failed (returned None)
                        if features is None:
                            continue

                        all_data.append(features)
                        all_labels.append(
                            int(float(label)))  # Convert to int through float to handle '1.0' type values
                        processed_count += 1

                    except Exception as e:
                        # Print error but continue with next sample
                        print(f"Error processing sample {i} from {os.path.basename(dataset_path)}: {e}")
                        continue

                print(f"Processed {processed_count} valid emails from {os.path.basename(dataset_path)}")

            except Exception as e:
                print(f"Error processing dataset {dataset_path}: {e}")
                traceback.print_exc()

        # Check if we have enough data
        if len(all_data) < 10:
            print("Not enough data to train model")
            create_default_model(os.path.join(app.models_dir, "phishing_detector_model.joblib"), app)
            return

        # Ensure consistent data lengths
        print(f"Raw data: {len(all_data)} samples, {len(all_labels)} labels")

        if len(all_data) != len(all_labels):
            print(f"Warning: Inconsistent data length. Features: {len(all_data)}, Labels: {len(all_labels)}")
            # Take the minimum length to ensure consistency
            min_len = min(len(all_data), len(all_labels))
            all_data = all_data[:min_len]
            all_labels = all_labels[:min_len]

        # Convert to numpy arrays
        X = np.array(all_data)
        y = np.array(all_labels)

        print(f"Final dataset size: {len(X)} samples with {X.shape[1]} features")

        # Train a Random Forest model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)

        # Save the model
        os.makedirs(app.models_dir, exist_ok=True)
        model_path = os.path.join(app.models_dir, "phishing_detector_model.joblib")
        joblib.dump(model, model_path)

        # Save model metadata
        app.model_metadata = {
            "model_type": "Random Forest Classifier",
            "version": "1.0.0",
            "last_updated": app.current_datetime,
            "features_used": X.shape[1],
            "training_data_size": len(X),
            "dataset_files": [os.path.basename(path) for path in dataset_paths],
            "accuracy": "N/A (no validation performed)",
            "created_by": app.current_user
        }

        metadata_path = os.path.join(app.models_dir, "model_metadata.json")
        with open(metadata_path, 'w') as file:
            json.dump(app.model_metadata, file, indent=2)

        # Set the model
        app.loaded_model = model
        app.model_feature_count = X.shape[1]
        app.update_status("Custom model trained successfully", "success")

    except Exception as e:
        print(f"Error training custom model: {e}")
        traceback.print_exc()
        create_default_model(os.path.join(app.models_dir, "phishing_detector_model.joblib"), app)

def extract_features_from_text(text):
    """Extract standardized features from email text for model training"""
    try:
        # Initialize features array
        features = np.zeros(10)  # Using 10 features for comprehensive analysis

        # Convert text to lowercase for case-insensitive matching
        text = str(text).lower()

        # Feature 1: Contains suspicious sender patterns (from, paypal, bank, etc.)
        suspicious_senders = ['paypal', 'bank', 'account', 'security', 'update', 'verify', 'amazon']
        features[0] = int(any(sender in text[:500] for sender in suspicious_senders))

        # Feature 2: Contains URLs
        features[1] = int(bool(re.search(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)))

        # Feature 3: Contains shortened URLs
        short_domains = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'is.gd']
        features[2] = int(any(domain in text for domain in short_domains))

        # Feature 4: Contains IP-based URLs
        features[3] = int(bool(re.search(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text)))

        # Feature 5: Contains urgency words
        urgency_words = ['urgent', 'immediately', 'alert', 'verify', 'suspend', 'restrict',
                        'limited', 'expires', 'validate', 'confirm']
        features[4] = int(any(word in text for word in urgency_words))

        # Feature 6: Contains sensitive data requests
        sensitive_requests = ['password', 'credit card', 'ssn', 'social security', 'credentials',
                             'login', 'username', 'pin', 'bank account', 'billing']
        features[5] = int(any(req in text for req in sensitive_requests))

        # Feature 7: Contains suspicious attachment mentions
        attachment_words = ['attach', 'document', 'file', 'pdf', 'doc', 'invoice', 'receipt', 'statement']
        features[6] = int(any(word in text for word in attachment_words))

        # Feature 8: Contains financial/money terms
        money_terms = ['$', 'dollar', 'payment', 'transfer', 'transaction', 'wire', 'money',
                      'credit', 'debit', 'cash', 'fund', 'tax', 'refund']
        features[7] = int(any(term in text for term in money_terms))

        # Feature 9: Contains threatening language
        threat_terms = ['suspended', 'terminated', 'unauthorized', 'closed', 'limited',
                       'suspicious activity', 'unusual', 'breach', 'compromised', 'fraud']
        features[8] = int(any(term in text for term in threat_terms))

        # Feature 10: Contains suspicious offers/claims
        offer_terms = ['won', 'winner', 'prize', 'million', 'free', 'discount', 'offer',
                      'reward', 'gift', 'claim', 'congratulations', 'selected']
        features[9] = int(any(term in text for term in offer_terms))

        return features
    except Exception as e:
        print(f"Error extracting features: {e}")
        # Return zeros if extraction fails to maintain consistency
        return np.zeros(10)

def create_default_model(model_path, app):
    """Create a simple default model if none exists"""
    try:
        # Create a simple RandomForest model
        model = RandomForestClassifier(n_estimators=100, random_state=42)

        # Create sample data to fit the model (minimal just to initialize)
        # Use our feature count (10 features)
        X = np.array([[0] * 10, [1] * 10])
        y = np.array([0, 1])

        # Fit and save the model
        model.fit(X, y)
        joblib.dump(model, model_path)

        app.loaded_model = model
        app.model_feature_count = 10  # Default model uses 10 features
        print(f"Created default model at: {model_path}")
    except Exception as e:
        print(f"Error creating default model: {e}")
        traceback.print_exc()