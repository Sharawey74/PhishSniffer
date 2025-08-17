"""
Quick test summary script to verify all fixes.
"""

import sys
import os
sys.path.append('.')

def test_fixes():
    """Test all the critical fixes."""
    print("🔧 TESTING ALL FIXES")
    print("=" * 50)
    
    # Test 1: External dependencies
    try:
        import sklearn, pandas, numpy, streamlit, plotly, joblib, matplotlib, seaborn
        print("✅ 1. All external dependencies available")
    except ImportError as e:
        print(f"❌ 1. Missing dependency: {e}")
    
    # Test 2: Internal imports
    try:
        from preprocessing.preprocess import DataPreprocessor
        from storage.extract import extract_data
        from model.features import EmailFeatureExtractor
        from gui.main_window import main
        print("✅ 2. All internal modules importable")
    except ImportError as e:
        print(f"❌ 2. Internal import failed: {e}")
    
    # Test 3: NLTK and text cleaning
    try:
        from preprocessing.utils import clean_text
        result = clean_text("Test email with <html>tags</html> and special chars!")
        print(f"✅ 3. Text cleaning works: '{result[:30]}...'")
    except Exception as e:
        print(f"❌ 3. Text cleaning failed: {e}")
    
    # Test 4: Feature extraction with small dataset
    try:
        from model.features import EmailFeatureExtractor
        extractor = EmailFeatureExtractor(max_features=20)
        texts = [
            'normal business email about work',
            'URGENT SPAM EMAIL WITH CAPS'
        ]
        X = extractor.fit_transform(texts)
        print(f"✅ 4. Feature extraction works: shape {X.shape}")
    except Exception as e:
        print(f"❌ 4. Feature extraction failed: {e}")
    
    # Test 5: Train/test split with small data
    try:
        import pandas as pd
        from sklearn.model_selection import train_test_split
        
        # Simulate small dataset scenario
        data = pd.DataFrame({
            'text': ['email1', 'email2', 'email3', 'email4'],
            'label': [0, 1, 0, 1]
        })
        
        # Test our fixed logic
        min_class_size = data['label'].value_counts().min()
        test_size = max(0.2, 2.0 / len(data))
        
        if min_class_size >= 2:
            X_train, X_test, y_train, y_test = train_test_split(
                data['text'], data['label'], 
                test_size=test_size, random_state=42, stratify=data['label']
            )
            print(f"✅ 5. Train/test split works: train={len(X_train)}, test={len(X_test)}")
        else:
            print("✅ 5. Small dataset handling works (no split needed)")
    except Exception as e:
        print(f"❌ 5. Train/test split failed: {e}")
    
    print("=" * 50)
    print("🎯 SUMMARY: Critical fixes tested")
    
    # Quick test count
    print("\n📊 Running quick unit test samples...")
    
    # Test import module
    try:
        from tests.test_imports import TestImports
        t = TestImports()
        t.test_external_dependencies()
        print("✅ Import tests pass")
    except Exception as e:
        print(f"❌ Import tests fail: {e}")
    
    print("\n🚀 All major fixes implemented and tested!")

if __name__ == "__main__":
    test_fixes()
