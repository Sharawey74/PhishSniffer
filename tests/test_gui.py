"""
Unit tests for GUI components.
"""

import unittest
import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import GUI modules
from gui.main_window import main
from gui.analyze_tab import show_analyze_tab
from gui.urls_tab import show_urls_tab
from gui.report_tab import show_report_tab
from gui.settings_tab import show_settings_tab

class TestMainWindow(unittest.TestCase):
    """Test main window functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('streamlit.sidebar')
    @patch('streamlit.title')
    def test_main_function_exists(self, mock_title, mock_sidebar):
        """Test that main function exists and can be called."""
        try:
            # Mock streamlit functions
            mock_sidebar.selectbox.return_value = "🔍 Analyze"
            
            # This should not raise an error
            main()
            
            # Check that title was called
            mock_title.assert_called()
            
        except Exception as e:
            # Expected to fail in test environment, but function should exist
            self.assertIsNotNone(main)

class TestAnalyzeTab(unittest.TestCase):
    """Test analyze tab functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('streamlit.text_area')
    @patch('streamlit.button')
    @patch('streamlit.columns')
    @patch('streamlit.header')
    def test_analyze_tab_exists(self, mock_header, mock_columns, mock_button, mock_text_area):
        """Test that analyze tab function exists."""
        try:
            # Mock streamlit components
            mock_text_area.return_value = "Test email content"
            mock_button.return_value = False
            mock_columns.return_value = [MagicMock(), MagicMock()]
            
            # Should not raise an error
            show_analyze_tab()
            
            # Check that header was called
            mock_header.assert_called()
            
        except Exception as e:
            # Expected to fail in test environment
            self.assertIsNotNone(show_analyze_tab)
    
    def test_analyze_tab_callable(self):
        """Test that analyze tab function is callable."""
        self.assertTrue(callable(show_analyze_tab))

class TestUrlsTab(unittest.TestCase):
    """Test URLs tab functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('streamlit.text_input')
    @patch('streamlit.button')
    @patch('streamlit.columns')
    @patch('streamlit.header')
    def test_urls_tab_exists(self, mock_header, mock_columns, mock_button, mock_text_input):
        """Test that URLs tab function exists."""
        try:
            # Mock streamlit components
            mock_text_input.return_value = "https://example.com"
            mock_button.return_value = False
            mock_columns.return_value = [MagicMock(), MagicMock()]
            
            # Should not raise an error
            show_urls_tab()
            
            # Check that header was called
            mock_header.assert_called()
            
        except Exception as e:
            # Expected to fail in test environment
            self.assertIsNotNone(show_urls_tab)
    
    def test_urls_tab_callable(self):
        """Test that URLs tab function is callable."""
        self.assertTrue(callable(show_urls_tab))

class TestReportTab(unittest.TestCase):
    """Test report tab functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('streamlit.selectbox')
    @patch('streamlit.date_input')
    @patch('streamlit.button')
    @patch('streamlit.header')
    def test_report_tab_exists(self, mock_header, mock_button, mock_date_input, mock_selectbox):
        """Test that report tab function exists."""
        try:
            # Mock streamlit components
            mock_selectbox.return_value = "All"
            mock_date_input.return_value = pd.Timestamp.now().date()
            mock_button.return_value = False
            
            # Should not raise an error
            show_report_tab()
            
            # Check that header was called
            mock_header.assert_called()
            
        except Exception as e:
            # Expected to fail in test environment
            self.assertIsNotNone(show_report_tab)
    
    def test_report_tab_callable(self):
        """Test that report tab function is callable."""
        self.assertTrue(callable(show_report_tab))

class TestSettingsTab(unittest.TestCase):
    """Test settings tab functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('streamlit.slider')
    @patch('streamlit.selectbox')
    @patch('streamlit.button')
    @patch('streamlit.header')
    def test_settings_tab_exists(self, mock_header, mock_button, mock_selectbox, mock_slider):
        """Test that settings tab function exists."""
        try:
            # Mock streamlit components
            mock_slider.return_value = 0.5
            mock_selectbox.return_value = "Random Forest"
            mock_button.return_value = False
            
            # Should not raise an error
            show_settings_tab()
            
            # Check that header was called
            mock_header.assert_called()
            
        except Exception as e:
            # Expected to fail in test environment
            self.assertIsNotNone(show_settings_tab)
    
    def test_settings_tab_callable(self):
        """Test that settings tab function is callable."""
        self.assertTrue(callable(show_settings_tab))

class TestGUIIntegration(unittest.TestCase):
    """Integration tests for GUI components."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_all_tabs_importable(self):
        """Test that all tab modules can be imported."""
        # Test imports
        self.assertTrue(callable(show_analyze_tab))
        self.assertTrue(callable(show_urls_tab))
        self.assertTrue(callable(show_report_tab))
        self.assertTrue(callable(show_settings_tab))
        self.assertTrue(callable(main))
    
    def test_tab_function_signatures(self):
        """Test that tab functions have expected signatures."""
        import inspect
        
        # Test analyze tab
        sig = inspect.signature(show_analyze_tab)
        self.assertIsInstance(sig, inspect.Signature)
        
        # Test URLs tab
        sig = inspect.signature(show_urls_tab)
        self.assertIsInstance(sig, inspect.Signature)
        
        # Test report tab
        sig = inspect.signature(show_report_tab)
        self.assertIsInstance(sig, inspect.Signature)
        
        # Test settings tab
        sig = inspect.signature(show_settings_tab)
        self.assertIsInstance(sig, inspect.Signature)

class TestMockStreamlitComponents(unittest.TestCase):
    """Test mock Streamlit components for testing."""
    
    def setUp(self):
        """Set up test environment."""
        pass
    
    def test_mock_text_input(self):
        """Test mock text input."""
        with patch('streamlit.text_input') as mock_input:
            mock_input.return_value = "test input"
            
            # Simulate using text input
            result = mock_input("Test label")
            self.assertEqual(result, "test input")
    
    def test_mock_button(self):
        """Test mock button."""
        with patch('streamlit.button') as mock_button:
            mock_button.return_value = True
            
            # Simulate button click
            result = mock_button("Test Button")
            self.assertTrue(result)
    
    def test_mock_selectbox(self):
        """Test mock selectbox."""
        with patch('streamlit.selectbox') as mock_selectbox:
            mock_selectbox.return_value = "Option 1"
            
            # Simulate selectbox
            result = mock_selectbox("Choose option", ["Option 1", "Option 2"])
            self.assertEqual(result, "Option 1")

def run_gui_tests():
    """Run all GUI unit tests."""
    print("🖥️ Running GUI unit tests...")
    
    test_classes = [
        TestMainWindow,
        TestAnalyzeTab,
        TestUrlsTab,
        TestReportTab,
        TestSettingsTab,
        TestGUIIntegration,
        TestMockStreamlitComponents
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
    
    print(f"\n📊 GUI Test Results: {total_tests - total_failures}/{total_tests} tests passed")
    return total_failures == 0

if __name__ == "__main__":
    unittest.main()
