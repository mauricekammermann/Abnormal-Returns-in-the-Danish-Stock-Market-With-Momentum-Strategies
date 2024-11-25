import pandas as pd
import numpy as np
from pathlib import Path
import sys
import yaml

# Add the project root directory to sys.path
# This should later be part of the configuration file
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.analysis.momentum_strategy_backtest import momentum_strategy
from src.analysis.load_data import load_data
from src.visualization.plotPerformance import plot_cumulative_returns
from src.visualization.plotRobustnessChecks import plotRobustnessChecks
from src.analysis.summarize_performance import summarize_performance, save_summary_to_latex
from src.analysis.robustness_checks import run_robustness_checks

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def main():
    # Define the base path for file locations
    base_path = Path(__file__).resolve().parents[1]

    # Construct file paths dynamically
    refinitiv_data_path = base_path / "data" / "processed" / "refinitiv_data.csv"
    rf_monthly_path = base_path / "data" / "processed" / "risk_free.csv"
    results_path = base_path / "data" / "results"
    spi_path = base_path / "data" / "processed" / "bloomberg_data.csv"
    summary_file_path = results_path / "summary_performance.tex"
    visualization_path = base_path / "reports" / "figures"

    # Debug: Print the constructed file paths
    print(f"Refinitiv Data Path: {refinitiv_data_path}")
    print(f"Risk-Free Monthly Returns Path: {rf_monthly_path}")
    print(f"Results Path: {results_path}")
    
    print(base_path / "config.yaml")
    config = load_config(base_path / "config.yaml")

    strategy_params = config['strategy_parameters']
    
    # Use parameters in the workflow
    lookback_period = strategy_params['lookback_period']
    holding_period = strategy_params['holding_period']
    nLong = strategy_params['nLong']
    nShort = strategy_params['nShort']
    trx_cost = strategy_params['trx_cost']

    # Ensure the results directory exists
    # results_path.mkdir(parents=True, exist_ok=True)

    # Load risk-free monthly returns
    rf_monthly = load_data(rf_monthly_path)
    print("Loaded risk-free monthly returns:")

    # Strategy parameters
    lookback_period = 12  # Number of months to look back
    nLong = 20             # Number of assets to go long
    nShort = 20            # Number of assets to short
    holding_period = 3    # Rebalance every month
    
    price_data_daily = load_data(refinitiv_data_path)
    
    excess_returns, portfolio_weights, turnover_series, portfolio_returns = momentum_strategy(
        price_data_daily=price_data_daily,
        lookback_period=lookback_period,
        nLong=nLong,
        nShort=nShort,
        holding_period=holding_period,
        rf_monthly=rf_monthly,
        trx_cost=0
    )
    
    excess_returns.columns = ['Strategy_Returns']
                  
    # Save results
    excess_returns.to_csv(results_path / "excess_returns.csv", index=True, header=True)
    portfolio_weights.to_csv(results_path / "portfolio_weights.csv", index=True, header=True)
    turnover_series.to_csv(results_path / "turnover_series.csv", index=True, header=True)
    
    plot_cumulative_returns(excess_returns, filename=visualization_path / "cumulative_returns")
    
    # read spi index data
    # Load data 
    spi_price_daily = load_data(spi_path)
    
    # Resample data to monthly frequency and calculate returns
    spi_price_monthly = spi_price_daily.resample('M').last()

    spi_returns_monthly = spi_price_monthly.pct_change()
 
    # Avoid massive outliers
    spi_returns_monthly = np.clip(spi_returns_monthly, -0.5, 0.5)

    spi_XsReturns_monthly = spi_returns_monthly['spx_index'] - rf_monthly['monthly_return']
    
    stats = summarize_performance(excess_returns, rf_monthly, spi_XsReturns_monthly, 12)

    # Save the summary table for LaTeX
    save_summary_to_latex(stats, summary_file_path)
    
    print("Performance summary saved successfully!")
    
    # Robustness checks
    # Run robustness checks
    run_robustness_checks(
        price_data_daily=price_data_daily,
        rf_monthly=rf_monthly,
        spi_XsReturns_monthly=spi_XsReturns_monthly,
        visualization_path=visualization_path,
        strategy_params={
            'lookback_period': lookback_period,
            'holding_period': holding_period,
            'nLong': nLong,
            'nShort': nShort,
            'trx_cost': trx_cost
        }
    )
    
    print("Results saved successfully!")

if __name__ == '__main__':
    main()
