# src/data_loader.py
"""
Load and preprocess forward curve data for the UGS auction.
"""

import pandas as pd
from typing import Tuple

def load_forward_curve(filepath: str) -> Tuple[pd.DataFrame, int]:
    """
    Load forward curve from CSV and validate its format.
    
    Args:
        filepath: Path to the forward curve CSV file.
        
    Returns:
        Tuple of (DataFrame with forward curve, number of days).
        
    Raises:
        ValueError: If CSV is missing required columns or has invalid data.
    """
    # Load CSV
    df = pd.read_csv(filepath)
    
    # Validate columns
    required_columns = ['date', 'price']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"CSV must contain columns: {required_columns}")
    
    # Convert date to datetime and price to float
    try:
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')  # Specify DD/MM/YYYY format
        df['price'] = df['price'].astype(float)
    except Exception as e:
        raise ValueError(f"Error processing CSV: {str(e)}")
    
    # Validate date range (April 1, 2026 to March 31, 2027)
    expected_start = pd.to_datetime('2026-04-01')
    expected_end = pd.to_datetime('2027-03-31')
    if df['date'].min() > expected_start or df['date'].max() < expected_end:
        raise ValueError("CSV dates must cover April 1, 2026 to March 31, 2027")
    
    # Ensure 365 days
    num_days = len(df)
    if num_days != 365:
        raise ValueError(f"Expected 365 days, got {num_days}")
    
    # Add day index (0 to 364)
    df['day_index'] = range(num_days)
    
    return df, num_days