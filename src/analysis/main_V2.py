import pandas as pd
from pathlib import Path
from momentum_strategy_backtest import momentum_strategy
from load_data import load_data  

def main():
    # Define the base path for file locations
    base_path = Path(__file__).resolve().parents[2]

    # Construct file paths dynamically
    refinitiv_data_path = base_path / "data" / "processed" / "refinitiv_data.csv"
    rf_monthly_path = base_path / "data" / "processed" / "risk_free.csv"
    results_path = base_path / "data" / "results"

    # Debug: Print the constructed file paths
    print(f"Refinitiv Data Path: {refinitiv_data_path}")
    print(f"Risk-Free Monthly Returns Path: {rf_monthly_path}")
    print(f"Results Path: {results_path}")

    # Ensure the results directory exists
    # results_path.mkdir(parents=True, exist_ok=True)

    # Load risk-free monthly returns
    rf_monthly = load_data(rf_monthly_path)
    print("Loaded risk-free monthly returns:")

    # Strategy parameters
    lookback_period = 12  # Number of months to look back
    nLong = 5             # Number of assets to go long
    nShort = 5            # Number of assets to short
    holding_period = 3    # Rebalance every month

    excess_returns, portfolio_weights, turnover_series = momentum_strategy(
        data_path=refinitiv_data_path,
        lookback_period=lookback_period,
        nLong=nLong,
        nShort=nShort,
        holding_period=holding_period,
        rf_monthly=rf_monthly
    )

    # Save results
    excess_returns.to_csv(results_path / "excess_returns.csv", index=True, header=True)
    portfolio_weights.to_csv(results_path / "portfolio_weights.csv", index=True, header=True)
    turnover_series.to_csv(results_path / "turnover_series.csv", index=True, header=True)

    print("Results saved successfully!")

if __name__ == '__main__':
    main()
