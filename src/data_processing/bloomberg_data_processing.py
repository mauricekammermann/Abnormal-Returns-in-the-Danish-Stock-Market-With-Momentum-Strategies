import pandas as pd
from pathlib import Path

def load_bloomberg_data(filepath):
    """
    Load the Bloomberg data from the specified Excel file.
    """
    print("Loading Bloomberg data...")
    return pd.read_excel(filepath, sheet_name=0, header=0)  # Adjust as needed for the file structure

def clean_bloomberg_data(df):
    """
    Clean the Bloomberg DataFrame by renaming columns and handling missing data.
    """
    print("Cleaning Bloomberg data...")

    # Rename the columns for clarity
    df.columns = ["date", "spx_index"]

    # Convert "date" to datetime format and automatically handle invalid entries
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")

    # Drop rows where "date" parsing failed
    df = df[~df["date"].isna()]

    # Keep "spx_index" as is, without converting to numeric
    return df

def load_and_clean_bloomberg_data(filepath):
    """
    Load and clean the Bloomberg data from the specified Excel file.
    """
    # Ensure filepath is a Path object
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found at {filepath}. Please ensure the file is in the correct location.")

    # Load and clean the data
    df = load_bloomberg_data(filepath)
    df = clean_bloomberg_data(df)

    return df
