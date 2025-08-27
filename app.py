#!/usr/bin/env python3
"""
PhishSniffer - Complete Email Security Pipeline
Main orchestrator for preprocessing, training, and GUI launch.

Workflow:
1. Dataset Input: Load raw datasets from data/
2. Preprocessing Pipeline: Clean, normalize, EDA, outlier detection
3. Model Pipeline: Feature extraction, training, evaluation
4. Tests: Unit tests for all components
5. Streamlit GUI: Launch web interface

Usage:
    python app.py [--skip-preprocessing] [--skip-training] [--model-type MODEL]
"""

import os
import sys
import argparse
import time
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def print_banner():
    """Print application banner."""
    print("=" * 100)
    print("🛡️  PHISHSNIFFER - ADVANCED EMAIL SECURITY PLATFORM")
    print("=" * 100)
    print("🔍 AI-Powered Phishing Detection & Analysis")
    print("📊 Complete ML Pipeline with Modern Web Interface")
    print("🌐 Streamlit-based GUI for Interactive Analysis")
    print("=" * 100)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)

def run_preprocessing():
    """Run the preprocessing pipeline."""
    print("\n🔧 STEP 1: DATA PREPROCESSING PIPELINE")
    print("-" * 80)
    
    try:
        from preprocessing.preprocess import DataPreprocessor
        
        preprocessor = DataPreprocessor()
        success = preprocessor.run_full_pipeline()
        
        if success:
            print("\n✅ Preprocessing completed successfully!")
            return True
        else:
            print("\n❌ Preprocessing failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error in preprocessing: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_model_training(model_type='random_forest', use_grid_search=True):
    """Run the model training pipeline."""
    print(f"\n🤖 STEP 2: MODEL TRAINING PIPELINE ({model_type.upper()})")
    print("-" * 80)
    
    try:
        from model.training import PhishingModelTrainer
        
        trainer = PhishingModelTrainer()
        success = trainer.run_full_pipeline(
            model_type=model_type,
            use_grid_search=use_grid_search
        )
        
        if success:
            print("\n✅ Model training completed successfully!")
            return True
        else:
            print("\n❌ Model training failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error in model training: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_tests():
    """Run comprehensive unit tests."""
    print("\n🧪 STEP 3: RUNNING COMPREHENSIVE UNIT TESTS")
    print("-" * 80)
    
    try:
        # Import the comprehensive test runner
        from tests.run_tests import run_all_tests, validate_test_environment
        
        # First validate test environment
        print("🔧 Validating test environment...")
        if not validate_test_environment():
            print("❌ Test environment validation failed!")
            return False
        
        # Run all tests with comprehensive coverage
        all_passed = run_all_tests(verbose=True)
        
        if all_passed:
            print("\n✅ All comprehensive tests passed!")
            return True
        else:
            print("\n❌ Some tests failed. Please check the output above.")
            return False
            
    except ImportError as e:
        print(f"⚠️ Could not import comprehensive test runner: {e}")
        print("Falling back to basic pytest execution...")
        
        # Fallback to pytest
        try:
            import subprocess
            
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'
            ], capture_output=True, text=True, cwd=project_root)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            if result.returncode == 0:
                print("\n✅ All tests passed!")
                return True
            else:
                print(f"\n⚠️ Some tests failed (exit code: {result.returncode})")
                return False
                
        except FileNotFoundError:
            print("❌ pytest not found. Running basic import tests...")
            try:
                # Run basic import tests
                from tests.test_imports import test_all_imports
                test_all_imports()
                print("\n✅ Basic import tests passed!")
                return True
            except Exception as test_error:
                print(f"❌ Error running basic tests: {test_error}")
                return False
    except Exception as e:
        print(f"❌ Error running comprehensive tests: {e}")
        return False

