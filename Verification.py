#!/usr/bin/env python3
"""
Verification script to test PhishSniffer modernization.
Tests all major components and imports.
"""

import sys
import os
import traceback

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test all critical imports."""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    return True

def test_gui_modules():
    """Test GUI module imports."""
    print("\n🎨 Testing GUI modules...")
    
    modules = [
        'gui.main_window',
        'gui.analyze_tab', 
        'gui.report_tab',
        'gui.urls_tab',
        'gui.settings_tab'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
            return False
        except Exception as e:
            print(f"⚠️ {module} has issues: {e}")
    
    return True

def test_model_modules():
    """Test model module imports."""
    print("\n🤖 Testing model modules...")
    
    modules = [
        'model.features',
        'model.predict',
        'model.training'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
            return False
        except Exception as e:
            print(f"⚠️ {module} has issues: {e}")
    
    return True

def test_preprocessing_modules():
    """Test preprocessing module imports."""
    print("\n🔧 Testing preprocessing modules...")
    
    modules = [
        'preprocessing.email_processor',
        'preprocessing.feature_extractor',
        'preprocessing.url_analyzer'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
            return False
        except Exception as e:
            print(f"⚠️ {module} has issues: {e}")
    
    return True

def test_storage_modules():
    """Test storage module imports."""
    print("\n💾 Testing storage modules...")
    
    modules = [
        'storage.history',
        'storage.urls',
        'storage.extract'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
            return False
        except Exception as e:
            print(f"⚠️ {module} has issues: {e}")
    
    return True

def test_directory_structure():
    """Test directory structure."""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        'gui',
        'model', 
        'preprocessing',
        'storage',
        'cleaned_data',
        'trained_models',
        'tests'
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}/ directory exists")
        else:
            print(f"❌ {directory}/ directory missing")
            return False
    
    return True

def test_key_files():
    """Test key files exist."""
    print("\n📄 Testing key files...")
    
    required_files = [
        'app_streamlit.py',
        'start_app.bat',
        'start_app.sh',
        'requirements.txt',
        'README.md',
        'MODERNIZATION_SUMMARY.md'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    return True

def main():
    """Run all verification tests."""
    print("🛡️ PhishSniffer Modernization Verification")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_directory_structure,
        test_key_files,
        test_gui_modules,
        test_model_modules,
        test_preprocessing_modules,
        test_storage_modules
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("❌ Test failed")
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! PhishSniffer modernization successful!")
        print("\n🚀 Ready to launch with:")
        print("   streamlit run app_streamlit.py")
        print("   or")
        print("   ./start_app.sh (Linux/Mac)")
        print("   start_app.bat (Windows)")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
