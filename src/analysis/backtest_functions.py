import pandas as pd
import numpy as np

'''
This file includes basic financial helper functions and the function to backtest
Momentum based on the approach of Jegadeesh and Titman (1993)
'''

def getFirstAndLastDayInMonth(dates):
        """
        Find last day of month in a list of dates. Values have to be provided
        in YYYYMMDD format. 
        
        Parameters:
        - dates (numpy array or list): Array of dates in 'YYYYMMDD' integer format.
        
        Returns:
        - firstDayList (numpy array): array with positions of first day dates.
        - lastDayList (numpy array): array with positions of last day dates.
        """
        dates = [int(date) for date in dates]
        numer_dates = len(dates)
        dates_cut = np.round(np.array(dates) / 100)
        isNewDate = np.diff(dates_cut)
        
        lastDayList = np.where(isNewDate)[0]
        
        firstDayList = lastDayList + 1
        lastDayList = np.append(lastDayList, numer_dates - 1)
        firstDayList = np.insert(firstDayList, 0, 0)
        
        return firstDayList, lastDayList

# test if it works
print(getFirstAndLastDayInMonth(['20240101','20240102','20240103','20240201','20240301','20240329']))

def adjust_interest_rates(interest_rates, numeric_date_d):
    """
    Adjusts interest rates for different durations of the months.
    
    Parameters:
    - interest_rates (numpy array): A NxM array where each row represents a date and each column represents an interest rate.
    - numeric_date_d (numpy array or Series): Array of dates in 'YYYYMMDD' integer format.
    
    Returns:
    - rf_d (numpy array): Adjusted interest rates based on day count fractions.
    """
    dates = pd.to_datetime(numeric_date_d.astype(str), format='%Y%m%d')
    day_counts = (dates - pd.Timestamp('1900-01-01')).days
    day_diffs = np.diff(day_counts, prepend=day_counts[0])

    rf_d = interest_rates * (day_diffs[:, None] / 360)
    return rf_d

# test if it works
interest_rates = np.array([0.36, 0.18, 0.18, 0.18, 0.18, 0.18]).reshape(-1, 1)
numeric_date_d = np.array(['20240101', '20240102', '20240103', '20240201', '20240301', '20240401'])
print(adjust_interest_rates(interest_rates, numeric_date_d))


def aggregate_returns(unaggregated_returns, date_list):
    """
    Aggregates daily asset returns to monthly ones
    
    Parameters:
    - unaggregated_returns (DataFrame or array): Array or DataFrame of returns, where rows represent days and columns represent assets.
    - date_list (list): List of dates (daily) corresponding to each row in unaggregated_returns.

    Returns:
    - aggregated_returns (array): Aggregated returns array with rows representing months and columns representing assets.
    """
    # Convert returns to numpy array if it's in DataFrame format
    unaggregated_returns = unaggregated_returns.values if hasattr(unaggregated_returns, 'values') else unaggregated_returns
    
    # Ensure original_returns is a 2D array, even if it's a single asset
    if unaggregated_returns.ndim == 1:
        unaggregated_returns = unaggregated_returns[:, np.newaxis]
        
    first_day_list, last_day_list = getFirstAndLastDayInMonth(date_list)
    
    n_months = len(first_day_list)
    n_assets = unaggregated_returns.shape[1]
    aggregated_returns = np.zeros((n_months, n_assets))
    
    for period_index in range(n_months):
        start_index = first_day_list[period_index]
        end_index = last_day_list[period_index]
        
        for asset_index in range(n_assets):
            returns_subset = unaggregated_returns[start_index:end_index + 1, asset_index]
            aggregated_returns[period_index, asset_index] = np.prod(1 + returns_subset) - 1
    
    return aggregated_returns


