#!/usr/bin/env python3
"""
Algorithm Comparison Script for PhishSniffer
Test all available algorithms and compare their performance.

This script will:
1. Load your preprocessed data
2. Train ALL 5 algorithms
3. Compare their performance
4. Show you which algorithm works best for your dataset
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import time

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_all_algorithms():
    """Test all available algorithms and compare performance."""
    print("=" * 100)
    print("🔬 PHISHSNIFFER - COMPLETE ALGORITHM COMPARISON")
    print("=" * 100)
    print("Testing ALL 5 algorithms on your dataset:")
    print("1. Random Forest (current champion)")
    print("2. Gradient Boosting") 
    print("3. Logistic Regression")
    print("4. Support Vector Machine (SVM)")
    print("5. Naive Bayes")
    print("=" * 100)
    
    try:
        from model.training import PhishingModelTrainer
        
        # Initialize trainer
        trainer = PhishingModelTrainer()
        
        # Load your data
        print("\n📊 Loading your preprocessed data...")
        if not trainer.load_data():
            print("❌ Failed to load data")
            return False
        
        # Extract features (using your current feature extraction)
        print("\n🔧 Extracting features with TF-IDF...")
        trainer.X_train, trainer.X_test, trainer.y_train, trainer.y_test = trainer.extract_features(
            max_features=5000,  # Reduced for faster comparison
            ngram_range=(1, 2)
        )
        
        # Train and compare ALL models
        print(f"\n{'=' * 80}")
        print("🚀 TRAINING ALL ALGORITHMS...")
        print(f"{'=' * 80}")
        
        results = trainer.train_all_models(use_grid_search=False)  # No grid search for speed
        
        if results:
            print(f"\n{'=' * 100}")
            print("📊 FINAL ALGORITHM COMPARISON RESULTS")
            print(f"{'=' * 100}")
            
            # Sort by accuracy
            sorted_results = sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True)
            
            print(f"{'Rank':<4} {'Algorithm':<20} {'Accuracy':<10} {'Status'}")
            print("-" * 50)
            
            for i, (name, result) in enumerate(sorted_results, 1):
                accuracy = result['accuracy']
                status = "🏆 BEST" if i == 1 else "✅ GOOD" if accuracy > 0.90 else "⚠️ OKAY"
                print(f"{i:<4} {name:<20} {accuracy:.4f}     {status}")
            
            # Detailed analysis
            best_name, best_result = sorted_results[0]
            print(f"\n{'=' * 60}")
            print("🏆 WINNER ANALYSIS")
            print(f"{'=' * 60}")
            print(f"Best Algorithm: {best_name}")
            print(f"Best Accuracy: {best_result['accuracy']:.4f}")
            
            # Compare with current Random Forest
            if 'random_forest' in results:
                rf_accuracy = results['random_forest']['accuracy']
                print(f"Random Forest (current): {rf_accuracy:.4f}")
                
                if best_name != 'random_forest':
                    improvement = best_result['accuracy'] - rf_accuracy
                    print(f"Potential improvement: +{improvement:.4f} ({improvement*100:.2f}%)")
                else:
                    print("Random Forest is still the best choice! ✅")
            
            return results
        else:
            print("❌ No algorithms completed successfully")
            return False
            
    except Exception as e:
        print(f"\n❌ Error in algorithm comparison: {e}")
        import traceback
        traceback.print_exc()
        return False

def explain_algorithms():
    """Explain each algorithm and when to use it."""
    print(f"\n{'=' * 100}")
    print("📚 ALGORITHM EXPLANATIONS")
    print(f"{'=' * 100}")
    
    algorithms = {
        "Random Forest": {
            "description": "Ensemble of decision trees voting together",
            "strengths": ["Robust to overfitting", "Handles mixed data well", "Feature importance"],
            "weaknesses": ["Can be memory intensive", "Less interpretable"],
            "best_for": "General-purpose classification with good balance of speed/accuracy"
        },
        "Gradient Boosting": {
            "description": "Sequential learning - each tree fixes previous mistakes",
            "strengths": ["Often highest accuracy", "Good with complex patterns", "Handles missing data"],
            "weaknesses": ["Can overfit", "Slower training", "Sensitive to noise"],
            "best_for": "When you need maximum accuracy and have clean data"
        },
        "Logistic Regression": {
            "description": "Linear model using logistic function for classification",
            "strengths": ["Very fast", "Interpretable coefficients", "Probabilistic output"],
            "weaknesses": ["Assumes linear relationships", "May underfit complex data"],
            "best_for": "Baseline models, when you need speed and interpretability"
        },
        "Support Vector Machine": {
            "description": "Finds optimal boundary between classes in high-dimensional space",
            "strengths": ["Excellent with high dimensions", "Memory efficient", "Versatile kernels"],
            "weaknesses": ["Slow on large datasets", "Sensitive to feature scaling"],
            "best_for": "High-dimensional data like TF-IDF features, small-medium datasets"
        },
        "Naive Bayes": {
            "description": "Probabilistic classifier assuming feature independence",
            "strengths": ["Very fast training/prediction", "Good with small data", "Handles multiple classes well"],
            "weaknesses": ["Assumes feature independence", "Can be outperformed by complex models"],
            "best_for": "Text classification, real-time predictions, baseline models"
        }
    }
    
    for name, info in algorithms.items():
        print(f"\n🔹 {name.upper()}")
        print(f"   Description: {info['description']}")
        print(f"   Strengths: {', '.join(info['strengths'])}")
        print(f"   Weaknesses: {', '.join(info['weaknesses'])}")
        print(f"   Best for: {info['best_for']}")

def explain_tfidf():
    """Explain TF-IDF in detail with examples."""
    print(f"\n{'=' * 100}")
    print("📖 TF-IDF DETAILED EXPLANATION")
    print(f"{'=' * 100}")
    
    print("""
