import pandas as pd
from prettytable import PrettyTable


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
                    row.append(d['Autocorrelations']['xs_Return'][lag])
                summary_rows.append(row)
                row_index.append(f'AC {lag}')
        else:
            row = []
            for d in dicts:
                # Handle 'Beta' as a special case to extract the value properly
                if key == 'Beta':
                    row.append(d['Beta'].loc['xs_Return', 'Benchmark'])
                else:
                    row.append(d[key]['xs_Return'])
            summary_rows.append(row)
            row_index.append(key)

    # Create DataFrame from the summary rows
    summary_df = pd.DataFrame(summary_rows, index=row_index, columns=labels).round(2)
    
    # Create PrettyTable instance
    table = PrettyTable()
    table.field_names = ["Metric"] + summary_df.columns.tolist()
    
    for row in summary_df.itertuples():
        table.add_row([row.Index] + list(row[1:]))
    
    #print(table)

    return summary_df
