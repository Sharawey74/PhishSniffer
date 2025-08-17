"""
Model package for PhishSniffer.
Contains machine learning models, prediction logic, and training utilities.
"""

from .predict import PhishingPredictor
from .features import EmailFeatureExtractor
from .training import PhishingModelTrainer

__all__ = [
    'PhishingPredictor',
    'EmailFeatureExtractor', 
    'PhishingModelTrainer'
]