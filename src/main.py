# src/main.py

# Import libraries
import pandas as pd
import numpy as np
import seaborn as sns
from pathlib import Path
import sys
import warnings
import os

# Determine the project root (two levels up from the current file)
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))
src_path = project_root / "src"

# Add the `src` directory to `sys.path`
sys.path.append(str(src_path))

# Absolute imports
from src.visualization.plotPerformance import plot_cumulative_returns
from src.visualization.plotRobustnessChecks import plotRobustnessChecks
from src.analysis.summarize_performance import summarize_performance, save_summary_to_latex
from src.analysis.momentum_strategy_backtest import momentum_strategy
from src.visualization.create_summary_table import create_summary_table
from src.analysis.load_data import load_data
from src.analysis.robustness_checks import (
    run_holding_period_check,
    run_lookback_period_check,
    run_number_assets_check,
    run_trx_cost_check
)

def main():
    venv_path = os.getenv('VIRTUAL_ENV')
    print(f"Virtual Environment Path: {venv_path}")
    warnings.simplefilter(action='ignore', category=FutureWarning)
    
    # Define the base path for file locations
    base_path = Path(__file__).resolve().parents[1]
    print(f"Base Path: {base_path}")
    
    # Construct file paths dynamically
    constituents_data_path = base_path / "data" / "processed" / "constituents_data.csv"
    rf_monthly_path = base_path / "data" / "processed" / "risk_free.csv"
    results_path = base_path / "data" / "results"
    spi_path = base_path / "data" / "processed" / "index_data.csv"
    summary_file_path_longOnly = results_path / "summary_performance_longOnly.tex"
    summary_file_path_longShort = results_path / "summary_performance_longShort.tex"
    summary_file_path_bm = results_path / "summary_performance_benchmark.tex"
    visualization_path = base_path / "reports" / "figures"
    
    # Debug: Print the constructed file paths
    print(f"Constituent Data Path: {constituents_data_path}")
    print(f"Risk-Free Monthly Returns Path: {rf_monthly_path}")
    print(f"Results Path: {results_path}")
    
    # Ensure the results directory exists
    results_path.mkdir(parents=True, exist_ok=True)
    
    # Load risk-free monthly returns
    rf_monthly = load_data(rf_monthly_path)
    
    # Strategy parameters
    lookback_period = 6  # Number of months to look back
    nLong = 20           # Number of assets to go long
    nShort = 20          # Number of assets to short
    holding_period = 6   # Rebalance every month
    
    price_data_daily = load_data(constituents_data_path)
    
    # Read SPI index data
    spi_price_daily = load_data(spi_path)
    
    # Resample data to monthly frequency and calculate returns
    spi_price_monthly = spi_price_daily.resample('ME').last()
    
    # Calculate Returns
    spi_returns_monthly = spi_price_monthly.pct_change()
    if isinstance(spi_returns_monthly, pd.Series):
        spi_returns_monthly = spi_returns_monthly.to_frame()
     
    # Avoid massive outliers
    spi_returns_monthly = np.clip(spi_returns_monthly, -0.5, 0.5)
    spi_XsReturns_monthly = spi_returns_monthly['SWISS PERFORMANCE INDEX - TOT RETURN IND'] - rf_monthly['monthly_return']
    if isinstance(spi_XsReturns_monthly, pd.Series):
        spi_XsReturns_monthly = spi_XsReturns_monthly.to_frame()
    
    # Rename Columns for consistency
    spi_XsReturns_monthly.columns = ['Benchmark']
    spi_returns_monthly.columns = ['Benchmark']
    
    # ----- Run Backtest LONGONLY -----
    excess_returns_longOnly, portfolio_weights_longOnly, turnover_series_longOnly, portfolio_returns_longOnly = momentum_strategy(
        price_data_daily=price_data_daily,
        lookback_period=lookback_period,
        nLong=nLong,
        nShort=0,
        holding_period=holding_period,
        rf_monthly=rf_monthly,
        trx_cost=0
    )
    
    excess_returns_longOnly.columns = ['Xs Returns LongOnly']
    portfolio_returns_longOnly.columns = ['Returns LongOnly']
    
    # Save results
    excess_returns_longOnly.to_csv(results_path / "excess_returns_longOnly.csv", index=True, header=True)
    portfolio_weights_longOnly.to_csv(results_path / "portfolio_weights_longOnly.csv", index=True, header=True)
    turnover_series_longOnly.to_csv(results_path / "turnover_series_longOnly.csv", index=True, header=True)
    stats_longOnly = summarize_performance(excess_returns_longOnly, rf_monthly, spi_XsReturns_monthly, 12, isBenchmark=False)
    save_summary_to_latex(stats_longOnly, summary_file_path_longOnly)
    
    # ----- Run Backtest LONG / SHORT -----
    excess_returns_longShort, portfolio_weights_longShort, turnover_series_longShort, portfolio_returns_longShort = momentum_strategy(
        price_data_daily=price_data_daily,
        lookback_period=lookback_period,
        nLong=nLong,
        nShort=nShort,
        holding_period=holding_period,
        rf_monthly=rf_monthly,
        trx_cost=0
    )
    excess_returns_longShort.columns = ['Xs Returns LongShort']
    portfolio_returns_longShort.columns = ['Returns LongShort']
    
    # Save results
    excess_returns_longShort.to_csv(results_path / "excess_returns_longShort.csv", index=True, header=True)
    portfolio_weights_longShort.to_csv(results_path / "portfolio_weights_longShort.csv", index=True, header=True)
    turnover_series_longShort.to_csv(results_path / "turnover_series_longShort.csv", index=True, header=True)
    stats_longShort = summarize_performance(excess_returns_longShort, rf_monthly, spi_XsReturns_monthly, 12, isBenchmark=False)
    save_summary_to_latex(stats_longShort, summary_file_path_longShort)
    
    # -----
    
    ### Put together and print stats
    # stats for benchmark itself
    stats_bm = summarize_performance(spi_XsReturns_monthly, rf_monthly, spi_XsReturns_monthly, 12, isBenchmark=True)

    # Create Summary Table
    summaryTable = create_summary_table([stats_longOnly, stats_longShort, stats_bm], ['Long Only', 'Long Short', "Benchmark"])
    print(summaryTable)
    
    # Custom labels
    labels = {
        'Strategy_Returns': 'Long Only Strategy',
        'Benchmark': 'SPI',
        'Portfolio_Returns': 'Long Only Strategy',
        'xs_Return': 'Long Only Strategy',
        'trx_cost_0.001': 'Long Only with Trx Cost: 0.1%',
        'trx_cost_0.005': 'Long Only with Trx Cost: 0.5%',
        'trx_cost_0.01': 'Long Only with Trx Cost: 1.0%',
    }
    
    # Create plot and save it
    combined_returns = pd.concat([portfolio_returns_longOnly, portfolio_returns_longShort], axis=1)
    plot_cumulative_returns(combined_returns, spi_returns_monthly, labels, filename=visualization_path / "cumulative_returns")
    
    print("Performance summary saved successfully!")
    
    # ----- Run Robustness Checks -----
    # Define ranges for robustness checks
    lookback_period_range = range(1, 13)
    nLong_range = range(5, 51)
    
    # Run Holding Period Robustness Check
    run_holding_period_check(
        price_data_daily=price_data_daily,
        lookback_period=lookback_period,
        nLong=nLong,
        rf_monthly=rf_monthly,
        spi_XsReturns_monthly=spi_XsReturns_monthly,
        visualization_path=visualization_path
    )
    
    # Run Lookback Period Robustness Check
    run_lookback_period_check(
        price_data_daily=price_data_daily,
        lookback_period_range=lookback_period_range,
        nLong=nLong,
        nShort=0,
        holding_period=holding_period,
        rf_monthly=rf_monthly,
        spi_XsReturns_monthly=spi_XsReturns_monthly,
        visualization_path=visualization_path
    )
    
    # Run Number of Assets Robustness Check
    run_number_assets_check(
        price_data_daily=price_data_daily,
        lookback_period=lookback_period,
        nLong_range=nLong_range,
        nShort=0,
        holding_period=holding_period,
        rf_monthly=rf_monthly,
        spi_XsReturns_monthly=spi_XsReturns_monthly,
        visualization_path=visualization_path
    )
    
    # Run Transaction Cost Robustness Check
    run_trx_cost_check(
        price_data_daily=price_data_daily,
        lookback_period=lookback_period,
        nLong=nLong,
        nShort=0,
        holding_period=holding_period,
        rf_monthly=rf_monthly,
        spi_returns_monthly=spi_returns_monthly,
        visualization_path=visualization_path
    )
    
    print("All robustness checks completed successfully!")

if __name__ == '__main__':
    main()
