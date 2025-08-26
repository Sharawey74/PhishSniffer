"""
Model package for PhishSniffer.
Contains machine learning models, prediction logic, and training utilities.
"""

# Import with error handling for cloud deployment
try:
    from .predict import PhishingPredictor
    PREDICT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ PhishingPredictor import failed: {e}")
    PREDICT_AVAILABLE = False

try:
    from .features import EmailFeatureExtractor
    FEATURES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ EmailFeatureExtractor import failed: {e}")
    FEATURES_AVAILABLE = False

try:
    from .training import PhishingModelTrainer
    TRAINING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ PhishingModelTrainer import failed: {e}")
    TRAINING_AVAILABLE = False

# Export only available components
__all__ = []
if PREDICT_AVAILABLE:
    __all__.append('PhishingPredictor')
if FEATURES_AVAILABLE:
    __all__.append('EmailFeatureExtractor')
if TRAINING_AVAILABLE:
    __all__.append('PhishingModelTrainer')