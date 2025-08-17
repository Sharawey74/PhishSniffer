"""
Unit tests for preprocessing pipeline components.
"""

import unittest
import pandas as pd
import numpy as np
import os
import sys
import tempfile
import shutil

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from preprocessing.preprocess import DataPreprocessor
from preprocessing.email_processor import EmailProcessor
from preprocessing.utils import TextCleaner, calculate_text_features, clean_text
from preprocessing.parser import extract_email_features

class TestDataPreprocessor(unittest.TestCase):
    """Test DataPreprocessor class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.preprocessor = DataPreprocessor(
            data_dir=self.temp_dir,
            output_dir=os.path.join(self.temp_dir, 'output')
        )
        
        # Create sample test data
        self.sample_data = pd.DataFrame({
            'text': [
                'This is a legitimate email about business.',
                'Click here now! Urgent! Free money!',
                'Meeting scheduled for tomorrow at 3pm.',
                'CONGRATULATIONS! You have won $1000000!'
            ],
            'label': [0, 1, 0, 1],
            'source': ['test.csv'] * 4
        })
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test preprocessor initialization."""
        self.assertIsNotNone(self.preprocessor)
        self.assertEqual(self.preprocessor.data_dir, self.temp_dir)
        self.assertTrue(os.path.exists(self.preprocessor.output_dir))
    
    def test_save_processed_data(self):
        """Test saving processed data."""
        self.preprocessor.raw_data = self.sample_data
        self.preprocessor.raw_data['cleaned_text'] = self.sample_data['text'].str.lower()
        
        result = self.preprocessor.save_processed_data()
        self.assertTrue(result)
        
        # Check if files were created
        train_path = os.path.join(self.preprocessor.output_dir, 'train_data.csv')
        test_path = os.path.join(self.preprocessor.output_dir, 'test_data.csv')
        
        self.assertTrue(os.path.exists(train_path))
        self.assertTrue(os.path.exists(test_path))

class TestEmailProcessor(unittest.TestCase):
    """Test EmailProcessor class."""
    
    def setUp(self):
        """Set up test environment."""
        self.processor = EmailProcessor()
    
    def test_initialization(self):
        """Test processor initialization."""
        self.assertIsNotNone(self.processor)
        self.assertIsNotNone(self.processor.preprocessor)
    
    def test_process_email(self):
        """Test email processing."""
        email_data = {'msg': 'This is a test email with some text.'}
        
        result = self.processor.process_email(email_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('body', result)

class TestTextCleaner(unittest.TestCase):
    """Test TextCleaner class."""
    
    def setUp(self):
        """Set up test environment."""
        self.cleaner = TextCleaner()
    
    def test_clean_text_basic(self):
        """Test basic text cleaning."""
        dirty_text = "Hello <b>World</b>! Visit http://example.com NOW!!!"
        cleaned = self.cleaner.clean_text(dirty_text)
        
        self.assertIsInstance(cleaned, str)
        self.assertNotIn('<b>', cleaned)
        self.assertNotIn('http://', cleaned)
    
    def test_clean_text_empty(self):
        """Test cleaning empty text."""
        result = self.cleaner.clean_text("")
        self.assertEqual(result, "")
    
    def test_clean_text_none(self):
        """Test cleaning None input."""
        result = self.cleaner.clean_text(None)
        self.assertEqual(result, "")

class TestTextFeatures(unittest.TestCase):
    """Test text feature extraction functions."""
    
    def test_calculate_text_features(self):
        """Test text feature calculation."""
        text = "This is a test email with multiple sentences. It has various features!"
        
        features = calculate_text_features(text)
        
        self.assertIsInstance(features, dict)
        self.assertIn('length', features)
        self.assertIn('word_count', features)
        self.assertIn('sentence_count', features)
        self.assertIn('avg_word_length', features)
        self.assertIn('char_count', features)
        
        self.assertGreater(features['length'], 0)
        self.assertGreater(features['word_count'], 0)
    
    def test_calculate_text_features_empty(self):
        """Test feature calculation with empty text."""
        features = calculate_text_features("")
        
        self.assertEqual(features['length'], 0)
        self.assertEqual(features['word_count'], 0)
    
    def test_clean_text_function(self):
        """Test standalone clean_text function."""
        dirty_text = "URGENT!!! <script>alert('xss')</script> Free money!"
        cleaned = clean_text(dirty_text)
        
        self.assertIsInstance(cleaned, str)
        self.assertNotIn('<script>', cleaned)
        self.assertNotIn('URGENT!!!', cleaned)  # Should be lowercased

class TestEmailFeatures(unittest.TestCase):
    """Test email feature extraction."""
    
    def test_extract_email_features_text(self):
        """Test extracting features from text email."""
        email_data = {
            'msg': 'From: sender@example.com\nTo: recipient@example.com\nSubject: Test\n\nThis is a test email.'
        }
        
        features = extract_email_features(email_data)
        
        self.assertIsInstance(features, dict)
        self.assertIn('from', features)
        self.assertIn('to', features)
        self.assertIn('subject', features)
        self.assertIn('body', features)
        self.assertIn('has_html', features)
        self.assertIn('has_attachments', features)
    
    def test_extract_email_features_empty(self):
        """Test extracting features from empty email."""
        email_data = {'msg': ''}
        
        features = extract_email_features(email_data)
        
        self.assertIsInstance(features, dict)
        self.assertEqual(features['from'], "")
        self.assertEqual(features['has_attachments'], False)

class TestIntegration(unittest.TestCase):
    """Integration tests for preprocessing pipeline."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test dataset
        test_data = pd.DataFrame({
            'body': [
                'This is a normal business email about meetings.',
                'Click here to claim your FREE prize NOW!!!',
                'Thank you for your purchase. Your order will ship soon.',
                'URGENT: Your account will be suspended unless you click here!'
            ],
            'label': [0, 1, 0, 1]
        })
        
        # Save test dataset
        test_file = os.path.join(self.temp_dir, 'test_dataset.csv')
        test_data.to_csv(test_file, index=False)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_preprocessing_pipeline(self):
        """Test complete preprocessing pipeline with sample data."""
        # This is a simplified test that checks the pipeline can run
        # without errors on sample data
        
        processor = EmailProcessor()
        
        sample_emails = [
            {'msg': 'This is a normal email.'},
            {'msg': 'URGENT!!! Free money!!! Click now!!!'}
        ]
        
        for email_data in sample_emails:
            result = processor.process_email(email_data)
            self.assertIsInstance(result, dict)
            self.assertIn('body', result)

def run_all_tests():
    """Run all preprocessing tests."""
    print("🧪 Running preprocessing unit tests...")
    
    test_classes = [
        TestDataPreprocessor,
        TestEmailProcessor,
        TestTextCleaner,
        TestTextFeatures,
        TestEmailFeatures,
        TestIntegration
    ]
    
    total_tests = 0
    total_failures = 0
    
    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}...")
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
        result = runner.run(suite)
        
        tests_run = result.testsRun
        failures = len(result.failures) + len(result.errors)
        
        total_tests += tests_run
        total_failures += failures
        
        if failures == 0:
            print(f"✅ {test_class.__name__}: {tests_run} tests passed")
        else:
            print(f"❌ {test_class.__name__}: {failures}/{tests_run} tests failed")
            for failure in result.failures + result.errors:
                print(f"   - {failure[0]}: {failure[1].splitlines()[-1]}")
    
    print(f"\n📊 Preprocessing Test Results: {total_tests - total_failures}/{total_tests} tests passed")
    return total_failures == 0

if __name__ == "__main__":
    # Run as unittest
    unittest.main()
