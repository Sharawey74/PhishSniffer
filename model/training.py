"""
Model training pipeline for phishing email detection.
Supports multiple algorithms and hyperparameter tuning.
"""

import os
import joblib
import json
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
import warnings
warnings.filterwarnings('ignore')

from model.features import EmailFeatureExtractor
from model.evaluation import evaluate_model

class PhishingModelTrainer:
    """Main training pipeline for phishing detection models."""
    
    def __init__(self, model_save_dir='trained_models', fast_mode=False):
        self.model_save_dir = model_save_dir
        self.feature_extractor = None
        self.model = None
        self.model_type = None
        self.feature_names = None
        self.fast_mode = fast_mode
        
        # Ensure save directory exists
        os.makedirs(model_save_dir, exist_ok=True)
        
        # Available models and their parameters
        if fast_mode:
            # Optimized for 20-40 minute training
            self.models = {
                'random_forest': {
                    'model': RandomForestClassifier(random_state=42, n_jobs=-1),
                    'params': {
                        'n_estimators': [50, 100],  # Reduced options
                        'max_depth': [10, 20],      # Reduced options
                        'min_samples_split': [5, 10], # Faster training
                        'min_samples_leaf': [2, 4]    # Reduced overfitting
                    }
                },
                'logistic_regression': {
                    'model': LogisticRegression(random_state=42, max_iter=500, n_jobs=-1),
                    'params': {
                        'C': [0.1, 1, 10],  # Reduced options
                        'solver': ['liblinear']  # Faster for small datasets
                    }
                }
            }
        else:
            # Full parameter search (slower but more thorough)
            self.models = {
                'random_forest': {
                    'model': RandomForestClassifier(random_state=42, n_jobs=-1),
                    'params': {
                        'n_estimators': [50, 100, 200],
                        'max_depth': [10, 20, None],
                        'min_samples_split': [2, 5, 10],
                        'min_samples_leaf': [1, 2, 4]
                    }
                },
            'gradient_boosting': {
                'model': GradientBoostingClassifier(random_state=42),
                'params': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7],
                    'subsample': [0.8, 0.9, 1.0]
                }
            },
            'logistic_regression': {
                'model': LogisticRegression(random_state=42, max_iter=1000),
                'params': {
                    'C': [0.01, 0.1, 1, 10, 100],
                    'penalty': ['l1', 'l2'],
                    'solver': ['liblinear', 'saga']
                }
            },
            'svm': {
                'model': SVC(random_state=42, probability=True),
                'params': {
                    'C': [0.1, 1, 10, 100],
                    'kernel': ['linear', 'rbf'],
                    'gamma': ['scale', 'auto', 0.001, 0.01]
                }
            },
            'naive_bayes': {
                'model': MultinomialNB(),
                'params': {
                    'alpha': [0.01, 0.1, 0.5, 1.0, 2.0]
                }
            }
        }
    
    def load_data(self, train_path='cleaned_data/train_data.csv', 
                  test_path='cleaned_data/test_data.csv'):
        """Load training and test data."""
        print(f"Loading training data from: {train_path}")
        self.train_data = pd.read_csv(train_path)
        
        print(f"Loading test data from: {test_path}")
        self.test_data = pd.read_csv(test_path)
        
        print(f"✓ Training data: {len(self.train_data)} samples")
        print(f"✓ Test data: {len(self.test_data)} samples")
        print(f"✓ Training class distribution: {self.train_data['label'].value_counts().to_dict()}")
        print(f"✓ Test class distribution: {self.test_data['label'].value_counts().to_dict()}")
        
        return True
    
    def extract_features(self, max_features=5000, ngram_range=(1, 2)):
        """Extract features from text data."""
        print(f"\n{'='*60}")
        print("FEATURE EXTRACTION")
        print(f"{'='*60}")
        
        # Initialize feature extractor
        self.feature_extractor = EmailFeatureExtractor(
            max_features=max_features,
            ngram_range=ngram_range
        )
        
        # Extract features
        print("Extracting features from training data...")
        X_train = self.feature_extractor.fit_transform(self.train_data['text'])
        
        print("Extracting features from test data...")
        X_test = self.feature_extractor.transform(self.test_data['text'])
        
        # Get labels
        y_train = self.train_data['label'].values
        y_test = self.test_data['label'].values
        
        # Store feature names
        self.feature_names = self.feature_extractor.get_feature_names()
        
        print(f"✓ Training features shape: {X_train.shape}")
        print(f"✓ Test features shape: {X_test.shape}")
        print(f"✓ Number of features: {len(self.feature_names) if self.feature_names else 'Unknown'}")
        
        return X_train, X_test, y_train, y_test
    
    def train_model(self, model_type='random_forest', use_grid_search=True, cv=3):
        """Train a specific model with optional hyperparameter tuning."""
        if model_type not in self.models:
            raise ValueError(f"Model type {model_type} not supported. Available: {list(self.models.keys())}")
        
        print(f"\n{'='*60}")
        print(f"TRAINING {model_type.upper()} MODEL")
        print(f"{'='*60}")
        
        # Get model and parameters
        model_config = self.models[model_type]
        base_model = model_config['model']
        param_grid = model_config['params']
        
        if use_grid_search and len(param_grid) > 0:
            print(f"Performing Grid Search with {cv}-fold cross-validation...")
            print(f"Parameter grid: {param_grid}")
            
            # Use a subset of data for grid search if dataset is large
            if hasattr(self, 'X_train') and len(self.X_train) > 10000:
                print("Using subset of data for faster grid search...")
                subset_size = min(5000, len(self.X_train))
                indices = np.random.choice(len(self.X_train), subset_size, replace=False)
                X_subset = self.X_train[indices]
                y_subset = self.y_train[indices]
            else:
                X_subset = self.X_train
                y_subset = self.y_train
            
            # Perform grid search
            grid_search = GridSearchCV(
                base_model, param_grid, cv=cv, 
                scoring='f1', n_jobs=-1, verbose=1
            )
            grid_search.fit(X_subset, y_subset)
            
            # Get best model
            self.model = grid_search.best_estimator_
            print(f"✓ Best parameters: {grid_search.best_params_}")
            print(f"✓ Best cross-validation score: {grid_search.best_score_:.4f}")
            
        else:
            print("Training with default parameters...")
            self.model = base_model
            self.model.fit(self.X_train, self.y_train)
        
        # Train final model on full training data
        if use_grid_search:
            print("Training final model on full training data...")
            self.model.fit(self.X_train, self.y_train)
        
        self.model_type = model_type
        
        # Evaluate on training data
        train_pred = self.model.predict(self.X_train)
        train_accuracy = accuracy_score(self.y_train, train_pred)
        print(f"✓ Training accuracy: {train_accuracy:.4f}")
        
        # Evaluate on test data
        test_pred = self.model.predict(self.X_test)
        test_accuracy = accuracy_score(self.y_test, test_pred)
        print(f"✓ Test accuracy: {test_accuracy:.4f}")
        
        return self.model
    
    def train_all_models(self, use_grid_search=False):
        """Train and compare all available models."""
        print(f"\n{'='*80}")
        print("TRAINING AND COMPARING ALL MODELS")
        print(f"{'='*80}")
        
        results = {}
        
        for model_name in self.models.keys():
            try:
                print(f"\n{'='*40}")
                print(f"Training {model_name}...")
                print(f"{'='*40}")
                
                # Train model
                model = self.train_model(model_name, use_grid_search=use_grid_search, cv=2)
                
                # Quick evaluation
                test_pred = model.predict(self.X_test)
                accuracy = accuracy_score(self.y_test, test_pred)
                
                results[model_name] = {
                    'model': model,
                    'accuracy': accuracy
                }
                
                print(f"✓ {model_name} accuracy: {accuracy:.4f}")
                
            except Exception as e:
                print(f"✗ Error training {model_name}: {e}")
                continue
        
        # Find best model
        if results:
            best_model_name = max(results.keys(), key=lambda x: results[x]['accuracy'])
            best_model = results[best_model_name]['model']
            best_accuracy = results[best_model_name]['accuracy']
            
            print(f"\n{'='*60}")
            print("MODEL COMPARISON RESULTS")
            print(f"{'='*60}")
            for name, result in sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True):
                print(f"{name:20}: {result['accuracy']:.4f}")
            
            print(f"\n✓ Best model: {best_model_name} (accuracy: {best_accuracy:.4f})")
            
            # Set best model as current model
            self.model = best_model
            self.model_type = best_model_name
            
            return results
        else:
            print("✗ No models trained successfully")
            return None
    
    def save_model(self, model_name=None):
        """Save the trained model and metadata."""
        if self.model is None:
            print("No model to save")
            return False
        
        if model_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name = f"{self.model_type}_{timestamp}"
        
        print(f"\n{'='*60}")
        print("SAVING MODEL")
        print(f"{'='*60}")
        
        # Save model
        model_path = os.path.join(self.model_save_dir, f"{model_name}.joblib")
        joblib.dump(self.model, model_path)
        print(f"✓ Model saved to: {model_path}")
        
        # Save feature extractor
        feature_extractor_path = os.path.join(self.model_save_dir, f"{model_name}_feature_extractor.joblib")
        joblib.dump(self.feature_extractor, feature_extractor_path)
        print(f"✓ Feature extractor saved to: {feature_extractor_path}")
        
        # Save metadata
        metadata = {
            'model_type': self.model_type,
            'model_name': model_name,
            'timestamp': datetime.now().isoformat(),
            'training_samples': len(self.X_train),
            'test_samples': len(self.X_test),
            'feature_count': len(self.feature_names) if self.feature_names else 'Unknown',
            'train_accuracy': accuracy_score(self.y_train, self.model.predict(self.X_train)),
            'test_accuracy': accuracy_score(self.y_test, self.model.predict(self.X_test))
        }
        
        metadata_path = os.path.join(self.model_save_dir, f"{model_name}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Metadata saved to: {metadata_path}")
        
        return model_path
    
    def evaluate_model(self, save_plots=True):
        """Comprehensive model evaluation."""
        if self.model is None:
            print("No model to evaluate")
            return None
        
        print(f"\n{'='*80}")
        print("COMPREHENSIVE MODEL EVALUATION")
        print(f"{'='*80}")
        
        # Create evaluator
        plot_dir = os.path.join(self.model_save_dir, 'evaluation_plots') if save_plots else None
        
        return evaluate_model(
            self.model, self.X_test, self.y_test, 
            self.X_train, self.y_train, save_dir=plot_dir
        )
    
    def run_full_pipeline(self, model_type='random_forest', use_grid_search=True):
        """Run the complete training pipeline."""
        print("="*100)
        print("PHISHING EMAIL DETECTION - MODEL TRAINING PIPELINE")
        print("="*100)
        
        try:
            # Step 1: Load data
            self.load_data()
            
            # Step 2: Extract features
            self.X_train, self.X_test, self.y_train, self.y_test = self.extract_features()
            
            # Step 3: Train model
            if model_type == 'all':
                self.train_all_models(use_grid_search=use_grid_search)
            else:
                self.train_model(model_type, use_grid_search=use_grid_search)
            
            # Step 4: Evaluate model
            evaluation_results = self.evaluate_model()
            
            # Step 5: Save model
            model_path = self.save_model()
            
            print(f"\n{'='*100}")
            print("TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
            print(f"{'='*100}")
            print(f"✓ Model type: {self.model_type}")
            print(f"✓ Model saved to: {model_path}")
            print(f"✓ Test accuracy: {evaluation_results['accuracy']:.4f}")
            print(f"✓ Test F1-score: {evaluation_results['f1_score']:.4f}")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Error in training pipeline: {e}")
            import traceback
            traceback.print_exc()
            return False

def train_custom_model(app=None):
    """Legacy function for backward compatibility."""
    trainer = PhishingModelTrainer()
    return trainer.run_full_pipeline()

def main():
    """Main function to run training pipeline."""
    trainer = PhishingModelTrainer()
    success = trainer.run_full_pipeline(model_type='random_forest', use_grid_search=True)
    return success

if __name__ == "__main__":
    main()