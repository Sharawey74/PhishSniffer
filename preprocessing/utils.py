"""
Utility functions for preprocessing email data.
"""

import re
import string
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import warnings

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

warnings.filterwarnings('ignore')

class TextCleaner:
    """Class for cleaning and preprocessing email text data."""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def remove_html(self, text):
        """Remove HTML tags from text."""
        if pd.isna(text):
            return ""
        try:
            soup = BeautifulSoup(str(text), 'html.parser')
            return soup.get_text()
        except:
            return str(text)
    
    def remove_urls(self, text):
        """Remove URLs from text."""
        if pd.isna(text):
            return ""
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        return url_pattern.sub('', str(text))
    
    def remove_email_addresses(self, text):
        """Remove email addresses from text."""
        if pd.isna(text):
            return ""
        email_pattern = re.compile(r'\S+@\S+')
        return email_pattern.sub('', str(text))
    
    def remove_special_chars(self, text):
        """Remove special characters and digits."""
        if pd.isna(text):
            return ""
        text = re.sub(r'[^a-zA-Z\s]', '', str(text))
        return text
    
    def normalize_text(self, text):
        """Convert text to lowercase and remove extra whitespace."""
        if pd.isna(text):
            return ""
        text = str(text).lower()
        text = ' '.join(text.split())  # Remove extra whitespace
        return text
    
    def remove_stopwords(self, text):
        """Remove stopwords from text."""
        if pd.isna(text) or text == "":
            return ""
        try:
            words = word_tokenize(str(text))
            return ' '.join([word for word in words if word.lower() not in self.stop_words])
        except Exception:
            # Fallback to simple split if NLTK fails
            words = str(text).split()
            return ' '.join([word for word in words if word.lower() not in self.stop_words])
    
    def lemmatize_text(self, text):
        """Lemmatize words in text."""
        if pd.isna(text) or text == "":
            return ""
        try:
            words = word_tokenize(str(text))
            return ' '.join([self.lemmatizer.lemmatize(word) for word in words])
        except Exception:
            # Fallback to simple processing if NLTK fails
            return str(text)
    
    def clean_text(self, text):
        """Apply all cleaning steps to text."""
        text = self.remove_html(text)
        text = self.remove_urls(text)
        text = self.remove_email_addresses(text)
        text = self.remove_special_chars(text)
        text = self.normalize_text(text)
        text = self.remove_stopwords(text)
        text = self.lemmatize_text(text)
        return text

def detect_outliers_iqr(data, column):
    """Detect outliers using IQR method."""
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)]
    return outliers.index

def detect_outliers_zscore(data, column, threshold=3):
    """Detect outliers using Z-score method."""
    z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
    outliers = data[z_scores > threshold]
    return outliers.index

def calculate_text_features(text):
    """Calculate additional text features for outlier detection."""
    if pd.isna(text) or text == "":
        return {
            'length': 0,
            'word_count': 0,
            'sentence_count': 0,
            'avg_word_length': 0,
            'char_count': 0
        }
    
    text = str(text)
    words = text.split()
    sentences = text.split('.')
    
    return {
        'length': len(text),
        'word_count': len(words),
        'sentence_count': len(sentences),
        'avg_word_length': np.mean([len(word) for word in words]) if words else 0,
        'char_count': len([c for c in text if c.isalpha()])
    }

def load_dataset(file_path, encoding='utf-8'):
    """Load dataset with error handling for different encodings."""
    encodings = [encoding, 'latin1', 'cp1252', 'iso-8859-1']
    
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc, on_bad_lines='skip', low_memory=False)
            print(f"Successfully loaded {file_path} with encoding: {enc}")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error loading {file_path} with encoding {enc}: {e}")
            continue
    
    raise ValueError(f"Could not load {file_path} with any of the attempted encodings")

def standardize_dataset(df, text_columns, label_columns):
    """Standardize dataset by finding the best text and label columns."""
    # Find text column
    text_col = None
    for col in text_columns:
        if col in df.columns:
            text_col = col
            break
    
    if text_col is None:
        # Use first string column
        string_cols = df.select_dtypes(include=['object']).columns
        if len(string_cols) > 0:
            text_col = string_cols[0]
    
    # Find label column
    label_col = None
    for col in label_columns:
        if col in df.columns:
            label_col = col
            break
    
    if label_col is None:
        # Try to find binary column
        for col in df.columns:
            unique_vals = set(pd.unique(df[col].dropna()))
            if unique_vals <= {0, 1, 0.0, 1.0, '0', '1'}:
                label_col = col
                break
    
    return text_col, label_col

def print_dataset_info(df, name):
    """Print comprehensive dataset information."""
    print(f"\n{'='*50}")
    print(f"Dataset: {name}")
    print(f"{'='*50}")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Data types:\n{df.dtypes}")
    print(f"\nMissing values:\n{df.isnull().sum()}")
    print(f"\nMemory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# Additional utility functions that are imported elsewhere
def clean_text(text):
    """Clean text using TextCleaner class."""
    cleaner = TextCleaner()
    return cleaner.clean_text(text)

def extract_urls_from_text(text):
    """Extract URLs from text."""
    if pd.isna(text):
        return []
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.findall(str(text))

def detect_urgency_words(text):
    """Detect urgency words in text."""
    if pd.isna(text):
        return False
    
    urgency_words = [
        'urgent', 'immediate', 'emergency', 'asap', 'quickly', 'hurry',
        'deadline', 'expires', 'limited time', 'act now', 'don\'t delay',
        'time sensitive', 'critical', 'important', 'priority'
    ]
    
    text_lower = str(text).lower()
    return any(word in text_lower for word in urgency_words)
