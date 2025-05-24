"""
Agents Routes Module for NYCHA QualityGuard Pro
Defines API endpoints for AI agent interactions.
"""

import logging
from typing import Dict, Any, Tuple
from flask import Blueprint, jsonify

# Import the daily briefing agent
from backend.agents.daily_briefing_agent import generate_daily_briefing

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
agents_bp = Blueprint('agents_api', __name__, url_prefix='/api/agents')

@agents_bp.route('/daily-briefing', methods=['GET'])
def get_daily_briefing() -> Tuple[Dict[str, Any], int]:
    """
    Endpoint to generate and retrieve the daily quality briefing.
    
    Returns:
        Tuple[Dict[str, Any], int]: JSON response and HTTP status code
        - On success: {"status": "success", "briefing_text": str}
        - On error: {"status": "error", "message": str}
    """
    try:
        logger.info("Generating daily briefing...")
        briefing_text = generate_daily_briefing()
        
        # Check if the briefing generation was successful
        if briefing_text.startswith("Error:"):
            logger.error(f"Briefing generation failed: {briefing_text}")
            return {
                "status": "error",
                "message": "Failed to generate daily briefing. Please check server logs."
            }, 500
        
        logger.info("Daily briefing generated successfully")
        return {
            "status": "success",
            "briefing_text": briefing_text
        }, 200
        
    except Exception as e:
        error_msg = f"Error generating daily briefing: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": "Failed to generate daily briefing. Please check server logs."
        }, 500 