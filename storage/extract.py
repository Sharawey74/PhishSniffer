"""
Data extraction utilities for PhishSniffer.
"""

import os
import pandas as pd
import json
from datetime import datetime
import logging

def extract_data(source_path, target_path=None, data_type='csv'):
    """
    Extract data from various sources.
    
    Args:
        source_path (str): Path to the source data file
        target_path (str): Optional target path for processed data
        data_type (str): Type of data to extract ('csv', 'json', 'txt')
    
    Returns:
        pd.DataFrame: Extracted data
    """
    try:
        if data_type.lower() == 'csv':
            df = pd.read_csv(source_path)
        elif data_type.lower() == 'json':
            with open(source_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        elif data_type.lower() == 'txt':
            with open(source_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            df = pd.DataFrame({'text': [line.strip() for line in lines]})
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        print(f"✓ Extracted {len(df)} records from {source_path}")
        
        if target_path:
            df.to_csv(target_path, index=False)
            print(f"✓ Saved extracted data to {target_path}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error extracting data from {source_path}: {e}")
        return pd.DataFrame()

def extract_email_data(email_path):
    """
    Extract email data from file.
    
    Args:
        email_path (str): Path to email data file
    
    Returns:
        pd.DataFrame: Email data
    """
    return extract_data(email_path, data_type='csv')

def extract_multiple_datasets(dataset_paths, output_dir=None):
    """
    Extract multiple datasets and optionally combine them.
    
    Args:
        dataset_paths (list): List of paths to dataset files
        output_dir (str): Optional output directory
    
    Returns:
        dict: Dictionary of extracted dataframes
    """
    extracted_data = {}
    
    for path in dataset_paths:
        if os.path.exists(path):
            filename = os.path.basename(path).split('.')[0]
            df = extract_data(path)
            extracted_data[filename] = df
        else:
            print(f"⚠️ File not found: {path}")
    
    if output_dir and extracted_data:
        os.makedirs(output_dir, exist_ok=True)
        
        # Save individual datasets
        for name, df in extracted_data.items():
            output_path = os.path.join(output_dir, f"{name}_extracted.csv")
            df.to_csv(output_path, index=False)
            print(f"✓ Saved {name} to {output_path}")
    
    return extracted_data