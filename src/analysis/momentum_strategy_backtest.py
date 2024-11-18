import pandas as pd
import numpy as np
from load_data import load_data

def momentum_strategy(price_data_daily, lookback_period, nLong, nShort, holding_period, rf_monthly, trx_cost):
    """
    Implements a momentum strategy with a rolling rebalancing approach.

    Parameters:
    - data_path: str, path to the CSV file containing the data.
    - lookback_period: int, number of months to look back for momentum calculation.
    - nLong: int, number of assets to go long.
    - nShort: int, number of assets to short.
    - holding_period: int, number of months to hold the positions before they roll off.
    - rf_monthly: pd.Series, monthly risk-free rate (indexed by date).

    Returns:
    - excess_returns: pd.Series, strategy's returns after accounting for the risk-free rate.
    - portfolio_weights: pd.DataFrame, weights allocated to each asset over time.
    - turnover_series: pd.Series, turnover for each month.
    """

    # Load data 
    data = price_data_daily
    
    # Resample data to monthly frequency and calculate returns
    monthly_prices = data.resample('M').last()
    monthly_returns = monthly_prices.pct_change()
    # Avoid massive outliers
    monthly_returns = np.clip(monthly_returns, -0.5, 0.5)

    # Calculate cumulative returns over the lookback period
    cum_returns = (1 + monthly_returns).rolling(window=lookback_period).apply(np.prod, raw=True) - 1
    
    # Avoid massive outliers
    cum_returns = np.clip(cum_returns, -0.5, 0.5)
    

    # Initialize portfolio weights and returns
    portfolio_weights = pd.DataFrame(0.0, index=monthly_returns.index, columns=monthly_returns.columns)
    excess_returns = pd.Series(0.0, index=monthly_returns.index)
    turnover_series = pd.Series(0.0, index=monthly_returns.index)
    new_weights_allocation = pd.DataFrame(0.0, index=monthly_returns.index, columns=monthly_returns.columns)

    nMonths = len(monthly_returns)
    start_month = lookback_period

    for t in range(start_month, nMonths):
        date = monthly_returns.index[t]
        # Define the lookback period
        lookback_start = t - lookback_period
        lookback_end = t

        # Select assets with full data in the lookback period
        valid_assets = monthly_returns.iloc[lookback_start:lookback_end].notna().all()
        valid_assets &= monthly_returns.iloc[t].notna()
        valid_assets = valid_assets[valid_assets].index

        # Skip if no valid assets
        if len(valid_assets) == 0:
            portfolio_weights.loc[date] = portfolio_weights.loc[monthly_returns.index[t - 1]]
            turnover_series[date] = 0.0
            continue

        # Calculate cumulative returns over the lookback period
        lookback_returns = (1 + monthly_returns.loc[monthly_returns.index[lookback_start:lookback_end], valid_assets]).prod() - 1

        # Rank assets by momentum
        ranked_assets = lookback_returns.sort_values(ascending=False)
        long_assets = ranked_assets.head(nLong).index
        if nShort != 0:
            short_assets = ranked_assets.tail(nShort).index

        # Reduce weights from assets that are being replaced (after holding_period)
        if t >= holding_period:
            prev_date = monthly_returns.index[t - holding_period]
            weights_to_remove = new_weights_allocation.loc[prev_date]
            portfolio_weights.loc[date] = portfolio_weights.loc[monthly_returns.index[t - 1]] - weights_to_remove
        else:
            portfolio_weights.loc[date] = portfolio_weights.loc[monthly_returns.index[t - 1]]

        # Assign new weights to long and short positions
        new_weights = pd.Series(0.0, index=monthly_returns.columns)
        new_weights.loc[long_assets] = 1 / (nLong * holding_period)
        if nShort != 0:
            new_weights.loc[short_assets] = -1 / (nShort * holding_period)
            
        new_weights_allocation.loc[date] = new_weights

        # Update portfolio weights
        portfolio_weights.loc[date] += new_weights

        # Handle very small weights by rounding
        portfolio_weights.loc[date] = portfolio_weights.loc[date].round(10)

        # Set very small weights to zero
        small_weight_threshold = 1e-8
        mask = portfolio_weights.loc[date].abs() < small_weight_threshold
        portfolio_weights.loc[date, mask] = 0.0

        # Calculate turnover
        if t > start_month:
            turnover_series[date] = (portfolio_weights.loc[date] - portfolio_weights.loc[monthly_returns.index[t - 1]]).abs().sum()
        else:
            turnover_series[date] = portfolio_weights.loc[date].abs().sum()

    # Calculate portfolio returns
    portfolio_returns = (portfolio_weights.shift(1) * monthly_returns).sum(axis=1)

    # Align rf_monthly with portfolio_returns index
    rf_monthly_aligned = rf_monthly.reindex(portfolio_returns.index).fillna(0.0)

    # Ensure rf_monthly_aligned is a Series
    if isinstance(rf_monthly_aligned, pd.DataFrame):
        rf_monthly_aligned = rf_monthly_aligned.iloc[:, 0]
    
    # Rename
    rf_monthly_aligned.columns = ['rf']
    portfolio_returns.columns = ['Portfolio_Returns']

    # Calculate excess returns
    if nShort == 0:
        excess_returns = portfolio_returns['Portfolio_Returns'] - rf_monthly_aligned['rf']
        
    else:
        excess_returns = portfolio_returns
        
    if isinstance(excess_returns, pd.Series):
        excess_returns = excess_returns.to_frame()
    if isinstance(portfolio_weights, pd.Series):
        portfolio_weights = portfolio_weights.to_frame()
    if isinstance(turnover_series, pd.Series):
        turnover_series = turnover_series.to_frame()
    if isinstance(monthly_returns, pd.Series):
        monthly_returns = monthly_returns.to_frame()
    
    excess_returns.columns = ['Strategy_Returns']
    turnover_series.columns = ['Turnover']
    
    # subtract trx cost
    excess_returns = excess_returns['Strategy_Returns'] - turnover_series['Turnover'] * trx_cost
    
        
    return excess_returns, portfolio_weights, turnover_series, portfolio_returns
