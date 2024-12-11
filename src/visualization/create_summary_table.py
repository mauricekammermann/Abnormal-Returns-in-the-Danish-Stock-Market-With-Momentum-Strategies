import pandas as pd
from prettytable import PrettyTable
import numpy as np

def create_summary_table(dicts, labels):
    """
    Creates a summary table from multiple dictionaries, each containing the same structure of summary statistics.
    
    Parameters:
    - dicts (list): A list of dictionaries containing summary statistics with the same structure.
    - labels (list): A list of labels corresponding to each dictionary to use as column headers in the resulting table.
    
    Returns:
    - pd.DataFrame: A DataFrame containing the summary table.
    """
    # Check that the number of labels matches the number of dictionaries
    if len(dicts) != len(labels):
        raise ValueError("The number of labels must match the number of dictionaries.")
    
    # Define readable metric names
    readable_metrics = {
        'Arithmetic_Avg_Total_Return': 'Arithmetic Avg Total Return', 
        'Arithmetic_Avg_Excess_Return': 'Arithmetic Avg Excess Return',
        'Geometric_Avg_Total_Return': 'Geometric Avg Total Return',
        'Geometric_Avg_Excess_Return': 'Geometric Avg Excess Return',
        'Std_of_Excess_Returns_Annualized': 'Std of Excess Returns (Annualized)',
        'Sharpe_Ratio_Arithmetic': 'Sharpe Ratio (Arithmetic)',
        'Sharpe_Ratio_Geometric': 'Sharpe Ratio (Geometric)',
        'Min_Excess_Return': 'Min Excess Return',
        'Max_Excess_Return': 'Max Excess Return',
        'Skewness_of_Excess_Return': 'Skewness of Excess Return',
        'Kurtosis_of_Excess_Return': 'Kurtosis of Excess Return',
        'Alpha_Arithmetic': 'Alpha (Arithmetic)',
        'Alpha_Geometric': 'Alpha (Geometric)',
        'T_stat_of_Alpha': 'T-stat of Alpha',
        'Beta': 'Beta (Factor Return)',
        'Std_Dev_of_Excess_Returns': 'Std Dev of Excess Returns',
        'Monthly_Excess_Return': 'Monthly Excess Return',
        'T_stat_of_Monthly_Excess_Return': 'T-stat of Monthly Excess Return',
        'Autocorrelations': 'Autocorrelations',
    }
    
    # Create a list to store rows for the final DataFrame
    summary_rows = []
    row_index = []

    # Extract keys for consistent structure (assuming all dictionaries have the same structure)
    keys = dicts[0].keys()

    # Iterate through each key to create a row per metric
    for key in keys:
        # Special handling for 'Autocorrelations'
        if key == 'Autocorrelations':
            for lag in ['Lag 1', 'Lag 2', 'Lag 3']:
                row = []
                for d in dicts:
                    if 'Benchmark_Return' in d['Autocorrelations']:
                        autocorr = d['Autocorrelations']['Benchmark_Return'].get(lag, np.nan)
                    else:
                        autocorr = d['Autocorrelations']['xs_Return'].get(lag, np.nan)
                    
                    if pd.isna(autocorr):
                        row.append('N/A')
                    else:
                        row.append(round(autocorr, 2))
                summary_rows.append(row)
                row_index.append(f'Autocorr {lag}')
        else:
            row = []
            for d in dicts:
                if key == 'Beta':
                    try:
                        if 'Benchmark_Return' in d['Beta'].index:
                            beta_val = d['Beta'].loc['Benchmark_Return', 'Benchmark']
                        else:
                            beta_val = d['Beta'].loc['xs_Return', 'Benchmark']
                        if pd.isna(beta_val):
                            row.append('N/A')
                        else:
                            row.append(round(beta_val, 2))
                    except (KeyError, AttributeError):
                        row.append('N/A')
                else:
                    if 'Benchmark_Return' in d:
                        if isinstance(d[key], dict):
                            metric_val = d[key].get('Benchmark_Return', np.nan)
                        else:
                            metric_val = d[key]
                    else:
                        if isinstance(d[key], dict):
                            metric_val = d[key].get('xs_Return', np.nan)
                        else:
                            metric_val = d[key]
                    
                    if isinstance(metric_val, pd.Series):
                        metric_val = metric_val.iloc[0] if not metric_val.empty else np.nan
                    
                    if pd.isna(metric_val):
                        row.append('N/A')
                    else:
                        row.append(round(metric_val, 2))
            summary_rows.append(row)
            readable_metric = readable_metrics.get(key, key)
            row_index.append(readable_metric)

    summary_df = pd.DataFrame(summary_rows, index=row_index, columns=labels)

    table = PrettyTable()
    table.field_names = ["Metric"] + summary_df.columns.tolist()

    for metric, row in summary_df.iterrows():
        table.add_row([metric] + list(row))

    return summary_df
