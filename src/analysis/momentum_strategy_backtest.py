import pandas as pd
import numpy as np

def momentum_strategy(data_path, lookback_period=12, nLong=5, nShort=5, holding_period=1, rf_monthly=0.0):
    """
    Implements an optimized momentum strategy with portfolio weights and turnover calculation.

    Parameters:
    - data_path: str, path to the CSV file containing the data.
    - lookback_period: int, number of months to look back for momentum calculation.
    - nLong: int, number of assets to go long.
    - nShort: int, number of assets to short.
    - holding_period: int, number of months to hold the positions before rebalancing.
    - rf_monthly: float, monthly risk-free rate.

    Returns:
    - excess_returns: pd.Series, strategy's returns after accounting for the risk-free rate.
    - portfolio_weights: pd.DataFrame, weights allocated to each asset over time.
    - turnover_series: pd.Series, turnover for each month.
    """
    # Load data
    data = pd.read_csv(data_path, low_memory=False)
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
    data.sort_index(inplace=True)
    
    # Convert all columns to numeric, coerce errors to NaN
    data = data.apply(pd.to_numeric, errors='coerce')

    # Drop columns with all NaN values
    data.dropna(axis=1, how='all', inplace=True)

    # Resample data to monthly frequency and calculate returns
    monthly_prices = data.resample('M').last()
    monthly_returns = monthly_prices.pct_change()

    # Calculate cumulative returns over the lookback period
    cum_returns = (1 + monthly_returns).rolling(window=lookback_period).apply(np.prod, raw=True) - 1

    # Define rebalancing dates (every holding_period months)
    rebalancing_dates = monthly_returns.index[lookback_period::holding_period]

    # Initialize portfolio weights and returns
    portfolio_weights = pd.DataFrame(0, index=monthly_returns.index, columns=monthly_returns.columns)
    excess_returns = pd.Series(0, index=monthly_returns.index)
    turnover_series = pd.Series(0, index=monthly_returns.index)

    prev_weights = pd.Series(0, index=monthly_returns.columns)

    for date in rebalancing_dates:
        # Get cumulative returns for the lookback period
        lookback_returns = cum_returns.loc[date]
        lookback_returns = lookback_returns.dropna()

        # Rank assets by momentum
        ranked_assets = lookback_returns.sort_values(ascending=False)
        long_assets = ranked_assets.head(nLong).index
        short_assets = ranked_assets.tail(nShort).index

        # Assign equal weights to long and short positions
        weights = pd.Series(0, index=monthly_returns.columns)
        weights[long_assets] = 1 / nLong
        weights[short_assets] = -1 / nShort

        # Calculate turnover
        turnover_series[date] = (weights - prev_weights).abs().sum()

        # Update weights
        portfolio_weights.loc[date] = weights
        prev_weights = weights

    # Forward-fill weights between rebalancing dates
    portfolio_weights = portfolio_weights.ffill()

    # Calculate portfolio returns
    portfolio_returns = (portfolio_weights.shift(1) * monthly_returns).sum(axis=1)

    # Calculate excess returns
    excess_returns = portfolio_returns - rf_monthly

    return excess_returns, portfolio_weights, turnover_series
