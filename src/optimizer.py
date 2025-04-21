# src/optimizer.py
"""
Linear programming model for UGS auction optimization.
"""

import pulp
import pandas as pd
from typing import Tuple, Dict, List
import numpy as np

def optimize_ugs_plan(forward_curve: pd.DataFrame, 
                     wgv: float = 1_000_000,
                     max_injection_rate: float = 20_000,
                     max_withdrawal_rate: float = 30_000,
                     injection_threshold: float = 0.5,
                     injection_first_half: float = 1.0,
                     injection_second_half: float = 0.7,
                     withdrawal_min_factor: float = 0.4,
                     withdrawal_max_factor: float = 1.0,
                     variable_cost_rate: float = 0.012) -> Dict:
    """
    Optimize injection/withdrawal plan using linear programming.
    
    Args:
        forward_curve: DataFrame with columns ['date', 'price', 'day_index'].
        wgv: Working gas volume (MWh).
        max_injection_rate: Maximum injection rate (MWh/day).
        max_withdrawal_rate: Maximum withdrawal rate (MWh/day).
        injection_threshold: Storage fill percentage for injection curve.
        injection_first_half: Injection rate factor when < threshold.
        injection_second_half: Injection rate factor when >= threshold.
        withdrawal_min_factor: Withdrawal rate factor when empty.
        withdrawal_max_factor: Withdrawal rate factor when full.
        variable_cost_rate: Variable cost as fraction of injected gas cost.
        
    Returns:
        Dictionary with optimization results: profit, plan, and status.
    """
    # Extract data
    prices = forward_curve['price'].values
    T = len(forward_curve)  # Number of days (365)
    
    # Initialize PuLP problem
    prob = pulp.LpProblem("UGS_Optimization", pulp.LpMaximize)
    
    # Variables
    inject = [pulp.LpVariable(f"inject_{t}", lowBound=0) for t in range(T)]
    withdraw = [pulp.LpVariable(f"withdraw_{t}", lowBound=0) for t in range(T)]
    storage = [pulp.LpVariable(f"storage_{t}", lowBound=0, upBound=wgv) for t in range(T)]
    
    # Binary variables for injection curve (storage < 50% or >= 50%)
    is_first_half = [pulp.LpVariable(f"is_first_half_{t}", cat='Binary') for t in range(T)]
    
    # Objective: Maximize profit
    # Profit = Revenue from withdrawals - Cost of injections - Variable costs
    revenue = pulp.lpSum(withdraw[t] * prices[t] for t in range(T))
    cost = pulp.lpSum(inject[t] * prices[t] * (1 + variable_cost_rate) for t in range(T))
    prob += revenue - cost, "Total_Profit"
    
    # Constraints
    # 1. Storage balance
    for t in range(T):
        if t == 0:
            prob += storage[t] == inject[t] - withdraw[t], f"Storage_Balance_0"
        else:
            prob += storage[t] == storage[t-1] + inject[t] - withdraw[t], f"Storage_Balance_{t}"
    
    # 2. Initial and final storage (flexible, but non-negative)
    prob += storage[0] >= 0, "Initial_Storage"
    
    # 3. Injection constraints (based on storage level)
    M = wgv * 2  # Big-M for binary constraints
    for t in range(T):
        # If storage[t-1] < threshold * wgv, is_first_half[t] = 1
        prob += storage[t-1] - injection_threshold * wgv <= M * (1 - is_first_half[t]), f"First_Half_Upper_{t}"
        prob += storage[t-1] - injection_threshold * wgv >= -M * is_first_half[t], f"First_Half_Lower_{t}"
        
        # Injection rate based on is_first_half
        prob += inject[t] <= max_injection_rate * (
            is_first_half[t] * injection_first_half +
            (1 - is_first_half[t]) * injection_second_half
        ), f"Injection_Rate_{t}"
        
        # Ensure injection doesn't exceed available capacity
        prob += inject[t] <= wgv - storage[t-1], f"Injection_Capacity_{t}"
    
    # 4. Withdrawal constraints (linear based on storage level)
    for t in range(T):
        fill_percentage = pulp.LpVariable(f"fill_{t}", lowBound=0, upBound=1)
        prob += fill_percentage * wgv == storage[t-1], f"Fill_Percentage_{t}"  # Fixed: Rewritten division
        prob += withdraw[t] <= max_withdrawal_rate * (
            withdrawal_min_factor +
            (withdrawal_max_factor - withdrawal_min_factor) * fill_percentage
        ), f"Withdrawal_Rate_{t}"
        prob += withdraw[t] <= storage[t-1], f"Withdrawal_Capacity_{t}"
    
    # Solve the problem
    prob.solve(pulp.PULP_CBC_CMD(msg=0))  # Use CBC solver, suppress output
    
    # Check status
    if pulp.LpStatus[prob.status] != 'Optimal':
        return {"status": "Infeasible", "profit": None, "plan": None}
    
    # Extract results
    plan = {
        "day_index": list(range(T)),
        "date": forward_curve['date'].tolist(),
        "price": prices.tolist(),
        "inject": [pulp.value(inject[t]) for t in range(T)],
        "withdraw": [pulp.value(withdraw[t]) for t in range(T)],
        "storage": [pulp.value(storage[t]) for t in range(T)]
    }
    
    profit = pulp.value(prob.objective)
    
    return {
        "status": pulp.LpStatus[prob.status],
        "profit": profit,
        "plan": pd.DataFrame(plan)
    }