"""
Comprehensive test runner for PhishSniffer project.
"""

import os
import sys
import unittest
import importlib
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def run_all_tests(verbose=True):
    """
    Run all unit tests for the PhishSniffer project.
    
    Args:
        verbose (bool): Whether to print detailed output
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    print("🚀 Starting PhishSniffer Comprehensive Test Suite")
    print("=" * 60)
    print(f"📅 Test run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test modules to run
    test_modules = [
        'test_imports',
        'test_preprocessing', 
        'test_model_training',
        'test_gui'
    ]
    
    total_tests = 0
    total_failures = 0
    failed_modules = []
    
    for module_name in test_modules:
        print(f"\n🔍 Running {module_name}...")
        print("-" * 40)
        
        try:
            # Import test module
            module = importlib.import_module(f'tests.{module_name}')
            
            # Load tests from module
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)
            
            # Run tests
            if verbose:
                runner = unittest.TextTestRunner(verbosity=2)
            else:
                runner = unittest.TextTestRunner(verbosity=1)
            
            result = runner.run(suite)
            
            # Track results
            tests_run = result.testsRun
            failures = len(result.failures) + len(result.errors)
            
            total_tests += tests_run
            total_failures += failures
            
            if failures == 0:
                print(f"✅ {module_name}: All {tests_run} tests passed!")
            else:
                print(f"❌ {module_name}: {failures}/{tests_run} tests failed")
                failed_modules.append(module_name)
                
                if verbose:
                    print("\nFailure details:")
                    for failure in result.failures + result.errors:
                        print(f"  - {failure[0]}")
                        print(f"    {failure[1].strip()}")
            
        except ImportError as e:
            print(f"⚠️ Could not import {module_name}: {e}")
            failed_modules.append(module_name)
        except Exception as e:
            print(f"❌ Error running {module_name}: {e}")
            failed_modules.append(module_name)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    success_rate = ((total_tests - total_failures) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total tests run: {total_tests}")
    print(f"Tests passed: {total_tests - total_failures}")
    print(f"Tests failed: {total_failures}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if failed_modules:
        print(f"\nModules with failures: {', '.join(failed_modules)}")
    
    if total_failures == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("PhishSniffer is ready for deployment!")
        return True
    else:
        print(f"\n⚠️ {total_failures} tests failed. Please review and fix issues.")
        return False

def run_specific_test(test_name, verbose=True):
    """
    Run a specific test module.
    
    Args:
        test_name (str): Name of the test module (without 'test_' prefix)
        verbose (bool): Whether to print detailed output
    
    Returns:
        bool: True if tests pass, False otherwise
    """
    module_name = f'test_{test_name}' if not test_name.startswith('test_') else test_name
    
    print(f"🔍 Running specific test: {module_name}")
    print("-" * 40)
    
    try:
        # Import test module
        module = importlib.import_module(f'tests.{module_name}')
        
        # Load and run tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        
        if verbose:
            runner = unittest.TextTestRunner(verbosity=2)
        else:
            runner = unittest.TextTestRunner(verbosity=1)
        
        result = runner.run(suite)
        
        # Check results
        failures = len(result.failures) + len(result.errors)
        
        if failures == 0:
            print(f"✅ {module_name}: All tests passed!")
            return True
        else:
            print(f"❌ {module_name}: {failures} tests failed")
            return False
            
    except Exception as e:
        print(f"❌ Error running {module_name}: {e}")
        return False

def check_test_coverage():
    """
    Check test coverage for the project.
    
    Returns:
        dict: Coverage information
    """
    print("📈 Checking test coverage...")
    
    # Define expected test coverage areas
    coverage_areas = {
        'imports': 'test_imports.py',
        'preprocessing': 'test_preprocessing.py', 
        'model_training': 'test_model_training.py',
        'gui': 'test_gui.py'
    }
    
    coverage_status = {}
    
    for area, test_file in coverage_areas.items():
        test_path = os.path.join('tests', test_file)
        
        if os.path.exists(test_path):
            coverage_status[area] = "✅ Covered"
        else:
            coverage_status[area] = "❌ Missing"
    
    print("\nTest Coverage Status:")
    for area, status in coverage_status.items():
        print(f"  {area}: {status}")
    
    return coverage_status

def validate_test_environment():
    """
    Validate that the test environment is properly set up.
    
    Returns:
        bool: True if environment is valid, False otherwise
    """
    print("🔧 Validating test environment...")
    
    # Check required directories
    required_dirs = ['tests', 'model', 'gui', 'preprocessing', 'storage']
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ Missing directories: {', '.join(missing_dirs)}")
        return False
    
    # Check test files exist
    test_files = [
        'tests/test_imports.py',
        'tests/test_preprocessing.py',
        'tests/test_model_training.py', 
        'tests/test_gui.py'
    ]
    
    missing_files = []
    for test_file in test_files:
        if not os.path.exists(test_file):
            missing_files.append(test_file)
    
    if missing_files:
        print(f"❌ Missing test files: {', '.join(missing_files)}")
        return False
    
    print("✅ Test environment is valid!")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='PhishSniffer Test Runner')
    parser.add_argument('--module', '-m', help='Run specific test module')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode (less verbose)')
    parser.add_argument('--coverage', '-c', action='store_true', help='Check test coverage')
    parser.add_argument('--validate', '-v', action='store_true', help='Validate test environment')
    
    args = parser.parse_args()
    
    # Change to project directory
    os.chdir(project_root)
    
    if args.validate:
        validate_test_environment()
    elif args.coverage:
        check_test_coverage()
    elif args.module:
        success = run_specific_test(args.module, verbose=not args.quiet)
        sys.exit(0 if success else 1)
    else:
        success = run_all_tests(verbose=not args.quiet)
        sys.exit(0 if success else 1)