🔤 TF-IDF converts email text into numbers for machine learning:

Example with 2 emails:
Email 1: "Urgent! Verify your account now!"
Email 2: "Please verify the account information when convenient"

Step 1: TERM FREQUENCY (TF)
- How often each word appears in each email
- Email 1 TF: urgent=1/5, verify=1/5, account=1/5, now=1/5
- Email 2 TF: verify=1/7, account=1/7, information=1/7, convenient=1/7

Step 2: INVERSE DOCUMENT FREQUENCY (IDF)  
- How rare each word is across ALL emails
- If "urgent" appears in 100 out of 10000 emails: IDF = log(10000/100) = 2.0
- If "verify" appears in 5000 out of 10000 emails: IDF = log(10000/5000) = 0.69

Step 3: TF-IDF SCORE = TF × IDF
- Email 1 "urgent": (1/5) × 2.0 = 0.40 (HIGH - rare urgent word)
- Email 1 "verify": (1/5) × 0.69 = 0.14 (LOWER - common verify word)

🎯 RESULT: Rare important words get high scores, common words get low scores

📊 YOUR PHISHSNIFFER TF-IDF SETTINGS:
- max_features=10,000: Keep only top 10K most important words
- ngram_range=(1,2): Use single words AND word pairs ("urgent action")
- min_df=2: Ignore words appearing in <2 emails (typos, noise)
- max_df=0.95: Ignore words appearing in >95% emails (too common)
- stop_words='english': Remove "the", "and", "is", etc.

🔍 EXAMPLE PHISHING WORDS WITH HIGH TF-IDF:
- "urgent action" (word pair)
- "verify immediately" 
- "suspended account"
- "click here"
- "limited time"
""")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='PhishSniffer Algorithm Analysis')
    parser.add_argument('--explain-only', action='store_true', 
                       help='Only show explanations, skip training')
    parser.add_argument('--test-algorithms', action='store_true',
                       help='Test all algorithms and compare performance')
    
    args = parser.parse_args()
    
    # Always show explanations
    explain_tfidf()
    explain_algorithms()
    
    if args.explain_only:
        print("\n📚 Explanation complete! Use --test-algorithms to run performance comparison.")
        return True
    
    if args.test_algorithms or input("\n🚀 Run algorithm comparison? (y/n): ").lower() == 'y':
        print("\n" + "="*50)
        print("⚡ Starting algorithm comparison...")
        print("⏱️  This will take about 10-15 minutes")
        print("="*50)
        
        results = test_all_algorithms()
        
        if results:
            print(f"\n{'=' * 100}")
            print("✅ ANALYSIS COMPLETE!")
            print(f"{'=' * 100}")
            print("📈 You now know which algorithm works best for your data!")
            print("🔧 You can modify app.py to use the best algorithm")
            print("💡 Or use train_all_models() to automatically pick the best one")
            return True
        else:
            print("\n❌ Algorithm comparison failed")
            return False
    
    return True

if __name__ == "__main__":
    main()
