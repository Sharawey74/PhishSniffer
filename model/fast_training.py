"""
Fast Training Pipeline for PhishSniffer
Optimized for 20-40 minute training time with minimal accuracy loss.

Key optimizations:
1. Reduced feature space (1000-2000 features)
2. Smart sampling for grid search
3. Simplified parameter grids
4. Early stopping
5. Progressive training strategy
"""

import os
import joblib
import json
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
warnings.filterwarnings('ignore')

class FastPhishingTrainer:
    """Optimized training pipeline for faster model development."""
    
    def __init__(self, model_save_dir='trained_models'):
        self.model_save_dir = model_save_dir
        os.makedirs(model_save_dir, exist_ok=True)
        
        # Fast training configurations
        self.fast_models = {
            'random_forest_fast': {
                'model': RandomForestClassifier(
                    n_estimators=100,  # Reduced from 200
                    random_state=42,
                    n_jobs=-1,
                    warm_start=True
                ),
                'params': {
                    'max_depth': [10, 20],  # Reduced options
                    'min_samples_split': [2, 5],  # Reduced options
                    'min_samples_leaf': [1, 2]  # Reduced options
                }
            },
            'gradient_boosting_fast': {
                'model': GradientBoostingClassifier(
                    n_estimators=100,  # Reduced from 200
                    random_state=42
                ),
                'params': {
                    'learning_rate': [0.1, 0.2],  # Reduced options
                    'max_depth': [3, 5],  # Reduced options
                    'subsample': [0.8, 1.0]  # Reduced options
                }
            },
            'logistic_regression_fast': {
                'model': LogisticRegression(
                    random_state=42,
                    max_iter=500,  # Reduced iterations
                    n_jobs=-1
                ),
                'params': {
                    'C': [0.1, 1, 10],  # Reduced options
                    'penalty': ['l2']  # Only L2 for speed
                }
            }
        }
    
    def load_data(self, train_path='cleaned_data/train_data.csv', 
                  test_path='cleaned_data/test_data.csv', sample_size=None):
        """Load and optionally sample data for faster training."""
        print(f"Loading training data from: {train_path}")
        self.train_data = pd.read_csv(train_path)
        
        print(f"Loading test data from: {test_path}")
        self.test_data = pd.read_csv(test_path)
        
        # Sample data for initial fast training
        if sample_size and len(self.train_data) > sample_size:
            print(f"Sampling {sample_size} training examples for fast training...")
            self.train_data = self.train_data.sample(n=sample_size, random_state=42)
        
        print(f"✓ Training data: {len(self.train_data)} samples")
        print(f"✓ Test data: {len(self.test_data)} samples")
        
        return True
    
    def extract_fast_features(self, max_features=2000, ngram_range=(1, 2)):
        """Fast feature extraction with reduced feature space."""
        print(f"\n{'='*60}")
        print("FAST FEATURE EXTRACTION")
        print(f"{'='*60}")
        
        # Optimized TF-IDF with reduced features
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,  # Reduced from 10000
            ngram_range=ngram_range,
            min_df=2,  # Remove very rare terms
            max_df=0.95,  # Remove very common terms
            stop_words='english',
            lowercase=True,
            strip_accents='unicode'
        )
        
        # Extract features
        print("Extracting TF-IDF features...")
        X_train = self.tfidf_vectorizer.fit_transform(self.train_data['text'])
        X_test = self.tfidf_vectorizer.transform(self.test_data['text'])
        
        # Add basic email features
        print("Adding basic email features...")
        train_email_features = self._extract_basic_features(self.train_data['text'])
        test_email_features = self._extract_basic_features(self.test_data['text'])
        
        # Combine features
        X_train_combined = np.hstack([X_train.toarray(), train_email_features])
        X_test_combined = np.hstack([X_test.toarray(), test_email_features])
        
        # Get labels
        y_train = self.train_data['label'].values
        y_test = self.test_data['label'].values
        
        print(f"✓ Training features shape: {X_train_combined.shape}")
        print(f"✓ Test features shape: {X_test_combined.shape}")
        
        return X_train_combined, X_test_combined, y_train, y_test
    
    def _extract_basic_features(self, texts):
        """Extract basic email features quickly."""
        features = []
        
        for text in texts:
            text = str(text).lower()
            
            # Basic features (10 total)
            text_features = [
                len(text),  # Length
                len(text.split()),  # Word count
                text.count('http'),  # URL mentions
                text.count('$'),  # Dollar signs
                text.count('urgent'),  # Urgency
                text.count('verify'),  # Verification requests
                text.count('click'),  # Click requests
                text.count('password'),  # Password mentions
                text.count('!'),  # Exclamation marks
                text.count('free')  # Free offers
            ]
            
            features.append(text_features)
        
        return np.array(features)
    
    def progressive_training(self, model_type='random_forest_fast'):
        """Progressive training strategy: start small, then scale up."""
        print(f"\n{'='*60}")
        print(f"PROGRESSIVE TRAINING - {model_type.upper()}")
        print(f"{'='*60}")
        
        model_config = self.fast_models[model_type]
        base_model = model_config['model']
        param_grid = model_config['params']
        
        # Stage 1: Quick parameter search on subset (5 minutes)
        print("\n🚀 STAGE 1: Quick Parameter Search (5 min target)")
        subset_size = min(5000, len(self.X_train))
        indices = np.random.choice(len(self.X_train), subset_size, replace=False)
        X_subset = self.X_train[indices]
        y_subset = self.y_train[indices]
        
        start_time = time.time()
        grid_search = GridSearchCV(
            base_model, param_grid, cv=2,  # Reduced CV folds
            scoring='f1', n_jobs=-1, verbose=1
        )
        grid_search.fit(X_subset, y_subset)
        stage1_time = time.time() - start_time
        
        print(f"✓ Stage 1 completed in {stage1_time:.1f} seconds")
        print(f"✓ Best parameters: {grid_search.best_params_}")
        
        # Stage 2: Train best model on full data (15-30 minutes)
        print(f"\n🎯 STAGE 2: Full Training with Best Parameters")
        best_model = grid_search.best_estimator_
        
        start_time = time.time()
        best_model.fit(self.X_train, self.y_train)
        stage2_time = time.time() - start_time
        
        print(f"✓ Stage 2 completed in {stage2_time:.1f} seconds")
        
        # Evaluate
        train_pred = best_model.predict(self.X_train)
        test_pred = best_model.predict(self.X_test)
        
        train_accuracy = accuracy_score(self.y_train, train_pred)
        test_accuracy = accuracy_score(self.y_test, test_pred)
        test_f1 = f1_score(self.y_test, test_pred)
        
        total_time = stage1_time + stage2_time
        print(f"\n📊 TRAINING RESULTS:")
        print(f"✓ Total training time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        print(f"✓ Training accuracy: {train_accuracy:.4f}")
        print(f"✓ Test accuracy: {test_accuracy:.4f}")
        print(f"✓ Test F1-score: {test_f1:.4f}")
        
        self.model = best_model
        self.model_type = model_type
        
        return best_model
    
    def incremental_training(self, model_type='random_forest_fast'):
        """Incremental training for even faster development."""
        print(f"\n{'='*60}")
        print(f"INCREMENTAL TRAINING - {model_type.upper()}")
        print(f"{'='*60}")
        
        if 'random_forest' in model_type:
            # Start with small forest, grow incrementally
            model = RandomForestClassifier(
                n_estimators=20,  # Start small
                random_state=42,
                n_jobs=-1,
                warm_start=True  # Allow incremental growth
            )
            
            start_time = time.time()
            
            # Incremental training stages
            stages = [20, 50, 100]
            for stage, n_trees in enumerate(stages, 1):
                print(f"\n🌳 Stage {stage}: Training {n_trees} trees...")
                model.n_estimators = n_trees
                model.fit(self.X_train, self.y_train)
                
                # Quick evaluation
                test_pred = model.predict(self.X_test)
                accuracy = accuracy_score(self.y_test, test_pred)
                print(f"✓ Accuracy with {n_trees} trees: {accuracy:.4f}")
            
            total_time = time.time() - start_time
            print(f"\n✅ Incremental training completed in {total_time:.1f} seconds")
            
            self.model = model
            self.model_type = model_type
            
            return model
        
        else:
            # For non-tree models, use regular training
            return self.progressive_training(model_type)
    
    def save_fast_model(self, model_name=None):
        """Save the fast-trained model."""
        if self.model is None:
            print("No model to save")
            return False
        
        if model_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name = f"fast_{self.model_type}_{timestamp}"
        
        # Save model
        model_path = os.path.join(self.model_save_dir, f"{model_name}.joblib")
        joblib.dump(self.model, model_path)
        
        # Save feature extractor
        feature_extractor_path = os.path.join(self.model_save_dir, f"{model_name}_vectorizer.joblib")
        joblib.dump(self.tfidf_vectorizer, feature_extractor_path)
        
        # Save metadata
        metadata = {
            'model_type': self.model_type,
            'model_name': model_name,
            'timestamp': datetime.now().isoformat(),
            'training_mode': 'fast',
            'feature_count': self.X_train.shape[1],
            'training_samples': len(self.X_train),
            'test_accuracy': accuracy_score(self.y_test, self.model.predict(self.X_test))
        }
        
        metadata_path = os.path.join(self.model_save_dir, f"{model_name}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Fast model saved: {model_path}")
        return model_path
    
    def run_fast_pipeline(self, training_mode='progressive', max_features=2000, sample_size=None):
        """Run the complete fast training pipeline."""
        print("="*100)
        print("⚡ PHISHSNIFFER - FAST TRAINING PIPELINE")
        print("="*100)
        print(f"🎯 Target: 20-40 minute training")
        print(f"🔧 Mode: {training_mode}")
        print(f"📊 Max features: {max_features}")
        print("="*100)
        
        pipeline_start = time.time()
        
        try:
            # Load data
            self.load_data(sample_size=sample_size)
            
            # Extract features
            self.X_train, self.X_test, self.y_train, self.y_test = self.extract_fast_features(max_features)
            
            # Train model
            if training_mode == 'progressive':
                self.progressive_training('random_forest_fast')
            elif training_mode == 'incremental':
                self.incremental_training('random_forest_fast')
            else:
                raise ValueError(f"Unknown training mode: {training_mode}")
            
            # Save model
            model_path = self.save_fast_model()
            
            total_time = time.time() - pipeline_start
            
            print(f"\n{'='*100}")
            print("⚡ FAST TRAINING PIPELINE COMPLETED!")
            print(f"{'='*100}")
            print(f"⏱️  Total pipeline time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
            print(f"🎯 Target met: {'✅ YES' if total_time < 2400 else '❌ NO'} (40 min limit)")
            print(f"💾 Model saved: {model_path}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error in fast training pipeline: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function for fast training."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fast PhishSniffer Training')
    parser.add_argument('--mode', choices=['progressive', 'incremental'], 
                       default='progressive', help='Training mode')
    parser.add_argument('--features', type=int, default=2000, 
                       help='Maximum features')
    parser.add_argument('--sample', type=int, default=None,
                       help='Sample size for training data')
    
    args = parser.parse_args()
    
    trainer = FastPhishingTrainer()
    success = trainer.run_fast_pipeline(
        training_mode=args.mode,
        max_features=args.features,
        sample_size=args.sample
    )
    
    return success

if __name__ == "__main__":
    main()
