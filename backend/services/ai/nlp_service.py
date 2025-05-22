"""
NLP Service for NYCHA QualityGuard Pro
Handles natural language processing tasks for complaint analysis.
"""

import re
import logging
from typing import List, Tuple, Dict, Any
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Configure logging
logger = logging.getLogger(__name__)

def ensure_nltk_resources():
    """
    Ensure all required NLTK resources are downloaded.
    This function should be called once when the module is imported.
    """
    required_resources = {
        'tokenizers/punkt': 'punkt',
        'corpora/stopwords': 'stopwords'
    }
    
    for resource_path, resource_name in required_resources.items():
        try:
            nltk.data.find(resource_path)
            logger.debug(f"NLTK resource '{resource_name}' is already downloaded")
        except LookupError:
            logger.info(f"Downloading NLTK resource '{resource_name}'...")
            nltk.download(resource_name, quiet=True)
            logger.info(f"Successfully downloaded NLTK resource '{resource_name}'")

# Download required NLTK resources
ensure_nltk_resources()

# Get English stopwords
STOPWORDS = set(stopwords.words('english'))

# Define urgent keywords and phrases
URGENT_KEYWORDS = [
    # Safety and Health
    'fire', 'smoke', 'gas leak', 'carbon monoxide',
    'collapse', 'unsafe', 'dangerous', 'hazard',
    'mold', 'asbestos', 'lead', 'infestation',
    
    # Essential Services
    'no heat', 'no hot water', 'no water',
    'no electricity', 'power outage',
    'elevator stuck', 'elevator broken',
    
    # Vulnerable Populations
    'child', 'children', 'baby', 'infant',
    'elderly', 'senior', 'disabled',
    'medical', 'health', 'emergency',
    
    # Structural Issues
    'ceiling collapse', 'wall collapse',
    'flood', 'water damage', 'leak',
    'broken window', 'broken door',
    
    # Security
    'break in', 'intruder', 'squatter',
    'illegal entry', 'forced entry'
]

def check_text_for_urgency(text: str) -> Tuple[bool, List[str]]:
    """
    Check if a text contains any urgent keywords or phrases.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        Tuple[bool, List[str]]: A tuple containing:
            - Boolean indicating if any urgent keywords were found
            - List of matched urgent keywords/phrases
    """
    if not isinstance(text, str) or not text.strip():
        return False, []
    
    # Tokenize and convert to lowercase
    tokens = word_tokenize(text.lower())
    text_lower = text.lower()
    
    # Remove stopwords from tokens for potential future use
    tokens_no_stopwords = [token for token in tokens if token not in STOPWORDS]
    
    # Find matches
    matches = []
    for keyword in URGENT_KEYWORDS:
        # Use regex for phrase matching
        if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
            matches.append(keyword)
    
    return bool(matches), matches

def flag_urgent_complaints(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flag urgent complaints in the DataFrame based on text analysis.
    
    Args:
        df (pd.DataFrame): Input DataFrame containing complaint data.
            Expected columns: 'descriptor', 'complaint_type', 'resolution_description'
    
    Returns:
        pd.DataFrame: DataFrame with added columns:
            - 'is_urgent': Boolean indicating if complaint is urgent
            - 'urgent_keywords_found': List of matched urgent keywords
    """
    logger.info("Starting urgent complaint analysis...")
    
    # Create a copy to avoid modifying the original
    df = df.copy()
    
    # Initialize new columns
    df['is_urgent'] = False
    df['urgent_keywords_found'] = [[] for _ in range(len(df))]
    
    # Columns to check for urgency
    text_columns = ['descriptor', 'complaint_type', 'resolution_description']
    
    # Process each row
    for idx, row in df.iterrows():
        all_matches = []
        
        # Check each text column
        for col in text_columns:
            if col in row and pd.notna(row[col]):
                is_urgent, matches = check_text_for_urgency(str(row[col]))
                if is_urgent:
                    all_matches.extend(matches)
        
        # Update row with results
        if all_matches:
            df.at[idx, 'is_urgent'] = True
            df.at[idx, 'urgent_keywords_found'] = list(set(all_matches))  # Remove duplicates
    
    # Log results
    urgent_count = df['is_urgent'].sum()
    logger.info(f"Found {urgent_count} urgent complaints out of {len(df)} total complaints")
    
    # Log distribution of urgent keywords
    keyword_counts = {}
    for keywords in df[df['is_urgent']]['urgent_keywords_found']:
        for keyword in keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    logger.info("Top urgent keywords found:")
    for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        logger.info(f"  - {keyword}: {count} occurrences")
    
    return df

if __name__ == '__main__':
    # Example usage
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    from services.data_ingestion_service import fetch_and_process_311_data
    
    # Fetch some data
    df = fetch_and_process_311_data(start_date='2024-01-01', max_pages=1)
    
    if not df.empty:
        # Process the data
        df_flagged = flag_urgent_complaints(df)
        
        # Display results
        print(f"\nProcessed {len(df_flagged)} complaints")
        print(f"Found {df_flagged['is_urgent'].sum()} urgent complaints")
        
        # Show some examples
        print("\nExample urgent complaints:")
        urgent_examples = df_flagged[df_flagged['is_urgent']].head()
        for _, row in urgent_examples.iterrows():
            print(f"\nComplaint Type: {row['complaint_type']}")
            print(f"Descriptor: {row['descriptor']}")
            print(f"Urgent Keywords: {', '.join(row['urgent_keywords_found'])}") 