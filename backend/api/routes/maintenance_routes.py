"""
Maintenance Routes Module for NYCHA QualityGuard Pro

This module defines a Flask Blueprint for maintenance-related API endpoints.
"""

import logging
from typing import Dict, Any, List
from flask import Blueprint, jsonify

from backend.services.ai.rework_predictor_service import predict_rework_risk_for_work_orders

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
maintenance_bp = Blueprint('maintenance_api', __name__, url_prefix='/api/maintenance')

@maintenance_bp.route('/rework-assessments', methods=['GET'])
def get_rework_assessments() -> Dict[str, Any]:
    """
    GET endpoint to retrieve rework risk assessments for synthetic work orders.
    Calls predict_rework_risk_for_work_orders, selects relevant columns, and returns a JSON response.
    """
    try:
        # Call the rework predictor service
        df = predict_rework_risk_for_work_orders()
        if df.empty:
            return jsonify({
                "status": "error",
                "message": "No rework assessments available."
            }), 404

        # Select relevant columns for the response
        relevant_columns = [
            'wo_id', 'asset_id', 'asset_type', 'assigned_contractor_id',
            'closed_date', 'resolution_text_simulated',
            'predicted_rework_risk_score', 'predicted_risk_factors'
        ]
        selected_df = df[relevant_columns]

        # Convert DataFrame to a list of dictionaries
        assessments = selected_df.to_dict(orient='records')

        # Return success response
        return jsonify({
            "status": "success",
            "rework_assessments": assessments,
            "count": len(assessments)
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving rework assessments: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve rework assessments. Please try again later."
        }), 500 