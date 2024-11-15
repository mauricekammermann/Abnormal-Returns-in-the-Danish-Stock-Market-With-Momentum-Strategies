# main.py

import pandas as pd
import numpy as np
import os
from momentum_strategy_backtest import momentum_strategy
from summarize_performance import summarize_performance

def main():
    # Adjust the paths to your CSV files
    refinitiv_data_path = r'H:\Projekte\SPI-Momentum\data\interim\refinitiv_data.csv'
    bloomberg_data_path = r'H:\Projekte\SPI-Momentum\data\interim\bloomberg_data.csv'
    results_path = r'H:\Projekte\SPI-Momentum\data\results'

    # Ensure the results directory exists
    if not os.path.exists(results_path):
        os.makedirs(results_path)

    # Strategy parameters
    lookback_period = 12  # Look back over the past 12 months
    nLong = 5             # Number of assets to go long
    nShort = 5            # Number of assets to go short
    holding_period = 1    # Rebalance every month
    rf_monthly = 0.0      # Monthly risk-free rate

    # Run the strategy
    excess_returns, portfolio_weights, turnover_series = momentum_strategy(
        refinitiv_data_path,
        lookback_period=lookback_period,
        nLong=nLong,
        nShort=nShort,
        holding_period=holding_period,
        rf_monthly=rf_monthly
    )

    # Read benchmark data
    benchmark_data = pd.read_csv(bloomberg_data_path)
    benchmark_data['date'] = pd.to_datetime(benchmark_data['date'])
    benchmark_data.set_index('date', inplace=True)
    benchmark_data = benchmark_data.sort_index()

    # Assuming the benchmark index price is in a column named 'Benchmark_Index'
    # Adjust 'Benchmark_Index' to the actual column name in your data
    benchmark_prices = benchmark_data['Benchmark_Index'].resample('M').last()
    benchmark_returns = benchmark_prices.pct_change().dropna()

    # Align benchmark returns with excess_returns
    benchmark_returns = benchmark_returns.loc[excess_returns.index]

    # Calculate benchmark excess returns (assuming rf_monthly = 0.0)
    benchmark_excess_returns = benchmark_returns - rf_monthly

    # Risk-free rate Series
    rf = pd.Series(rf_monthly, index=excess_returns.index)

    # Factor returns (benchmark excess returns)
    factor_xs_returns = pd.DataFrame({'Benchmark': benchmark_excess_returns})

    # Annualization factor
    annualization_factor = 12  # Monthly data

    # Summarize performance
    results = summarize_performance(excess_returns, rf, factor_xs_returns, annualization_factor)

    # Output the results
    print("Performance Summary:")
    for key, value in results.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for subkey, subvalue in value.items():
                print(f"  {subkey}: {subvalue}")
        else:
            print(f"{key}: {value}")

    # Save results to the specified directory
    # Save excess_returns, portfolio_weights, turnover_series
    excess_returns.to_csv(os.path.join(results_path, 'excess_returns.csv'))
    portfolio_weights.to_csv(os.path.join(results_path, 'portfolio_weights.csv'))
    turnover_series.to_csv(os.path.join(results_path, 'turnover_series.csv'))

    # Save the performance summary to a CSV file
    # Flatten the results dictionary for saving
    results_flat = {}
    for key, value in results.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                results_flat[f"{key}_{subkey}"] = subvalue
        elif isinstance(value, (list, tuple)):
            for idx, item in enumerate(value, start=1):
                results_flat[f"{key}_Lag{idx}"] = item
        else:
            results_flat[key] = value
    results_df = pd.DataFrame.from_dict(results_flat, orient='index', columns=['Value'])
    results_df.to_csv(os.path.join(results_path, 'performance_summary.csv'))

if __name__ == '__main__':
    main()
