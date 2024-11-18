import pandas as pd
import numpy as np
import seaborn as sns
from pathlib import Path
from momentum_strategy_backtest import momentum_strategy
from load_data import load_data
from plotPerformance import plot_cumulative_returns
from plotRobustnessChecks import plotRobustnessChecks
from summarize_performance import summarize_performance

def main():
    # Define the base path for file locations
    base_path = Path(__file__).resolve().parents[2]

    # Construct file paths dynamically
    refinitiv_data_path = base_path / "data" / "processed" / "refinitiv_data.csv"
    rf_monthly_path = base_path / "data" / "processed" / "risk_free.csv"
    results_path = base_path / "data" / "results"
    returns_path = base_path / "data" / "results"
    spi_path = base_path / "data" / "processed" / "bloomberg_data.csv"

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
    
    plot_cumulative_returns(excess_returns)
    
    # read spi index data
    # Load data 
    spi_price_daily = load_data(spi_path)

    
    # Resample data to monthly frequency and calculate returns
    spi_price_monthly = spi_price_daily.resample('ME').last()


    spi_returns_monthly = spi_price_monthly.pct_change()
 
    
    # Avoid massive outliers
    spi_returns_monthly = np.clip(spi_returns_monthly, -0.5, 0.5)

    spi_XsReturns_monthly = spi_returns_monthly['spx_index'] - rf_monthly['monthly_return']
    

    stats = summarize_performance(excess_returns, rf_monthly, spi_XsReturns_monthly, 12)
    print(stats)
    
    # Plot robustness checks
    # plotRobustnessChecks(
    #     df,
    #     title='Sharpe Ratios over Holding Periods',
    #     x_label='Holding Period',
    #     y_label='Sharpe Ratio',
    #     savefig=True,
    #     filename='sharpe_ratios_robustness.png'
    # )
    

    print("Results saved successfully!")

if __name__ == '__main__':
    main()
