"""
Complaints Routes Module for NYCHA QualityGuard Pro
Handles API endpoints for complaint analysis and processing.
"""

import os
import logging
from typing import Dict, Any, List
import pandas as pd
from flask import Blueprint, jsonify, current_app

from backend.services.ai.nlp_service import flag_urgent_complaints

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
complaints_bp = Blueprint('complaints', __name__, url_prefix='/api/complaints')

@complaints_bp.route('/analyze-urgency', methods=['POST'])
def analyze_urgency() -> tuple[Dict[str, Any], int]:
    """
    Analyze stored 311 complaints for urgency using NLP.
    
    Returns:
        tuple[Dict[str, Any], int]: JSON response and HTTP status code
            Success response:
            {
                "status": "success",
                "urgent_complaints": List[Dict],
                "count": int
            }
            Error response:
            {
                "status": "error",
                "message": str
            }
    """
    try:
        # Get the data directory path (relative to project root)
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data')
        logger.info(f"Looking for data files in: {data_dir}")
        
        if not os.path.exists(data_dir):
            logger.error(f"Data directory does not exist: {data_dir}")
            return jsonify({
                'status': 'error',
                'message': 'Data directory not found'
            }), 404
        
        # Find the most recent 311 data file
        data_files = [f for f in os.listdir(data_dir) if f.startswith('311_') and f.endswith('.csv')]
        if not data_files:
            logger.error(f"No 311 data files found in {data_dir}")
            return jsonify({
                'status': 'error',
                'message': 'No 311 data files found in data directory'
            }), 404
        
        # Sort by modification time and get the most recent
        latest_file = max(data_files, key=lambda x: os.path.getmtime(os.path.join(data_dir, x)))
        file_path = os.path.join(data_dir, latest_file)
        
        logger.info(f"Reading 311 data from {latest_file}")
        
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        if df.empty:
            logger.error("Empty CSV file encountered")
            return jsonify({
                'status': 'error',
                'message': 'No complaints found in the data file'
            }), 404
        
        # Process the data for urgency
        df_flagged = flag_urgent_complaints(df)
        
        # Filter for urgent complaints
        urgent_df = df_flagged[df_flagged['is_urgent']]
        
        if urgent_df.empty:
            logger.info("No urgent complaints found in the data")
            return jsonify({
                'status': 'success',
                'urgent_complaints': [],
                'count': 0,
                'message': 'No urgent complaints found'
            }), 200
        
        # Select relevant columns and convert to list of dicts
        columns_to_include = [
            'unique_key', 'created_date', 'complaint_type',
            'descriptor', 'urgent_keywords_found'
        ]
        
        # Ensure all required columns exist
        available_columns = [col for col in columns_to_include if col in urgent_df.columns]
        if not available_columns:
            logger.error(f"Required columns not found. Available columns: {urgent_df.columns.tolist()}")
            return jsonify({
                'status': 'error',
                'message': 'Required columns not found in data'
            }), 500
        
        urgent_complaints = urgent_df[available_columns].to_dict(orient='records')
        logger.info(f"Found {len(urgent_complaints)} urgent complaints")
        
        return jsonify({
            'status': 'success',
            'urgent_complaints': urgent_complaints,
            'count': len(urgent_complaints)
        }), 200
        
    except pd.errors.EmptyDataError:
        logger.error("Empty CSV file encountered")
        return jsonify({
            'status': 'error',
            'message': 'The data file is empty'
        }), 400
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Data file not found'
        }), 404
        
    except Exception as e:
        logger.error(f"Error processing complaints: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error processing complaints: {str(e)}'
        }), 500 