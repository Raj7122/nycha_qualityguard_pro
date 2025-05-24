"""
Daily Briefing Agent for NYCHA QualityGuard Pro

This module defines a DailyBriefingAgent that generates concise daily quality briefings
for NYCHA Superintendents by analyzing urgent complaints and high-risk work orders.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from smolagents import CodeAgent

# Import required services
from backend.services.ai.nlp_service import flag_urgent_complaints
from backend.services.ai.rework_predictor_service import predict_rework_risk_for_work_orders
from backend.services.data_ingestion_service import fetch_and_process_311_data

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_today_urgent_complaints() -> List[Dict[str, Any]]:
    """
    Fetches and analyzes recent 311 HPD complaints to identify urgent issues.
    Returns a list of dictionaries, each representing an urgent complaint with
    'unique_key', 'descriptor', and 'urgent_keywords_found', or an empty list if none.
    """
    try:
        # Get data for the last 24 hours
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        df = fetch_and_process_311_data(start_date=yesterday)
        
        if df.empty:
            logger.warning("No complaints data available for the last 24 hours")
            return []
        
        # Flag urgent complaints
        urgent_df = flag_urgent_complaints(df)
        
        # Sort by urgency score and get top 5
        top_urgent = urgent_df.nlargest(5, 'urgency_score')
        
        # Format results
        urgent_complaints = []
        for _, row in top_urgent.iterrows():
            urgent_complaints.append({
                'unique_key': row['complaint_id'],
                'descriptor': row['complaint_descriptor'],
                'urgent_keywords_found': row.get('keywords', [])
            })
        
        return urgent_complaints
    
    except Exception as e:
        logger.error(f"Error in get_today_urgent_complaints: {str(e)}")
        return []

def get_recent_high_rework_risk_jobs() -> List[Dict[str, Any]]:
    """
    Analyzes recently completed synthetic work orders to predict high rework risk.
    Returns a list of dictionaries, each representing a high-risk job with
    'wo_id', 'asset_type', 'predicted_rework_risk_score', and 'predicted_risk_factors',
    or an empty list if none.
    """
    try:
        # Get work orders with risk predictions
        df = predict_rework_risk_for_work_orders()
        
        if df.empty:
            logger.warning("No work orders data available")
            return []
        
        # Filter for high risk (score > 0.6) and sort by score
        high_risk_df = df[df['predicted_rework_risk_score'] > 0.6].nlargest(5, 'predicted_rework_risk_score')
        
        # Format results
        high_risk_jobs = []
        for _, row in high_risk_df.iterrows():
            high_risk_jobs.append({
                'wo_id': row['wo_id'],
                'asset_type': row['asset_type'],
                'predicted_rework_risk_score': float(row['predicted_rework_risk_score']),
                'predicted_risk_factors': row['predicted_risk_factors']
            })
        
        return high_risk_jobs
    
    except Exception as e:
        logger.error(f"Error in get_recent_high_rework_risk_jobs: {str(e)}")
        return []

def generate_daily_briefing() -> str:
    """
    Generate a concise daily quality briefing for the NYCHA Superintendent using smolagents.
    
    The briefing includes:
    1. Today's most urgent new 311 complaints
    2. Recently completed work orders with high rework risk
    3. Critical safety issues highlighted
    
    Returns:
        str: A concise, actionable text briefing
    """
    try:
        # Get Gemini API key
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            return "Error: GEMINI_API_KEY not configured"
        
        # Get urgent complaints and high-risk jobs
        urgent_complaints = get_today_urgent_complaints()
        high_risk_jobs = get_recent_high_rework_risk_jobs()
        
        # Initialize the CodeAgent
        agent = CodeAgent(
            model="gemini-pro",
            api_key=gemini_api_key,
            temperature=0.7
        )
        
        # Prepare the prompt for the agent
        prompt = f"""Generate a concise daily quality briefing for the NYCHA Superintendent.

URGENT COMPLAINTS:
{urgent_complaints if urgent_complaints else 'No urgent complaints found in the last 24 hours.'}

HIGH-RISK WORK ORDERS:
{high_risk_jobs if high_risk_jobs else 'No high-risk work orders found.'}

Please format the briefing as follows:
1. Start with a greeting
2. List urgent complaints first, with their key details
3. List high-risk work orders next, with their risk factors
4. End with a polite closing

Keep the briefing concise and actionable."""
        
        # Generate the briefing using the agent
        response = agent.generate(prompt)
        
        if not response:
            logger.error("Failed to generate briefing from agent")
            return "Error: Failed to generate briefing"
        
        logger.info("Daily briefing generated successfully")
        return response
        
    except Exception as e:
        error_msg = f"Error generating daily briefing: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"

if __name__ == '__main__':
    # Ensure environment variables are loaded
    load_dotenv()
    
    # Test the briefing generation
    briefing = generate_daily_briefing()
    print("\nDaily Briefing:")
    print("=" * 50)
    print(briefing)
    print("=" * 50) 