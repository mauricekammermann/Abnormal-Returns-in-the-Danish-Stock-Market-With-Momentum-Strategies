import pandas as pd
import numpy as np

def momentum_strategy(refinitiv_data_path, lookback_period=12, nLong=5, nShort=5, holding_period=1, rf_monthly=0.0):
    # Read the data
    data = pd.read_csv(refinitiv_data_path, low_memory=False)

    # Convert 'date' column to datetime
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
    # Sort the index
    data = data.sort_index()
    # Check for duplicate dates and remove them
    data = data[~data.index.duplicated(keep='first')]

    # Convert all columns to numeric, coerce errors to NaN
    data = data.apply(pd.to_numeric, errors='coerce')

    # Handle any specific formatting issues, such as commas as decimal separators
    # If your data uses commas as decimal separators, uncomment the following lines:
    # data = data.replace(',', '.', regex=True)
    # data = data.apply(lambda x: x.str.replace(',', '.').astype(float))

    # Drop columns with all NaN values (if any)
    data.dropna(axis=1, how='all', inplace=True)

    # Calculate monthly returns
    # Resample data to monthly frequency using last available price in the month
    monthly_prices = data.resample('M').last()
    # Calculate monthly returns
    monthly_returns = monthly_prices.pct_change()

    # Initialize variables
    dates = monthly_returns.index
    assets = monthly_returns.columns
    num_months = len(dates)
    portfolio_weights = pd.DataFrame(0, index=dates, columns=assets)
    excess_returns = pd.Series(0, index=dates)
    turnover_series = pd.Series(0, index=dates)

    prev_weights = pd.Series(0, index=assets)

    for t in range(lookback_period, num_months):
        current_date = dates[t]
        lookback_start = dates[t - lookback_period]
        lookback_end = dates[t - 1]
        # Get returns in the lookback period
        lookback_returns = monthly_returns.loc[lookback_start:lookback_end]
        # Filter assets with sufficient data
        sufficient_data = lookback_returns.notnull().all()
        # Also, check if the current month's return is not NaN
        current_month_returns = monthly_returns.loc[current_date]
        sufficient_data &= current_month_returns.notnull()

        eligible_assets = assets[sufficient_data]

        # Skip iteration if there are not enough eligible assets
        if len(eligible_assets) < max(nLong, nShort):
            continue

        # Calculate cumulative returns over the lookback period
        cum_returns = (1 + lookback_returns[eligible_assets]).prod() - 1
        # Rank assets
        ranked_assets = cum_returns.sort_values(ascending=False)
        long_assets = ranked_assets.head(nLong).index
        short_assets = ranked_assets.tail(nShort).index

        # Update portfolio weights
        # We adjust weights every 'holding_period' months
        if (t - lookback_period) % holding_period == 0:
            # Remove weights for assets that are being replaced
            weights_to_remove = prev_weights.copy()
            weights_to_remove[:] = 0
            # For assets in previous long positions
            prev_long_assets = prev_weights[prev_weights > 0].index
            weights_to_remove[prev_long_assets] = -1 / (nLong)
            # For assets in previous short positions
            prev_short_assets = prev_weights[prev_weights < 0].index
            weights_to_remove[prev_short_assets] = 1 / (nShort)
            # Apply weights_to_remove to prev_weights
            prev_weights += weights_to_remove

            # Add new weights
            weights_to_add = pd.Series(0, index=assets)
            weights_to_add[long_assets] = 1 / nLong
            weights_to_add[short_assets] = -1 / nShort
            # Apply weights_to_add to prev_weights
            prev_weights += weights_to_add

        # Record current weights
        portfolio_weights.loc[current_date] = prev_weights

        # Calculate turnover
        if t > lookback_period:
            turnover = (portfolio_weights.loc[current_date] - portfolio_weights.loc[dates[t-1]]).abs().sum()
            turnover_series[current_date] = turnover

        # Calculate portfolio return
        port_return = (prev_weights * current_month_returns).sum()
        # Calculate excess return
        excess_returns[current_date] = port_return - rf_monthly

    # Trim initial periods with NaN returns
    excess_returns = excess_returns.iloc[lookback_period:]
    portfolio_weights = portfolio_weights.iloc[lookback_period:]
    turnover_series = turnover_series.iloc[lookback_period:]

    return excess_returns, portfolio_weights, turnover_series

# Example usage:
# Adjust the path to your CSV file
refinitiv_data_path = 'H:\\Projekte\\SPI-Momentum\\data\\interim\\refinitiv_data.csv'
excess_returns, portfolio_weights, turnover_series = momentum_strategy(refinitiv_data_path)



# Parameters
lookback_period = 12  # Look back over the past 12 months
nLong = 5             # Number of assets to go long
nShort = 5            # Number of assets to go short
holding_period = 1    # Rebalance every month
rf_monthly = 0.0      # Risk-free rate per month

# Run the strategy
excess_returns, portfolio_weights, turnover_series = momentum_strategy(
    refinitiv_data_path,
    lookback_period=lookback_period,
    nLong=nLong,
    nShort=nShort,
    holding_period=holding_period,
    rf_monthly=rf_monthly
)

# Display results
print("Excess Returns:")
print(excess_returns)
print("\nPortfolio Weights:")
print(portfolio_weights)
print("\nTurnover Series:")
print(turnover_series)


