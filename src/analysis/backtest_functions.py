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

def backtest_momentum(return_data):
    '''
    Returns the returns (monthly) of a momentum strategy with predefined parameters

    Parameters
    ----------
    return_data : pd.DataFrame
        A DataFrame of monthly returns with rows representing months and columns representing assets.
        Each entry should be the monthly return of a given asset.

    Returns
    -------
    portfolio_returns : pd.Series
        A Series representing the monthly returns of the momentum strategy. Each entry corresponds to
        the strategy's return for that month.

    '''
    # basic parameters
    lookback_period = 9
    holding_period = 6 

    num_months = len(return_data)
    num_assets = len(return_data.columns)
    signals = pd.DataFrame(np.zeros((num_months, num_assets)), index=return_data.index, columns=return_data.columns)
    portfolio_returns = pd.Series(np.zeros(num_months), index=return_data.index)

    # signals past performance
    for t in range(lookback_period, num_months):
        # Calculate past 9m returns
        past_returns = return_data.iloc[t - lookback_period:t].sum()

        # Get top and bottom performing stocks
        best_stocks = past_returns.nlargest(3).index
        worst_stocks = past_returns.nsmallest(3).index

        signals.loc[return_data.index[t], best_stocks] = 1 / 3
        signals.loc[return_data.index[t], worst_stocks] = -1 / 3  

    # pf returns
    for t in range(num_months):
        if t >= holding_period:
            portfolio_returns.iloc[t] = (signals.iloc[t - holding_period] * return_data.iloc[t]).sum()

    return portfolio_returns
