#!/usr/bin/env python3
"""
Example client code for PhishSniffer REST API.
Demonstrates how to interact with the API endpoints.
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000/api"

def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health check passed: {result}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error in health check: {e}")
        return False

def analyze_email_text(email_content):
    """Analyze email content using the API."""
    print(f"📧 Analyzing email content...")
    
    try:
        payload = {
            "email_content": email_content,
            "options": {
                "include_details": True,
                "extract_urls": True,
                "return_features": False
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/analyze/text",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis completed:")
            print(f"   🎯 Is Phishing: {result['is_phishing']}")
            print(f"   📊 Probability: {result['probability']:.2%}")
            print(f"   🔍 Confidence: {result['confidence_level']}")
            print(f"   ⚠️ Risk Factors: {', '.join(result['risk_factors']) if result['risk_factors'] else 'None'}")
            print(f"   📋 Features: {', '.join(result['features_detected']) if result['features_detected'] else 'None'}")
            return result
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error in email analysis: {e}")
        return None

def analyze_email_file(file_path):
    """Analyze email file using the API."""
    print(f"📁 Analyzing email file: {file_path}")
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (file_path, file, 'text/plain')}
            
            response = requests.post(
                f"{BASE_URL}/v1/analyze/file",
                files=files
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ File analysis completed:")
            print(f"   📁 Filename: {result['filename']}")
            print(f"   📏 File size: {result['file_size']} bytes")
            
            analysis = result['analysis']
            print(f"   🎯 Is Phishing: {analysis['is_phishing']}")
            print(f"   📊 Probability: {analysis.get('probability', 0):.2%}")
            
            return result
        else:
            print(f"❌ File analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error in file analysis: {e}")
        return None

def get_model_info():
    """Get information about the loaded model."""
    print("🤖 Getting model information...")
    
    try:
        response = requests.get(f"{BASE_URL}/v1/models/info")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Model information:")
            print(f"   🔧 Model Type: {result['model_type']}")
            print(f"   🎯 Threshold: {result['threshold']}")
            print(f"   📊 Has Feature Extractor: {result['has_feature_extractor']}")
            
            if result['metadata']:
                metadata = result['metadata']
                print(f"   📅 Training Date: {metadata.get('timestamp', 'Unknown')}")
                print(f"   🎯 Test Accuracy: {metadata.get('test_accuracy', 'Unknown')}")
            
            return result
        else:
            print(f"❌ Failed to get model info: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting model info: {e}")
        return None

def analyze_urls(urls):
    """Analyze URLs for suspicious indicators."""
    print(f"🔗 Analyzing {len(urls)} URL(s)...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/urls/analyze",
            json=urls,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ URL analysis completed:")
            
            for i, analysis in enumerate(result['url_analyses'], 1):
                print(f"   🔗 URL {i}: {analysis['url']}")
                print(f"      🎯 Suspicious: {analysis['is_suspicious']}")
                print(f"      🏷️ Domain: {analysis['domain']}")
                print(f"      📊 Safety Score: {analysis['safety_score']:.1%}")
                if analysis['risk_factors']:
                    print(f"      ⚠️ Risk Factors: {', '.join(analysis['risk_factors'])}")
                print()
            
            return result
        else:
            print(f"❌ URL analysis failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error in URL analysis: {e}")
        return None

def main():
    """Main example function."""
    print("=" * 80)
    print("🛡️ PHISHSNIFFER REST API - EXAMPLE CLIENT")
    print("=" * 80)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Test 1: Health check
    if not test_health_check():
        print("❌ API server is not running. Please start it first:")
        print("   python api/start_api.py")
        return
    
    print("\n" + "-" * 60)
    
    # Test 2: Model information
    get_model_info()
    
    print("\n" + "-" * 60)
    
    # Test 3: Analyze sample phishing email
    phishing_email = """
    Subject: URGENT: Your account will be suspended!
    
    Dear valued customer,
    
    We have detected unusual activity on your account. 
    Your account will be suspended within 24 hours unless you verify your information immediately.
    
    Click here to verify: http://bit.ly/fake-bank-verify
    
    Enter your username, password, and credit card details to maintain access.
    
    Act now before it's too late!
    
    Best regards,
    Security Team
    """
    
    analyze_email_text(phishing_email)
    
    print("\n" + "-" * 60)
    
    # Test 4: Analyze sample legitimate email
    legitimate_email = """
    Subject: Weekly Newsletter - Security Tips
    
    Hello,
    
    Here are this week's cybersecurity tips:
    
    1. Always verify sender authenticity
    2. Check URLs before clicking
    3. Use strong, unique passwords
    4. Enable two-factor authentication
    
    Stay safe online!
    
    Best regards,
    IT Security Team
    """
    
    analyze_email_text(legitimate_email)
    
    print("\n" + "-" * 60)
    
    # Test 5: URL analysis
    test_urls = [
        "https://google.com",
        "http://192.168.1.1/phishing",
        "https://bit.ly/suspicious-link",
        "https://legitimate-bank.com/login"
    ]
    
    analyze_urls(test_urls)
    
    print("\n" + "=" * 80)
    print("✅ API testing completed!")
    print("📚 For more examples, check the API documentation at:")
    print(f"   {BASE_URL}/docs")
    print("=" * 80)

if __name__ == "__main__":
    main()
