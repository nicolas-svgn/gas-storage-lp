# src/visualization.py
"""
Visualize UGS auction optimization results.
"""

import matplotlib.pyplot as plt
import os
from typing import Dict, Any

def plot_results(result: Dict[str, Any], save_dir: str = "results") -> None:
    """
    Plot forward curve, injection/withdrawal, and storage levels.
    
    Args:
        result: Result from strategy (bid, plan, summary).
        save_dir: Directory to save plots.
    """
    plan = result["plan"]
    os.makedirs(save_dir, exist_ok=True)
    
    fig, axs = plt.subplots(3, 1, figsize=(12, 15), sharex=True)
    
    # Plot forward curve
    days = plan["day_index"]
    prices = plan["price"]
    axs[0].plot(days, prices, color='blue', label='Forward Curve')
    axs[0].set_ylabel('Price (€/MWh)')
    axs[0].set_title('Forward Curve')
    axs[0].legend()
    axs[0].grid(True)
    
    # Plot actions (injection/withdrawal)
    injections = plan["inject"]
    withdrawals = plan["withdraw"]
    axs[1].bar(days, injections, color='green', label='Injection')
    axs[1].bar(days, -withdrawals, color='red', label='Withdrawal')
    axs[1].set_ylabel('Volume (MWh)')
    axs[1].set_title('Daily Injection/Withdrawal')
    axs[1].legend()
    axs[1].grid(True)
    
    # Plot storage level
    storage = plan["storage"]
    axs[2].plot(days, storage, color='purple', label='Storage Level')
    axs[2].set_xlabel('Day')
    axs[2].set_ylabel('Storage Level (MWh)')
    axs[2].set_title('Storage Level Evolution')
    axs[2].axhline(y=1_000_000, color='red', linestyle='--', label='Max Capacity')
    axs[2].legend()
    axs[2].grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "ugs_plan.png"))
    plt.close()