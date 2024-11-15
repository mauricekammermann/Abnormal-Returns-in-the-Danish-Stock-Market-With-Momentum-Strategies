import pandas as pd
from pathlib import Path

def load_snb_data(filepath):
    """
    Load the SNB yield data from the specified CSV file.
    """
    print("Loading SNB yield data...")
    return pd.read_csv(filepath, header=0)

def clean_snb_data(df):
    """
    Clean the SNB yield data by handling the date and value columns.
    """
    print("Cleaning SNB yield data...")

    # Convert "date" to datetime format
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")

    # Drop rows where "date" parsing failed
    df = df[~df["date"].isna()]

    # Ensure "value" is numeric
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Drop rows where "value" is NaN
    df = df.dropna(subset=["value"])

    return df

def load_and_clean_snb_data(filepath):
    """
    Load and clean the SNB yield data from the specified CSV file.
    """
    # Ensure filepath is a Path object
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found at {filepath}. Please ensure the file is in the correct location.")

    # Load and clean the data
    df = load_snb_data(filepath)
    df = clean_snb_data(df)

    return df
