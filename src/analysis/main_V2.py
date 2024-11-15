import pandas as pd
import numpy as np
from momentum_strategy_backtest import momentum_strategy

def main():
    # Adjust the path to your CSV file
    refinitiv_data_path = 'H:\\Projekte\\SPI-Momentum\\data\\interim\\refinitiv_data.csv'

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

    # Output the results
    # For now, we can print the first few rows of the results
    print("Excess Returns:")
    print(excess_returns.head())

    print("\nPortfolio Weights:")
    print(portfolio_weights.head())

    print("\nTurnover Series:")
    print(turnover_series.head())

    # Optionally, save results to CSV files
    # excess_returns.to_csv('excess_returns.csv')
    # portfolio_weights.to_csv('portfolio_weights.csv')
    # turnover_series.to_csv('turnover_series.csv')

if __name__ == '__main__':
    main()
