import pandas as pd

def process_risk_free_yield(input_path):
    """
    Processes SNB daily yield data into approximate monthly risk-free returns.

    Parameters:
    - input_path: str or Path, path to the SNB yield data CSV.

    Returns:
    - DataFrame containing processed monthly risk-free returns with columns ['date', 'monthly_return'].
    """
    # Load SNB yield data
    snb_data = pd.read_csv(input_path, parse_dates=['date'])
    snb_data.set_index('date', inplace=True)

    # Ensure numeric values for yields
    snb_data['value'] = pd.to_numeric(snb_data['value'], errors='coerce')

    # Drop NaN values
    snb_data.dropna(inplace=True)

    # Convert daily yields to daily returns
    snb_data['daily_return'] = (1 + snb_data['value'] / 100) ** (1 / 252) - 1

    # Resample to monthly returns (product of daily returns)
    rf_monthly = snb_data['daily_return'].resample('M').apply(lambda x: (1 + x).prod() - 1)

    # Convert to a DataFrame for usability
    rf_monthly_df = rf_monthly.reset_index()
    rf_monthly_df.columns = ['date', 'monthly_return']

    return rf_monthly_df
