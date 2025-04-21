# src/strategy.py
"""
Generate bidding strategy and injection/withdrawal plan for UGS auction.
"""

from typing import Dict, Any
import pandas as pd

def calculate_bid_and_plan(optimization_result: Dict, bid_fraction: float = 0.8, wgv: float = 1_000_000) -> Dict[str, Any]:
    """
    Calculate bid and format injection/withdrawal plan.
    
    Args:
        optimization_result: Result from optimizer (status, profit, plan).
        bid_fraction: Fraction of intrinsic value to bid (e.g., 0.8 for 80%).
        wgv: Working gas volume (MWh).
        
    Returns:
        Dictionary with bid, profit, and plan.
    """
    if optimization_result["status"] != "Optimal":
        raise ValueError("Optimization failed, cannot calculate bid.")
    
    # Intrinsic value (profit excluding fixed fee)
    intrinsic_value = optimization_result["profit"]
    intrinsic_value_per_mwh = intrinsic_value / wgv
    
    # Calculate bid (e.g., 80% of intrinsic value)
    bid_per_mwh = intrinsic_value_per_mwh * bid_fraction
    bid_total = bid_per_mwh * wgv
    
    # Expected profit after fixed fee
    expected_profit = intrinsic_value - bid_total
    expected_profit_per_mwh = expected_profit / wgv
    
    # Get plan
    plan = optimization_result["plan"]
    
    # Summary metrics
    total_injected = plan["inject"].sum()
    total_withdrawn = plan["withdraw"].sum()
    max_storage = plan["storage"].max()
    final_storage = plan["storage"].iloc[-1]
    injection_days = (plan["inject"] > 0).sum()
    withdrawal_days = (plan["withdraw"] > 0).sum()
    hold_days = ((plan["inject"] == 0) & (plan["withdraw"] == 0)).sum()
    
    return {
        "bid_per_mwh": bid_per_mwh,
        "bid_total": bid_total,
        "intrinsic_value": intrinsic_value,
        "intrinsic_value_per_mwh": intrinsic_value_per_mwh,
        "expected_profit": expected_profit,
        "expected_profit_per_mwh": expected_profit_per_mwh,
        "plan": plan,
        "summary": {
            "total_injected": total_injected,
            "total_withdrawn": total_withdrawn,
            "max_storage": max_storage,
            "final_storage": final_storage,
            "injection_days": injection_days,
            "withdrawal_days": withdrawal_days,
            "hold_days": hold_days,
            "capacity_utilization": max_storage / wgv * 100
        }
    }