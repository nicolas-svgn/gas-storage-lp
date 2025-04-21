import os
import pandas as pd
from src.data_loader import load_forward_curve
from src.optimizer import optimize_ugs_plan
from src.strategy import calculate_bid_and_plan
from src.visualization import plot_results

def main():
    print(f"Current working directory: {os.getcwd()}")
    
    print("Loading forward curve...")
    data_path = "data/UTF-8fwcurve.csv"
    forward_curve, _ = load_forward_curve(data_path)
    
    print("Optimizing injection/withdrawal plan...")
    optimization_result = optimize_ugs_plan(forward_curve)
    
    print("Calculating bid and plan...")
    result = calculate_bid_and_plan(optimization_result, bid_fraction=0.8)
    
    # Debug: Print result dictionary (optional, can remove after verification)
    print("Result dictionary:", result)
    
    print("\n=== UGS Auction Results ===")
    print(f"Intrinsic Value: {result['intrinsic_value']:.2f} € ({result['intrinsic_value_per_mwh']:.3f} €/MWh)")
    print(f"Bid: {result['bid_total']:.2f} € ({result['bid_per_mwh']:.3f} €/MWh)")
    print(f"Expected Profit: {result['expected_profit']:.2f} € ({result['expected_profit_per_mwh']:.3f} €/MWh)")
    
    print("\nSummary:")
    summary = result["summary"]
    print(f"  total_injected: {summary['total_injected']:.2f}")
    print(f"  total_withdrawn: {summary['total_withdrawn']:.2f}")
    print(f"  max_storage: {summary['max_storage']:.2f}")
    print(f"  final_storage: {summary['final_storage']:.2f}")
    print(f"  injection_days: {summary['injection_days']:.2f}")
    print(f"  withdrawal_days: {summary['withdrawal_days']:.2f}")
    print(f"  hold_days: {summary['hold_days']:.2f}")
    print(f"  capacity_utilization: {summary['capacity_utilization']:.2f}")
    
    # Save the plan to CSV
    os.makedirs("results", exist_ok=True)
    plan_csv_path = "results/ugs_plan.csv"
    plan = result["plan"]
    plan["gain_loss"] = plan["withdraw"] * plan["price"] - plan["inject"] * plan["price"] * 1.012
    plan["storage_change"] = plan["storage"].diff().fillna(plan["storage"])
    plan.to_csv(plan_csv_path, index=False)
    print(f"Plan saved to {plan_csv_path}")
    
    print("Generating plots...")
    plot_results(result, save_dir="results")
    print("Plots saved to results/ugs_plan.png")

if __name__ == "__main__":
    main()