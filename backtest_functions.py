import pandas as pd
import numpy as np

def backtest_momentum(return_data):
    # basic parameters
    lookback_period = 9
    holding_period = 6 

    num_months = len(return_data)
    num_assets = len(return_data.columns)
    signals = pd.DataFrame(np.zeros((num_months, num_assets)), index=return_data.index, columns=return_data.columns)
    portfolio_returns = pd.Series(np.zeros(num_months), index=return_data.index)

    # signals past performance
    for t in range(formation_period, num_months):
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
