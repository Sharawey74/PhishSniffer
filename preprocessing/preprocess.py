"""
Data preprocessing pipeline for phishing email detection                    if text_col and label_col:
                        # Create standardized dataset
                        standardized_df = pd.DataFrame({
                            'text': df[text_col],
                            'label': df[label_col],
                            'source': filename
                        })
                        
                        # Clean and validate label column
                        standardized_df['label'] = pd.to_numeric(standardized_df['label'], errors='coerce')
                        
                        # Remove rows with invalid labels
                        before_clean = len(standardized_df)
                        standardized_df = standardized_df.dropna(subset=['label'])
                        after_clean = len(standardized_df)
                        
                        if before_clean != after_clean:
                            print(f"  ⚠️ Removed {before_clean - after_clean} rows with invalid labels")
                        
                        # Ensure labels are binary (0 or 1)
                        unique_labels = set(standardized_df['label'].unique())
                        if not unique_labels.issubset({0, 1, 0.0, 1.0}):
                            print(f"  ⚠️ Non-binary labels found: {unique_labels}")
                            # Convert to binary if possible
                            standardized_df['label'] = (standardized_df['label'] > 0).astype(int)
                        
                        # Handle special cases for datasets without explicit labels
                        if filename in ['Nigerian_Fraud.csv', 'Nazario.csv']:
                            standardized_df['label'] = 1  # All phishingcleaning, normalization, EDA, and outlier detection.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

from preprocessing.utils import (
    TextCleaner, 
    detect_outliers_iqr, 
    detect_outliers_zscore,
    calculate_text_features,
    load_dataset,
    standardize_dataset,
    print_dataset_info
)

class DataPreprocessor:
    """Main preprocessing pipeline for email datasets."""
    
    def __init__(self, data_dir='data', output_dir='cleaned_data'):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.text_cleaner = TextCleaner()
        self.processed_data = None
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def load_datasets(self):
        """Load all available datasets."""
        dataset_files = {
            'CEAS_08.csv': {'text_cols': ['body', 'content', 'text'], 'label_cols': ['label', 'is_spam']},
            'Nigerian_Fraud.csv': {'text_cols': ['body', 'content', 'text', 'email'], 'label_cols': ['label']},
            'Nazario.csv': {'text_cols': ['body', 'content', 'text', 'email'], 'label_cols': ['label']},
            'Enron.csv': {'text_cols': ['body', 'content', 'text'], 'label_cols': ['label']},
            'Ling.csv': {'text_cols': ['body', 'content', 'text'], 'label_cols': ['label']},
            'SpamAssasin.csv': {'text_cols': ['body', 'content', 'text'], 'label_cols': ['label', 'is_spam']}
        }
        
        all_data = []
        
        for filename, config in dataset_files.items():
            file_path = os.path.join(self.data_dir, filename)
            
            if os.path.exists(file_path):
                print(f"\nLoading {filename}...")
                try:
                    df = load_dataset(file_path)
                    print_dataset_info(df, filename)
                    
                    # Standardize columns
                    text_col, label_col = standardize_dataset(df, config['text_cols'], config['label_cols'])
                    
                    if text_col and label_col:
                        # Create standardized dataframe
                        standardized_df = pd.DataFrame({
                            'text': df[text_col],
                            'label': df[label_col],
                            'source': filename
                        })
                        
                        # Handle special cases for datasets without explicit labels
                        if filename in ['Nigerian_Fraud.csv', 'Nazario.csv']:
                            standardized_df['label'] = 1  # All phishing
                        
                        all_data.append(standardized_df)
                        print(f"✓ Successfully processed {filename}")
                        print(f"  Text column: {text_col}")
                        print(f"  Label column: {label_col}")
                        print(f"  Samples: {len(standardized_df)}")
                    else:
                        print(f"✗ Could not find suitable text/label columns in {filename}")
                        
                except Exception as e:
                    print(f"✗ Error processing {filename}: {e}")
            else:
                print(f"✗ File not found: {filename}")
        
        if all_data:
            self.raw_data = pd.concat(all_data, ignore_index=True)
            print(f"\n{'='*60}")
            print(f"COMBINED DATASET SUMMARY")
            print(f"{'='*60}")
            print(f"Total samples: {len(self.raw_data)}")
            print(f"Sources: {self.raw_data['source'].value_counts().to_dict()}")
            print(f"Class distribution: {self.raw_data['label'].value_counts().to_dict()}")
            return True
        else:
            print("✗ No datasets could be loaded successfully")
            return False
    
    def perform_eda(self):
        """Perform Exploratory Data Analysis."""
        if self.raw_data is None:
            print("No data loaded for EDA")
            return
        
        print(f"\n{'='*60}")
        print(f"EXPLORATORY DATA ANALYSIS")
        print(f"{'='*60}")
        
        # Basic statistics
        print("\n1. BASIC STATISTICS")
        print(f"Dataset shape: {self.raw_data.shape}")
        print(f"Missing values in text: {self.raw_data['text'].isnull().sum()}")
        print(f"Missing values in label: {self.raw_data['label'].isnull().sum()}")
        
        # Class distribution
        print("\n2. CLASS DISTRIBUTION")
        label_counts = self.raw_data['label'].value_counts()
        print(label_counts)
        print(f"Class balance ratio: {label_counts[1]/label_counts[0]:.3f}")
        
        # Source distribution
        print("\n3. SOURCE DISTRIBUTION")
        source_counts = self.raw_data['source'].value_counts()
        print(source_counts)
        
        # Calculate text features for analysis
        print("\n4. TEXT FEATURE ANALYSIS")
        print("Calculating text features...")
        
        text_features = []
        failed_features = 0
        
        for idx, text in enumerate(self.raw_data['text']):
            if idx % 10000 == 0:
                print(f"  Processing sample {idx}/{len(self.raw_data)}")
            
            try:
                features = calculate_text_features(text)
                text_features.append(features)
            except Exception as e:
                # Handle corrupted text data
                failed_features += 1
                default_features = {
                    'length': 0,
                    'word_count': 0,
                    'sentence_count': 0,
                    'avg_word_length': 0,
                    'char_count': 0
                }
                text_features.append(default_features)
        
        if failed_features > 0:
            print(f"  ⚠️ {failed_features} samples had corrupted text features (set to default)")
        
        feature_df = pd.DataFrame(text_features)
        self.raw_data = pd.concat([self.raw_data, feature_df], axis=1)
        
        # Text statistics
        print(f"\nText length statistics:")
        print(f"  Mean: {feature_df['length'].mean():.2f}")
        print(f"  Median: {feature_df['length'].median():.2f}")
        print(f"  Std: {feature_df['length'].std():.2f}")
        print(f"  Min: {feature_df['length'].min()}")
        print(f"  Max: {feature_df['length'].max()}")
        
        print(f"\nWord count statistics:")
        print(f"  Mean: {feature_df['word_count'].mean():.2f}")
        print(f"  Median: {feature_df['word_count'].median():.2f}")
        print(f"  Std: {feature_df['word_count'].std():.2f}")
        print(f"  Min: {feature_df['word_count'].min()}")
        print(f"  Max: {feature_df['word_count'].max()}")
        
        # Correlation analysis
        print("\n5. CORRELATION ANALYSIS")
        numeric_cols = ['length', 'word_count', 'sentence_count', 'avg_word_length', 'char_count', 'label']
        
        # Clean numeric columns - convert non-numeric values to NaN
        cleaned_data = self.raw_data.copy()
        corrupted_counts = {}
        
        for col in numeric_cols:
            if col in cleaned_data.columns:
                original_count = len(cleaned_data[col])
                cleaned_data[col] = pd.to_numeric(cleaned_data[col], errors='coerce')
                valid_count = cleaned_data[col].notna().sum()
                corrupted_count = original_count - valid_count
                
                if corrupted_count > 0:
                    corrupted_counts[col] = corrupted_count
                    print(f"  ⚠️ Column '{col}': {corrupted_count} corrupted values converted to NaN")
        
        # Remove rows where any numeric column is NaN
        valid_numeric_data = cleaned_data[numeric_cols].dropna()
        
        if len(valid_numeric_data) == 0:
            print("⚠️ No valid numeric data found for correlation analysis")
            return
        
        print(f"Using {len(valid_numeric_data)}/{len(self.raw_data)} samples for correlation analysis")
        
        correlation_matrix = valid_numeric_data.corr()
        print("Correlation with label:")
        print(correlation_matrix['label'].sort_values(ascending=False))
        
        # Update the main dataset to remove corrupted rows
        invalid_rows = len(self.raw_data) - len(valid_numeric_data)
        if invalid_rows > 0:
            print(f"⚠️ Removed {invalid_rows} rows with corrupted numeric data")
            self.raw_data = self.raw_data.loc[valid_numeric_data.index]
    
    def detect_outliers(self):
        """Detect and handle outliers in the dataset."""
        if self.raw_data is None:
            print("No data loaded for outlier detection")
            return
        
        print(f"\n{'='*60}")
        print(f"OUTLIER DETECTION")
        print(f"{'='*60}")
        
        numeric_cols = ['length', 'word_count', 'sentence_count', 'avg_word_length', 'char_count']
        all_outliers = set()
        
        for col in numeric_cols:
            if col in self.raw_data.columns:
                print(f"\nAnalyzing outliers in {col}:")
                
                # IQR method
                iqr_outliers = detect_outliers_iqr(self.raw_data, col)
                print(f"  IQR method: {len(iqr_outliers)} outliers")
                
                # Z-score method
                zscore_outliers = detect_outliers_zscore(self.raw_data, col)
                print(f"  Z-score method: {len(zscore_outliers)} outliers")
                
                # Combine outliers
                combined_outliers = set(iqr_outliers) | set(zscore_outliers)
                all_outliers.update(combined_outliers)
                print(f"  Combined: {len(combined_outliers)} outliers")
        
        print(f"\nTotal unique outliers across all features: {len(all_outliers)}")
        print(f"Percentage of data: {len(all_outliers)/len(self.raw_data)*100:.2f}%")
        
        # Remove extreme outliers (top 1% of outliers)
        if len(all_outliers) > 0:
            outlier_threshold = int(0.01 * len(self.raw_data))  # Remove top 1%
            outliers_to_remove = list(all_outliers)[:outlier_threshold]
            
            print(f"Removing {len(outliers_to_remove)} extreme outliers ({len(outliers_to_remove)/len(self.raw_data)*100:.2f}% of data)")
            self.raw_data = self.raw_data.drop(outliers_to_remove).reset_index(drop=True)
            print(f"Dataset size after outlier removal: {len(self.raw_data)}")
        
        return all_outliers
    
    def clean_text_data(self):
        """Clean and preprocess text data."""
        if self.raw_data is None:
            print("No data loaded for cleaning")
            return
        
        print(f"\n{'='*60}")
        print(f"TEXT CLEANING AND PREPROCESSING")
        print(f"{'='*60}")
        
        # Remove rows with missing text or labels
        initial_size = len(self.raw_data)
        self.raw_data = self.raw_data.dropna(subset=['text', 'label']).reset_index(drop=True)
        print(f"Removed {initial_size - len(self.raw_data)} rows with missing text/labels")
        
        # Clean text data
        print("Cleaning text data...")
        cleaned_texts = []
        
        for idx, text in enumerate(self.raw_data['text']):
            if idx % 5000 == 0:
                print(f"  Cleaning sample {idx}/{len(self.raw_data)}")
            
            cleaned_text = self.text_cleaner.clean_text(text)
            cleaned_texts.append(cleaned_text)
        
        self.raw_data['cleaned_text'] = cleaned_texts
        
        # Remove rows with empty cleaned text
        before_empty_removal = len(self.raw_data)
        self.raw_data = self.raw_data[self.raw_data['cleaned_text'].str.len() > 0].reset_index(drop=True)
        print(f"Removed {before_empty_removal - len(self.raw_data)} rows with empty cleaned text")
        
        # Convert labels to integers
        self.raw_data['label'] = self.raw_data['label'].astype(int)
        
        print(f"Final dataset size: {len(self.raw_data)}")
        print(f"Final class distribution: {self.raw_data['label'].value_counts().to_dict()}")
    
    def save_processed_data(self):
        """Save processed data to files."""
        if self.raw_data is None:
            print("No processed data to save")
            return
        
        print(f"\n{'='*60}")
        print(f"SAVING PROCESSED DATA")
        print(f"{'='*60}")
        
        # Save full processed dataset
        full_path = os.path.join(self.output_dir, 'processed_emails.csv')
        self.raw_data.to_csv(full_path, index=False)
        print(f"✓ Saved full processed dataset: {full_path}")
        
        # Create train/test split - ensure we have enough samples
        X = self.raw_data['cleaned_text']
        y = self.raw_data['label']
        
        # Calculate appropriate test size
        min_class_size = y.value_counts().min()
        test_size = max(0.2, 2.0 / len(y))  # At least 2 samples or 20%
        
        if min_class_size < 2:
            print(f"⚠️ Warning: Only {min_class_size} samples in smallest class. Using all data for training.")
            X_train, X_test, y_train, y_test = X, X.iloc[:0], y, y.iloc[:0]
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
        
        # Save training data
        train_data = pd.DataFrame({
            'text': X_train,
            'label': y_train
        })
        train_path = os.path.join(self.output_dir, 'train_data.csv')
        train_data.to_csv(train_path, index=False)
        print(f"✓ Saved training data: {train_path} ({len(train_data)} samples)")
        
        # Save test data
        test_data = pd.DataFrame({
            'text': X_test,
            'label': y_test
        })
        test_path = os.path.join(self.output_dir, 'test_data.csv')
        test_data.to_csv(test_path, index=False)
        print(f"✓ Saved test data: {test_path} ({len(test_data)} samples)")
        
        # Save feature-rich dataset for analysis
        analysis_path = os.path.join(self.output_dir, 'analysis_data.csv')
        self.raw_data.to_csv(analysis_path, index=False)
        print(f"✓ Saved analysis data with features: {analysis_path}")
        
        self.processed_data = self.raw_data
        return True
    
    def run_full_pipeline(self):
        """Run the complete preprocessing pipeline."""
        print("="*80)
        print("PHISHING EMAIL DETECTION - DATA PREPROCESSING PIPELINE")
        print("="*80)
        
        try:
            # Step 1: Load datasets
            if not self.load_datasets():
                return False
            
            # Step 2: Perform EDA
            self.perform_eda()
            
            # Step 3: Detect outliers
            self.detect_outliers()
            
            # Step 4: Clean text data
            self.clean_text_data()
            
            # Step 5: Save processed data
            self.save_processed_data()
            
            print(f"\n{'='*80}")
            print("PREPROCESSING PIPELINE COMPLETED SUCCESSFULLY!")
            print(f"{'='*80}")
            print(f"✓ Processed {len(self.processed_data)} email samples")
            print(f"✓ Class distribution: {self.processed_data['label'].value_counts().to_dict()}")
            print(f"✓ Output saved to: {self.output_dir}/")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Error in preprocessing pipeline: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function to run preprocessing pipeline."""
    preprocessor = DataPreprocessor()
    success = preprocessor.run_full_pipeline()
    return success

if __name__ == "__main__":
    main()