def launch_gui():
    """Launch the Streamlit GUI."""
    print("\n🌐 STEP 4: LAUNCHING STREAMLIT GUI")
    print("-" * 80)
    
    try:
        import subprocess
        import webbrowser
        import time
        
        print("🚀 Starting Streamlit server...")
        print("📱 Web interface will be available at: http://localhost:8501")
        print("🔄 Opening browser automatically...")
        
        # Start Streamlit in background
        process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 
            'streamlit_app.py',
            '--server.port=8501',
            '--server.address=localhost',
            '--server.headless=false'
        ], cwd=project_root)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Open browser
        try:
            webbrowser.open('http://localhost:8501')
        except Exception as e:
            print(f"⚠️ Could not open browser automatically: {e}")
            print("Please manually open: http://localhost:8501")
        
        print("\n✅ Streamlit GUI launched successfully!")
        print("🎯 Application is ready for use!")
        print("\n📋 GUI Features:")
        print("   📧 Email Analysis - Upload files or paste content")
        print("   📊 Reports & Analytics - View detection results")
        print("   🔗 URL Management - Track suspicious URLs")
        print("   ⚙️ Settings - Configure detection parameters")
        
        print(f"\n{'='*80}")
        print("🎉 PHISHSNIFFER STARTUP COMPLETE!")
        print(f"{'='*80}")
        print("✅ All components initialized successfully")
        print("🌐 Web interface running at: http://localhost:8501")
        print("🛑 Press Ctrl+C to stop the application")
        print(f"{'='*80}")
        
        # Keep the process running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Streamlit server...")
            process.terminate()
            process.wait()
            print("✅ Application stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_dependencies():
    """Check if all required dependencies are available."""
    print("\n🔍 CHECKING DEPENDENCIES")
    print("-" * 80)
    
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'sklearn', 
        'plotly', 'joblib', 'matplotlib', 'seaborn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("📦 Please install with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies satisfied!")
        return True

def check_data_availability():
    """Check if required data files are available."""
    print("\n📂 CHECKING DATA AVAILABILITY")
    print("-" * 80)
    
    data_dir = os.path.join(project_root, 'data')
    required_files = [
        'CEAS_08.csv', 'Nigerian_Fraud.csv', 'Nazario.csv',
        'Enron.csv', 'Ling.csv', 'SpamAssasin.csv'
    ]
    
    available_files = []
    missing_files = []
    
    for filename in required_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"✅ {filename} ({size_mb:.1f} MB)")
            available_files.append(filename)
        else:
            print(f"❌ {filename} - MISSING")
            missing_files.append(filename)
    
    if available_files:
        print(f"\n✅ Found {len(available_files)} dataset(s)")
        if missing_files:
            print(f"⚠️ Missing {len(missing_files)} dataset(s) - will continue with available data")
        return True
    else:
        print(f"\n❌ No datasets found in {data_dir}")
        print("📄 Please ensure at least one dataset is available")
        return False

def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description='PhishSniffer - Complete Email Security Pipeline')
    parser.add_argument('--skip-preprocessing', action='store_true', 
                       help='Skip preprocessing step (use existing cleaned data)')
    parser.add_argument('--skip-training', action='store_true',
                       help='Skip model training step (use existing trained model)')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Skip unit tests')
    parser.add_argument('--model-type', default='random_forest',
                       choices=['random_forest', 'gradient_boosting', 'logistic_regression', 'svm', 'naive_bayes', 'all'],
                       help='Type of model to train')
    parser.add_argument('--no-grid-search', action='store_true',
                       help='Disable hyperparameter grid search (faster training)')
    parser.add_argument('--gui-only', action='store_true',
                       help='Launch GUI only (skip all preprocessing and training)')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install required packages.")
        return False
    
    # GUI-only mode
    if args.gui_only:
        print("\n🌐 GUI-ONLY MODE: Launching Streamlit interface directly...")
        return launch_gui()
    
    # Check data availability
    if not args.skip_preprocessing and not check_data_availability():
        print("\n❌ Data check failed. Please ensure datasets are available.")
        return False
    
    # Step 1: Preprocessing
    if not args.skip_preprocessing:
        if not run_preprocessing():
            print("\n❌ Preprocessing failed. Cannot continue.")
            return False
    else:
        print("\n⏭️ Skipping preprocessing (using existing cleaned data)")
    
    # Step 2: Model Training
    if not args.skip_training:
        if not run_model_training(
            model_type=args.model_type,
            use_grid_search=not args.no_grid_search
        ):
            print("\n❌ Model training failed. Cannot continue.")
            return False
    else:
        print("\n⏭️ Skipping model training (using existing trained model)")
    
    # Step 3: Tests
    if not args.skip_tests:
        test_success = run_tests()
        if not test_success:
            print("\n⚠️ Some tests failed, but continuing to GUI launch...")
    else:
        print("\n⏭️ Skipping unit tests")
    
    # Step 4: Launch GUI
    return launch_gui()

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)