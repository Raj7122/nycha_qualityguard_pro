"""
Rework Predictor Service for NYCHA QualityGuard Pro

This service predicts the rework risk for synthetic work orders using rule-based logic.
It loads and merges synthetic asset, contractor, and work order data, enriches the work orders,
and applies a set of rules to estimate rework risk and contributing factors.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from pandas.errors import EmptyDataError

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_synthetic_data(data_dir: str = 'data/') -> Optional[pd.DataFrame]:
    """
    Load and merge synthetic assets, contractors, and work orders data.
    Adds asset age and contractor rework propensity to each work order.
    Returns merged DataFrame or None if loading fails.
    """
    try:
        assets_path = os.path.join(data_dir, 'synthetic_assets.csv')
        contractors_path = os.path.join(data_dir, 'synthetic_contractors.csv')
        work_orders_path = os.path.join(data_dir, 'synthetic_work_orders.csv')

        assets_df = pd.read_csv(assets_path)
        contractors_df = pd.read_csv(contractors_path)
        work_orders_df = pd.read_csv(work_orders_path)

        # Calculate asset age at time of work order
        work_orders_df = work_orders_df.merge(
            assets_df[['asset_id', 'installation_year', 'asset_type']],
            on='asset_id', how='left'
        )
        work_orders_df['created_year'] = pd.to_datetime(work_orders_df['created_date']).dt.year
        work_orders_df['asset_age_at_wo'] = work_orders_df['created_year'] - work_orders_df['installation_year']

        # Add contractor rework propensity
        work_orders_df = work_orders_df.merge(
            contractors_df[['contractor_id', 'base_rework_propensity']],
            left_on='assigned_contractor_id', right_on='contractor_id', how='left'
        )
        work_orders_df.rename(columns={'base_rework_propensity': 'contractor_rework_propensity'}, inplace=True)
        work_orders_df.drop(columns=['contractor_id'], inplace=True)

        return work_orders_df
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except EmptyDataError as e:
        logger.error(f"Empty data file: {e}")
    except Exception as e:
        logger.error(f"Error loading synthetic data: {e}")
    return None

def predict_rework_risk_for_work_orders(data_dir: str = 'data/') -> pd.DataFrame:
    """
    Predict rework risk for each synthetic work order using rule-based logic.
    Adds 'predicted_rework_risk_score' (0-1) and 'predicted_risk_factors' (list of strings).
    Returns the enriched DataFrame.
    """
    df = load_synthetic_data(data_dir)
    if df is None:
        logger.error("Failed to load or merge synthetic data. Returning empty DataFrame.")
        return pd.DataFrame()

    def assess_risk_revised(row) -> pd.Series:
        # Changed return type hint for clarity
        score = 0.05  # small base risk
        risk_factors = []

        # Asset age
        asset_age = row.get('asset_age_at_wo', 0)
        if asset_age > 15:
            score += 0.4
            risk_factors.append('Old Asset (Age: ' + str(asset_age) + ')')  # More informative
        elif asset_age > 8:
            score += 0.2
            risk_factors.append('Moderately Old Asset (Age: ' + str(asset_age) + ')')

        # Resolution Text Analysis
        resolution = str(row.get('resolution_text_simulated', '')).lower()
        if 'patch' in resolution or 'temporary' in resolution:
            score += 0.3
            risk_factors.append('Quick Fix Indicated')
        elif 'replaced' in resolution or 'overhaul' in resolution or 'new unit installed' in resolution:  # Add more "good fix" keywords
            score -= 0.25  # <--- SIGNIFICANTLY REDUCE RISK for thorough fixes
            risk_factors.append('Thorough Fix Performed')  # This is a positive factor

        # Contractor
        contractor_prop = row.get('contractor_rework_propensity')
        if pd.notnull(contractor_prop):  # Check if contractor_prop is not NaN
            if contractor_prop > 0.2:
                score += 0.25
                risk_factors.append(f'High Propensity Contractor (Prop: {contractor_prop:.2f})')  # More informative
            elif contractor_prop > 0.12:
                score += 0.1
                risk_factors.append(f'Moderate Propensity Contractor (Prop: {contractor_prop:.2f})')

        # Cap score
        score = min(max(score, 0.0), 1.0)  # Ensure score is not less than 0

        return pd.Series({'predicted_rework_risk_score': score,
                          'predicted_risk_factors': risk_factors if risk_factors else ['Low Base Risk']})  # Default if no specific factors

    risk_results = df.apply(assess_risk_revised, axis=1)
    df = pd.concat([df, risk_results], axis=1)

    # Log summary
    high_risk_count = (df['predicted_rework_risk_score'] >= 0.6).sum()
    logger.info(f"Processed {len(df)} work orders. {high_risk_count} flagged as high risk (score >= 0.6).")

    return df 