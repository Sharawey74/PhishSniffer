#!/usr/bin/env python3
"""
Simple test to verify prediction works
"""

try:
    from model.predict import PhishingPredictor
    
    print("🔄 Initializing PhishingPredictor...")
    predictor = PhishingPredictor()
    
    print("🔄 Loading model...")
    predictor.load_model()
    
    print("🔄 Making prediction...")
    sample_email = """
    From: security@paypal-verification.com
    Subject: URGENT Account Suspension Notice
    
    Your account has been suspended. Click here immediately:
    http://paypal-security-verify.suspicious-domain.com
    
    Enter your password and credit card details to restore access.
    """
    
    result = predictor.predict_single(sample_email, return_details=True)
    
    print("\n✅ SUCCESS! Result received:")
    print(f"📊 Is Phishing: {result.get('is_phishing')}")
    print(f"📊 Probability: {result.get('probability'):.4f}")
    print(f"📊 Result Keys: {list(result.keys())}")
    
    details = result.get('details', {})
    print(f"📊 Details Keys: {list(details.keys())}")
    
    if 'risk_factors' in details:
        print(f"📊 Risk Factors ({len(details['risk_factors'])}): {details['risk_factors']}")
    
    if 'features_detected' in details:
        print(f"📊 Features Detected ({len(details['features_detected'])}): {details['features_detected']}")
    
    print("\n🎉 Test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
