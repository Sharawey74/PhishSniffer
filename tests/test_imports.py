"""
Test imports for all modules in PhishSniffer.
Ensures all components can be imported correctly.
"""

import unittest
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

class TestImports(unittest.TestCase):
    """Test all module imports."""
    
    def test_preprocessing_imports(self):
        """Test preprocessing module imports."""
        try:
            from preprocessing.preprocess import DataPreprocessor
            from preprocessing.email_processor import EmailProcessor
            from preprocessing.utils import TextCleaner
            from preprocessing.parser import extract_email_content
            self.assertTrue(True, "Preprocessing imports successful")
        except ImportError as e:
            self.fail(f"Preprocessing import failed: {e}")
    
    def test_model_imports(self):
        """Test model module imports."""
        try:
            from model.training import PhishingModelTrainer
            from model.features import EmailFeatureExtractor
            from model.predict import PhishingPredictor
            from model.evaluation import evaluate_model
            self.assertTrue(True, "Model imports successful")
        except ImportError as e:
            self.fail(f"Model import failed: {e}")
    
    def test_gui_imports(self):
        """Test GUI module imports."""
        try:
            from gui.main_window import PhishingDetectorApp
            from gui.analyze_tab import show_analyze_tab
            from gui.report_tab import show_report_tab
            from gui.urls_tab import show_urls_tab
            from gui.settings_tab import show_settings_tab
            self.assertTrue(True, "GUI imports successful")
        except ImportError as e:
            self.fail(f"GUI import failed: {e}")
    
    def test_storage_imports(self):
        """Test storage module imports."""
        try:
            from storage.history import load_analysis_history
            from storage.urls import load_suspicious_urls
            from storage.extract import extract_data
            self.assertTrue(True, "Storage imports successful")
        except ImportError as e:
            self.fail(f"Storage import failed: {e}")
    
    def test_external_dependencies(self):
        """Test external package imports."""
        required_packages = [
            'streamlit', 'pandas', 'numpy', 'sklearn',
            'plotly', 'joblib', 'matplotlib', 'seaborn'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                self.fail(f"Required package {package} not available")

def test_all_imports():
    """Run all import tests programmatically."""
    print("🧪 Testing all module imports...")
    
    def test_preprocessing_imports():
        from preprocessing.preprocess import DataPreprocessor
        from preprocessing.email_processor import EmailProcessor
        from preprocessing.utils import TextCleaner
        from preprocessing.parser import extract_email_content
    
    def test_model_imports():
        from model.training import PhishingModelTrainer
        from model.features import EmailFeatureExtractor
        from model.predict import PhishingPredictor
        from model.evaluation import evaluate_model
    
    def test_gui_imports():
        from gui.main_window import PhishingDetectorApp
        from gui.analyze_tab import show_analyze_tab
        from gui.report_tab import show_report_tab
        from gui.urls_tab import show_urls_tab
        from gui.settings_tab import show_settings_tab
    
    def test_storage_imports():
        from storage.history import load_analysis_history
        from storage.urls import load_suspicious_urls
        from storage.extract import extract_data
    
    def test_external_dependencies():
        required_packages = [
            'streamlit', 'pandas', 'numpy', 'scikit-learn',
            'plotly', 'joblib', 'matplotlib', 'seaborn'
        ]
        for package in required_packages:
            __import__(package)
    
    test_cases = [
        ("Preprocessing", test_preprocessing_imports),
        ("Model", test_model_imports), 
        ("GUI", test_gui_imports),
        ("Storage", test_storage_imports),
        ("Dependencies", test_external_dependencies)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in test_cases:
        try:
            test_func()
            print(f"✅ {name} imports: PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {name} imports: FAILED - {e}")
            failed += 1
    
    print(f"\n📊 Import Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    unittest.main()
