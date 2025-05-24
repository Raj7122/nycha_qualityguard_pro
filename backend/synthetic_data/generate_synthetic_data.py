"""
Synthetic Data Generation Module for NYCHA QualityGuard Pro

This module generates synthetic datasets for assets, contractors, and work orders
to simulate NYCHA maintenance scenarios. The data is designed to be realistic
while maintaining controlled patterns for testing and development purposes.
"""

import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import pandas as pd
import numpy as np
from faker import Faker

# Initialize Faker for generating realistic data
fake = Faker()

# Constants for data generation
ASSET_TYPES = ['Boiler', 'Elevator', 'HVAC Unit', 'Roof Section', 'Plumbing Main Stack']
CONTRACTOR_SPECIALIZATIONS = ['HVAC', 'Plumbing', 'Electrical', 'General Maintenance']
COMPLAINT_TYPES = [
    'No Heat', 'Leak', 'Strange Noise', 'Out of Service',
    'Temperature Issue', 'Pressure Problem', 'Vibration',
    'Water Quality', 'Air Quality', 'Structural Concern'
]
QUICK_FIX_RESOLUTIONS = [
    'Temporary patch applied', 'Reset unit', 'Cleared blockage',
    'Adjusted settings', 'Tightened connections', 'Cleaned filters'
]
THOROUGH_FIX_RESOLUTIONS = [
    'Replaced compressor', 'Full pipe segment replaced',
    'Complete system overhaul', 'Major component replacement',
    'Structural reinforcement applied', 'Full system recalibration'
]

