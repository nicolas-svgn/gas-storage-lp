# Gas Storage Optimization Project

## Overview

This project provides a robust solution for optimizing natural gas storage operations to maximize profit in underground gas storage (UGS) auctions. It implements a linear programming model that determines the optimal injection and withdrawal strategy based on forward curve prices and storage facility constraints.

The optimization considers:
- Daily market prices from a forward curve
- Storage capacity constraints
- Variable injection and withdrawal rates based on storage fill levels
- Operational costs

## Theoretical Background

### Gas Storage Economics

Underground Gas Storage (UGS) facilities play a crucial role in the natural gas market by providing flexibility to balance supply and demand. They allow operators to:
1. **Buy low, sell high**: Inject gas when prices are low and withdraw when prices are high
2. **Manage seasonal price spreads**: Take advantage of seasonal price differentials
3. **Provide supply flexibility**: Support system balancing and security of supply

### Optimization Model: Linear Programming

The core of this project is a linear programming (LP) model that maximizes the intrinsic value of the storage asset. The intrinsic value represents the profit potential from a static, deterministic strategy based on current forward prices.

#### Key Components of the LP Model:

1. **Decision Variables**:
   - Daily injection volumes
   - Daily withdrawal volumes 
   - Storage inventory levels
   - Binary variables for injection regime switching

2. **Objective Function**:
   - Maximize: Revenue from gas sales - Cost of gas purchases - Variable operational costs

3. **Constraints**:
   - Storage balance equations (continuity constraints)
   - Maximum and minimum storage levels
   - Injection rate limitations (dependent on storage fill level)
   - Withdrawal rate limitations (linear dependency on storage fill level)
   - Non-negativity constraints

#### Injection/Withdrawal Curves Modeling

The model incorporates realistic operational constraints:

- **Injection Curve**: Two-regime model where injection capacity decreases when storage is more than 50% full
  - Below 50%: 100% of maximum rate available
  - Above 50%: 70% of maximum rate available

- **Withdrawal Curve**: Linear model where withdrawal capacity increases with storage level
  - At 0% fill: 40% of maximum rate available
  - At 100% fill: 100% of maximum rate available
  - Linear interpolation between these points

### Bidding Strategy

The bidding strategy is based on the intrinsic value of the storage asset. Since UGS auctions are typically competitive, a strategic approach is used:

1. Calculate the total intrinsic value through optimization
2. Determine a bid fraction (e.g., 80% of intrinsic value)
3. Bid this amount to maintain a profit margin while remaining competitive

This approach balances the probability of winning the auction with ensuring profitability.

## Project Architecture

```
gas-storage-lp/
│
├── src/
│   ├── data_loader.py      # Load and validate forward curve data
│   ├── optimizer.py        # Linear programming optimization model
│   ├── strategy.py         # Generate bidding strategy and operational plan
│   └── visualization.py    # Create visualizations of results
│
├── data/
│   └── UTF-8fwcurve.csv    # Forward curve data
│
├── results/                # Generated output directory
│   └── ugs_plan.png        # Visualization of optimization results
│
├── main.py                 # Main execution script
└── requirements.txt        # Project dependencies
```

### Component Details

#### `data_loader.py`
- Loads forward curve data from CSV
- Validates data format and content
- Converts dates and ensures complete coverage of the storage period
- Indexes days from 0 to 364 for optimization

#### `optimizer.py` 
- Implements the core LP model using PuLP
- Defines decision variables, objective function, and constraints
- Models complex injection/withdrawal curves
- Returns detailed optimization results

#### `strategy.py`
- Calculates optimal bidding values based on optimization results
- Computes key performance metrics
- Formats results for reporting and visualization

#### `visualization.py`
- Creates comprehensive visualizations of the optimized strategy
- Plots forward curve, daily actions, and storage levels
- Generates publication-quality graphics for analysis

#### `main.py`
- Coordinates the overall workflow
- Integrates all components into a complete solution

## Installation Instructions

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gas-storage-lp.git
   cd gas-storage-lp
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage Guide

### Running the Optimization

Execute the main script to run the full optimization:

```bash
python main.py
```

### Configuration

The optimization parameters can be customized in `main.py`:

- `wgv`: Working gas volume in MWh
- `max_injection_rate`: Maximum daily injection rate
- `injection_threshold`: Storage level threshold for injection rate change
- `injection_first_half`: Injection rate factor for first half of storage
- `injection_second_half`: Injection rate factor for second half of storage
- `max_withdrawal_rate`: Maximum daily withdrawal rate
- `withdrawal_min_factor`: Withdrawal rate factor when storage is empty
- `withdrawal_max_factor`: Withdrawal rate factor when storage is full
- `variable_cost_rate`: Variable cost as a percentage of injected gas cost
- `bid_fraction`: Percentage of intrinsic value to bid in the auction

### Output

The program generates:

1. A bidding strategy with:
   - Recommended bid per MWh and total bid
   - Expected profit calculation
   - Intrinsic value analysis

2. Detailed operational plan with daily:
   - Injection volumes
   - Withdrawal volumes
   - Storage inventory levels

3. Visualizations in the `results/` directory

## Example Results

When run with the provided forward curve and default parameters, the optimization produces:

### Visualization Output
![UGS Plan](results/ugs_plan.png)

The visualization includes:
- Top panel: Forward curve prices throughout the storage period
- Middle panel: Daily injection (green) and withdrawal (red) volumes
- Bottom panel: Storage inventory level evolution with maximum capacity shown

### Key Performance Metrics

- **Bidding Strategy**:
  - Intrinsic Value: €X.XX per MWh
  - Recommended Bid: €X.XX per MWh (80% of intrinsic value)
  - Total Bid Amount: €X,XXX,XXX

- **Operational Summary**:
  - Total Gas Injected: X,XXX,XXX MWh
  - Total Gas Withdrawn: X,XXX,XXX MWh
  - Maximum Storage Utilization: XX.X%
  - Injection Days: XX
  - Withdrawal Days: XX
  - Hold Days: XX

## Advanced Usage

### Sensitivity Analysis

You can perform sensitivity analysis by modifying key parameters and observing the impact on profitability:

```python
# Example: Testing different bid fractions
for bid_fraction in [0.7, 0.75, 0.8, 0.85, 0.9]:
    result = calculate_bid_and_plan(optimization_result, bid_fraction=bid_fraction)
    print(f"Bid Fraction: {bid_fraction}, Expected Profit: {result['expected_profit']}")
```

### Using Different Forward Curves

To use an alternative forward curve:

1. Prepare a CSV file with columns 'date' and 'price'
2. Ensure dates cover the full storage period (April 1, 2026 to March 31, 2027)
3. Update the filepath in `main.py`

## Contributing

Contributions to improve the project are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[MIT License](LICENSE)

## Acknowledgments

- PuLP library for linear programming functionality
- Pandas for data handling
- Matplotlib for visualization

## Contact

For questions or support, please contact your-email@example.com
