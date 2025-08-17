"""
Email processor module - provides email parsing and feature extraction.
This module acts as the main interface for email processing in the PhishSniffer application.
"""

from .parser import extract_email_content, extract_email_features
from .preprocess import DataPreprocessor
from .utils import clean_text, extract_urls_from_text, detect_urgency_words

# Re-export main functions for easy access
__all__ = [
    'extract_email_content',
    'extract_email_features', 
    'DataPreprocessor',
    'clean_text',
    'extract_urls_from_text',
    'detect_urgency_words'
]

class EmailProcessor:
    """
    Main email processing class that combines all email analysis functionality.
    """
    
    def __init__(self):
        self.preprocessor = DataPreprocessor()
    
    def process_email(self, email_data):
        """
        Process an email and extract all relevant features.
        
        Args:
            email_data: Dictionary containing email message object or raw text
            
        Returns:
            Dictionary containing extracted features and analysis results
        """
        # Extract basic email features
        features = extract_email_features(email_data)
        
        # Clean and preprocess text content
        if 'body' in features:
            features['cleaned_body'] = clean_text(features['body'])
            features['urls'] = extract_urls_from_text(features['body'])
            features['urgency_detected'] = detect_urgency_words(features['body'])
        
        # Extract features from subject
        if 'subject' in features:
            features['cleaned_subject'] = clean_text(features['subject'])
            features['subject_urgency'] = detect_urgency_words(features['subject'])
        
        return features
    
    def extract_content(self, msg):
        """
        Extract content from email message object.
        
        Args:
            msg: Email message object
            
        Returns:
            String containing full email content
        """
        return extract_email_content(msg)
