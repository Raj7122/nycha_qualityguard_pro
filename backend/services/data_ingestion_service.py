"""
Data Ingestion Service for NYCHA QualityGuard Pro
Handles fetching and processing of 311 service requests from NYC OpenData API.
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union, Any
import requests
import pandas as pd
from pandas import DataFrame
from dotenv import load_dotenv

# Load environment variables if not already loaded
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def fetch_and_process_311_data(
    start_date: Optional[str] = None,
    agency_filter: str = 'HPD',
    max_pages: int = 100
) -> pd.DataFrame:
    """
    Fetch and process 311 service requests from NYC OpenData API.
    
    Args:
        start_date (str, optional): Start date in 'YYYY-MM-DD' format. 
            Defaults to January 1st of the previous year.
        agency_filter (str, optional): Agency to filter by. Defaults to 'HPD'.
        max_pages (int, optional): Maximum number of pages to fetch. Defaults to 100.
    
    Returns:
        pd.DataFrame: Processed 311 service request data.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting 311 data fetch for agency: {agency_filter}")

    # Get API token from environment
    app_token = os.getenv('NYC_OPENDATA_APP_TOKEN')
    if not app_token:
        logger.warning("NYC_OPENDATA_APP_TOKEN not found. API calls may be throttled.")

    # Set default start date if not provided
    if not start_date:
        last_year = datetime.now().year - 1
        start_date = f"{last_year}-01-01"
    
    # Base API endpoint
    base_url = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
    
    # Essential columns to fetch
    columns = [
        'unique_key', 'created_date', 'agency', 'complaint_type',
        'descriptor', 'resolution_description', 'incident_address',
        'borough', 'bbl', 'latitude', 'longitude'
    ]
    
    # Construct SoQL query
    where_clause = (
        f"agency='{agency_filter}' AND "
        f"created_date >= '{start_date}T00:00:00.000'"
    )
    
    # Initialize variables for pagination
    offset = 0
    limit = 1000
    all_records: List[Dict] = []
    
    try:
        while offset < (max_pages * limit):
            # Construct query parameters
            params = {
                '$select': ','.join(columns),
                '$where': where_clause,
                '$limit': limit,
                '$offset': offset,
                '$order': 'created_date DESC'
            }
            
            # Prepare headers
            headers = {'X-App-Token': app_token} if app_token else {}
            
            # Make API request
            logger.info(f"Fetching records {offset} to {offset + limit}")
            response = requests.get(
                base_url,
                params=params,
                headers=headers,
                timeout=30
            )
            
            # Check response status
            response.raise_for_status()
            
            # Parse response
            records = response.json()
            
            # Break if no more records
            if not records:
                logger.info("No more records to fetch")
                break
                
            # Add records to collection
            all_records.extend(records)
            
            # Increment offset for next page
            offset += limit
            
            # Polite delay between requests
            time.sleep(0.2)
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()
    
    # Check if we got any records
    if not all_records:
        logger.warning("No records fetched")
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(all_records)
    
    # Data cleaning
    try:
        # Convert created_date to datetime
        df['created_date'] = pd.to_datetime(df['created_date'])
        
        # Clean text fields
        text_columns = ['complaint_type', 'descriptor', 'resolution_description']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].fillna('').str.lower()
        
        logger.info(f"Successfully processed {len(df)} records")
        
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return pd.DataFrame()
    
    return df

if __name__ == '__main__':
    # Example usage
    df = fetch_and_process_311_data()
    print(f"Fetched {len(df)} records")
    if not df.empty:
        print("\nSample data:")
        print(df.head()) 