# main.py

import pandas as pd
import numpy as np
import os
from pathlib import Path
from momentum_strategy_backtest import momentum_strategy
from summarize_performance import summarize_performance

def main():
    # Define the base path for file locations
    base_path = Path(__file__).resolve().parents[2]  

    # Construct file paths dynamically
    refinitiv_data_path = base_path / "data" / "interim" / "refinitiv_data.csv"
    bloomberg_data_path = base_path / "data" / "interim" / "bloomberg_data.csv"
    results_path = base_path / "data" / "results"

    # Debug: Print the constructed file paths
    print(f"Refinitiv Data Path: {refinitiv_data_path}")
    print(f"Bloomberg Data Path: {bloomberg_data_path}")
    print(f"Results Path: {results_path}")

    # Ensure the results directory exists
    results_path.mkdir(parents=True, exist_ok=True)

    # Strategy parameters
    lookback_period = 12  # Number of months to look back
    nLong = 5             # Number of assets to go long
    nShort = 5            # Number of assets to go short
    holding_period = 1    # Rebalance every month
    rf_monthly = 0.0      # Monthly risk-free rate

    # Run the momentum strategy
    excess_returns, portfolio_weights, turnover_series = momentum_strategy(
        refinitiv_data_path,
        lookback_period=lookback_period,
        nLong=nLong,
        nShort=nShort,
        holding_period=holding_period,
        rf_monthly=rf_monthly
    )

if __name__ == '__main__':
    main()