def backtest_momentum(returns_monthly, rf_monthly, numericDate_monthly, lookback_period, holding_period, start_month, nLong, nShort):
    """
    Backtests a momentum strategy based on historical monthly returns.
    
    Parameters:
    - returns_monthly (DataFrame): Monthly returns of assets, indexed by date.
    - rf_monthly (Series): Monthly risk-free rate.
    - numericDate_monthly (Series): Numeric dates for each month.
    - lookback_period (int): Lookback period for momentum calculation.
    - holding_period (int): Holding period before rebalancing.
    - start_month (int): Month to start the backtest.
    - nLong (int): Number of assets to buy (long).
    - nShort (int): Number of assets to sell (short).
    
    Returns:
    - excess_returns (Series): Excess returns of the strategy after adjusting for risk-free rate.
    - portfolio_weights (DataFrame): Portfolio weights for each asset over time.
    - turnover_series (Series): Total turnover per month.
    """
    
    # 1) Basic Information
    nMonths, nAssets = returns_monthly.shape
    
    # Prepare DataFrames to store portfolio weights and returns
    portfolio_weights = pd.DataFrame(np.zeros((len(returns_monthly.index), len(returns_monthly.columns))), index=returns_monthly.index, columns=returns_monthly.columns, dtype='float64')
    portfolio_returns = pd.Series(data=0.0, index=returns_monthly.index, dtype='float64')

    # Prepare a DataFrame to store newly allocated weights to track the changes
    new_weights_allocation = pd.DataFrame(np.zeros((len(returns_monthly.index), len(returns_monthly.columns))), index=returns_monthly.index, columns=returns_monthly.columns, dtype='float64')

    # Prepare a Series to store turnover values per month
    turnover_series = pd.Series(data=0.0, index=returns_monthly.index, dtype='float64')

    # Loop over each rebalance period starting from 'start_month'
    for t in range(start_month, nMonths):
        # Define the lookback period
        lookback_start = t - lookback_period
        lookback_end = t

        # 2) Check the conditions for possible assets
        # Condition 1: Asset must have return history for the past 'lookback_period' months
        valid_assets = returns_monthly.iloc[lookback_start:lookback_end].notna().all()

        # Condition 2: Asset must still exist at the time of portfolio formation (month 't')
        valid_assets &= returns_monthly.iloc[t].notna()

        # Filter possible assets based on the conditions
        cumulative_returns = pd.Series(np.nan, index=returns_monthly.columns)
        cumulative_returns[valid_assets] = (returns_monthly[valid_assets].iloc[lookback_start:lookback_end] + 1).prod() - 1

        # 3) Calculate cumulative returns over the lookback period
        cumulative_returns = (returns_monthly[valid_assets].iloc[lookback_start:lookback_end] + 1).prod() - 1

        # Rank assets based on cumulative returns
        ranked_assets = cumulative_returns.sort_values(ascending=False)

        # Select top 'nLong' assets for the long portfolio
        long_assets = ranked_assets.head(nLong).index

        # Select bottom 'nShort' assets for the short portfolio
        short_assets = ranked_assets.tail(nShort).index

        # 4) Calculate new weights and update portfolio weights
        # Reduce weights from assets that are being replaced
        if t >= holding_period:
            previous_new_weights = new_weights_allocation.iloc[t - holding_period]
            portfolio_weights.loc[returns_monthly.index[t]] = portfolio_weights.loc[returns_monthly.index[t - 1]] - previous_new_weights

        # Add new weights for the newly selected assets and track them in new_weights_allocation
        for asset in long_assets:
            new_weights_allocation.at[returns_monthly.index[t], asset] = 1 / (nLong * holding_period)
            portfolio_weights.at[returns_monthly.index[t], asset] += new_weights_allocation.at[returns_monthly.index[t], asset]
        for asset in short_assets:
            new_weights_allocation.at[returns_monthly.index[t], asset] = -1 / (nShort * holding_period)
            portfolio_weights.at[returns_monthly.index[t], asset] += new_weights_allocation.at[returns_monthly.index[t], asset]

        # 5) Calculate turnover
        if t > start_month:
            turnover = (portfolio_weights.iloc[t] - portfolio_weights.iloc[t - 1]).abs().sum()
        else:
            turnover = portfolio_weights.iloc[t].abs().sum()
        turnover_series.iloc[t] = turnover

        # 6) Calculate portfolio returns
        portfolio_returns.iloc[t] = np.dot(returns_monthly.iloc[t].values, portfolio_weights.iloc[t].values)

    # Adjust for the risk-free rate
    excess_returns = portfolio_returns.subtract(rf_monthly, fill_value=0)

    return excess_returns, portfolio_weights, turnover_series

# Example usage (you would need to replace these with actual DataFrames/Series):
# returns_monthly = pd.DataFrame(...)
# rf_monthly = pd.Series(...)
# numericDate_monthly = pd.Series(...)
# result, weights, turnover = backtest_momentum(returns_monthly, rf_monthly, numericDate_monthly, 12, 6, 24, 5, 5)
