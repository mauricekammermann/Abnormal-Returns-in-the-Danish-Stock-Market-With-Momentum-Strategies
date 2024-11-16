import pandas as pd

def load_data(data_path):
    """
    Load and preprocess data for the momentum strategy.
    
    Parameters:
    - data_path (str or Path): The file path to the CSV data file.
    
    Returns:
    - pd.DataFrame: A DataFrame with a DateTime index ('date'), sorted in ascending order.
      All other columns are treated as numeric asset data.
    
    Raises:
    - ValueError: If the 'date' column is missing or improperly formatted.
    """
    # Load the CSV file
    data = pd.read_csv(data_path, low_memory=False)

    # Check if the 'date' column is present
    if 'date' not in data.columns:
        raise ValueError("The data must contain a 'date' column.")

    # Convert 'date' to datetime format and set as the index
    try:
        data['date'] = pd.to_datetime(data['date'])
    except Exception as e:
        raise ValueError(f"Error parsing 'date' column: {e}")
    
    data.set_index('date', inplace=True)

    # Sort the index by date
    data.sort_index(inplace=True)

    # Ensure all other columns are numeric
    data = data.apply(pd.to_numeric, errors='coerce')

    # Drop rows with missing dates or all NaN values
    data.dropna(how='all', inplace=True)

    return data
