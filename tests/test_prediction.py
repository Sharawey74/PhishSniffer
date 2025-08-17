#!/usr/bin/env python3
"""
Test script to debug prediction results and data structure
To run the test, use the following command: python tests/test_prediction.py
"""

import json
from pathlib import Path
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def ensure_import_path():
    """Add project root to Python path"""
    project_root = str(Path(__file__).parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"ℹ️ Added project root to path: {project_root}")

def test_prediction():
    """Test prediction with sample phishing email"""
    try:
        ensure_import_path()
        from model.predict import PhishingPredictor
    except ImportError as e:
        print(f"Error importing PhishingPredictor: {e}")
        return

    # Initialize predictor
    predictor = PhishingPredictor()
    predictor.load_model()
    
    # Sample phishing email content
    sample_email = """
    From: security@paypal-update.com
    To: user@example.com
    Subject: URGENT: Verify Your PayPal Account Now!
    
    Dear Valued Customer,
    
    Your PayPal account has been temporarily suspended due to suspicious activity.
    
    To restore access, please click the link below and verify your information:
    http://paypal-verification-center.suspicious-site.com
    
    Act now! Your account will be permanently closed if you don't verify within 24 hours.
    
    Click here to verify: http://bit.ly/paypal-urgent-verify
    
    Best regards,
    PayPal Security Team
    """
    
    print("🔍 Testing PhishSniffer Prediction...")
    print("=" * 50)
    
    # Make prediction
    try:
        result = predictor.predict_single(sample_email, return_details=True)
        
        print("📊 PREDICTION RESULT:")
        print(f"Is Phishing: {result.get('is_phishing', 'Unknown')}")
        print(f"Probability: {result.get('probability', 0):.4f}")
        print(f"Source: {result.get('source', 'Unknown')}")
        print()
        
        # Check details
        details = result.get('details', {})
        print("📋 DETAILS STRUCTURE:")
        for key, value in details.items():
            if isinstance(value, list):
                print(f"{key}: {len(value)} items - {value[:3]}{'...' if len(value) > 3 else ''}")
            else:
                print(f"{key}: {value}")
        print()
        
        # Check specific fields
        print("🚨 RISK FACTORS:")
        risk_factors = details.get('risk_factors', [])
        if risk_factors:
            for i, factor in enumerate(risk_factors, 1):
                print(f"  {i}. {factor}")
        else:
            print("  No risk factors found")
        print()
        
        print("🔍 FEATURES DETECTED:")
        features_detected = details.get('features_detected', [])
        if features_detected:
            for i, feature in enumerate(features_detected, 1):
                print(f"  {i}. {feature}")
        else:
            print("  No features detected")
        print()
        
        print("🔗 URLS FOUND:")
        urls = result.get('extracted_urls', [])
        if urls:
            for i, url in enumerate(urls, 1):
                print(f"  {i}. {url}")
        else:
            print("  No URLs found")
        print()
        
        print("📧 EMAIL DATA:")
        email_data = result.get('email', {})
        if email_data:
            for key, value in email_data.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")
        else:
            print("  No email data structure found")
        
        # Save result to file for debugging
        with open('debug_result.json', 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print()
        print("✅ Test completed! Result saved to debug_result.json")
        
    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_prediction()
