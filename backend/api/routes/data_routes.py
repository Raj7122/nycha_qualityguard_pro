"""
Data Routes Module for NYCHA QualityGuard Pro
Defines API endpoints for data ingestion and processing.
"""

import os
import logging
from typing import Dict, Any, Tuple
from datetime import datetime
from flask import Blueprint, jsonify, request
from backend.services.data_ingestion_service import fetch_and_process_311_data

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
data_bp = Blueprint('data_api', __name__, url_prefix='/api/data')

def ensure_data_directory() -> str:
    """
    Ensure the data directory exists and return its path.
    
    Returns:
        str: Path to the data directory
    """
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def save_dataframe_to_csv(df: Any, data_dir: str) -> str:
    """
    Save DataFrame to CSV file with timestamp.
    
    Args:
        df: Pandas DataFrame to save
        data_dir: Directory to save the file in
    
    Returns:
        str: Path to the saved file
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'311_hpd_processed_data_{timestamp}.csv'
    filepath = os.path.join(data_dir, filename)
    df.to_csv(filepath, index=False)
    return filepath

@data_bp.route('/ingest-311', methods=['POST'])
def ingest_311_data() -> Tuple[Dict[str, Any], int]:
    """
    Endpoint to ingest 311 service request data.
    
    Returns:
        Tuple[Dict[str, Any], int]: JSON response and HTTP status code
    """
    try:
        # Get optional parameters from request
        request_data = request.get_json() or {}
        start_date = request_data.get('start_date')
        agency = request_data.get('agency', 'HPD')
        
        logger.info(f"Starting 311 data ingestion for agency: {agency}")
        
        # Fetch and process data
        df = fetch_and_process_311_data(
            start_date=start_date,
            agency_filter=agency
        )
        
        # Check if we got any data
        if df.empty:
            logger.warning("No data received from 311 service")
            return {
                "status": "error",
                "message": "No data found for the specified parameters."
            }, 404
        
        # Ensure data directory exists
        data_dir = ensure_data_directory()
        
        # Save data to CSV
        filepath = save_dataframe_to_csv(df, data_dir)
        logger.info(f"311 data saved to: {filepath}")
        
        # Return success response
        return {
            "status": "success",
            "message": "311 data ingestion complete.",
            "records_processed": len(df),
            "file_path": filepath
        }, 200
        
    except Exception as e:
        logger.error(f"Error in 311 data ingestion: {str(e)}")
        return {
            "status": "error",
            "message": "Data ingestion failed. Please try again later."
        }, 500 