def generate_synthetic_assets(num_assets: int = 50) -> pd.DataFrame:
    """
    Generate synthetic asset data.
    
    Args:
        num_assets: Number of assets to generate
        
    Returns:
        pd.DataFrame: DataFrame containing synthetic asset data
    """
    # Generate building IDs (fewer buildings than assets)
    num_buildings = max(3, num_assets // 10)
    building_ids = [f'BLDG_{chr(65 + i)}' for i in range(num_buildings)]
    
    data = {
        'asset_id': [f'ASSET_{i:03d}' for i in range(1, num_assets + 1)],
        'building_id': random.choices(building_ids, k=num_assets),
        'asset_type': random.choices(ASSET_TYPES, k=num_assets),
        'installation_year': [random.randint(1980, 2020) for _ in range(num_assets)],
        'last_maintenance_date': [
            (datetime.now() - timedelta(days=random.randint(0, 730))).strftime('%Y-%m-%d')
            if random.random() < 0.8 else None
            for _ in range(num_assets)
        ]
    }
    
    return pd.DataFrame(data)

def generate_synthetic_contractors(num_contractors: int = 5) -> pd.DataFrame:
    """
    Generate synthetic contractor data.
    
    Args:
        num_contractors: Number of contractors to generate
        
    Returns:
        pd.DataFrame: DataFrame containing synthetic contractor data
    """
    data = {
        'contractor_id': [f'CONTR_{i:03d}' for i in range(1, num_contractors + 1)],
        'contractor_name': [fake.company() for _ in range(num_contractors)],
        'specialization': random.choices(CONTRACTOR_SPECIALIZATIONS, k=num_contractors),
        'base_rework_propensity': [round(random.uniform(0.05, 0.3), 3) for _ in range(num_contractors)]
    }
    
    return pd.DataFrame(data)

def calculate_rework_probability(
    asset_year: int,
    resolution_text: str,
    contractor_propensity: Optional[float]
) -> float:
    """
    Calculate the probability of rework needed based on various factors.
    
    Args:
        asset_year: Year the asset was installed
        resolution_text: Text describing the resolution
        contractor_propensity: Contractor's base rework propensity
        
    Returns:
        float: Probability of rework needed
    """
    # Base probability (reduced from 0.1 to 0.05)
    prob = 0.05
    
    # Age factor (older assets more likely to need rework)
    # Increased weight of age factor
    age_factor = (2024 - asset_year) / 40  # Normalize by 40 years
    prob += age_factor * 0.4  # Increased from 0.3 to 0.4
    
    # Resolution type factor
    if resolution_text in QUICK_FIX_RESOLUTIONS:
        prob += 0.25  # Increased from 0.2 to 0.25
    elif resolution_text in THOROUGH_FIX_RESOLUTIONS:
        prob -= 0.15  # Added penalty for thorough fixes
    
    # Contractor factor
    if contractor_propensity is not None:
        prob += contractor_propensity * 1.2  # Increased weight of contractor factor
    
    # Add some randomness (reduced from ±0.1 to ±0.05)
    prob += random.uniform(-0.05, 0.05)
    
    return min(max(prob, 0), 1)  # Ensure probability is between 0 and 1

def generate_synthetic_work_orders(
    assets_df: pd.DataFrame,
    contractors_df: pd.DataFrame,
    num_work_orders: int = 500
) -> pd.DataFrame:
    """
    Generate synthetic work order data.
    
    Args:
        assets_df: DataFrame containing asset data
        contractors_df: DataFrame containing contractor data
        num_work_orders: Number of work orders to generate
        
    Returns:
        pd.DataFrame: DataFrame containing synthetic work order data
    """
    # Create a mapping of asset IDs to their installation years
    asset_years = dict(zip(assets_df['asset_id'], assets_df['installation_year']))
    
    # Create a mapping of contractor IDs to their rework propensity
    contractor_propensities = dict(zip(contractors_df['contractor_id'], 
                                     contractors_df['base_rework_propensity']))
    
    work_orders = []
    for i in range(1, num_work_orders + 1):
        # Select random asset and contractor
        asset_id = random.choice(assets_df['asset_id'].tolist())
        contractor_id = random.choice(contractors_df['contractor_id'].tolist()) if random.random() < 0.8 else None
        
        # Generate dates
        created_date = datetime.now() - timedelta(days=random.randint(0, 1095))  # Last 3 years
        closed_date = created_date + timedelta(days=random.randint(1, 30))
        
        # Generate resolution text
        resolution_text = random.choice(QUICK_FIX_RESOLUTIONS + THOROUGH_FIX_RESOLUTIONS)
        
        # Calculate rework probability
        rework_prob = calculate_rework_probability(
            asset_years[asset_id],
            resolution_text,
            contractor_propensities.get(contractor_id)
        )
        
        work_orders.append({
            'wo_id': f'WO_{i:04d}',
            'asset_id': asset_id,
            'created_date': created_date.strftime('%Y-%m-%d'),
            'closed_date': closed_date.strftime('%Y-%m-%d'),
            'complaint_type_simulated': random.choice(COMPLAINT_TYPES),
            'resolution_text_simulated': resolution_text,
            'assigned_contractor_id': contractor_id,
            'actual_rework_needed': random.random() < rework_prob
        })
    
    return pd.DataFrame(work_orders)

def generate_all_data(output_dir: str = 'data/') -> None:
    """
    Generate all synthetic datasets and save them to CSV files.
    
    Args:
        output_dir: Directory to save the generated data files
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate datasets
    assets_df = generate_synthetic_assets()
    contractors_df = generate_synthetic_contractors()
    work_orders_df = generate_synthetic_work_orders(assets_df, contractors_df)
    
    # Save to CSV files
    assets_df.to_csv(os.path.join(output_dir, 'synthetic_assets.csv'), index=False)
    contractors_df.to_csv(os.path.join(output_dir, 'synthetic_contractors.csv'), index=False)
    work_orders_df.to_csv(os.path.join(output_dir, 'synthetic_work_orders.csv'), index=False)
    
    # Log generation results
    print(f"Generated synthetic data:")
    print(f"- {len(assets_df)} assets")
    print(f"- {len(contractors_df)} contractors")
    print(f"- {len(work_orders_df)} work orders")
    print(f"\nFiles saved in: {output_dir}")

if __name__ == '__main__':
    generate_all_data() 