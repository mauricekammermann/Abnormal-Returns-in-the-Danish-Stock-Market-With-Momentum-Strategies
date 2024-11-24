import os
import requests
import pandas as pd
from joblib import Memory
from pathlib import Path

# Define the base path for file locations
BASE_PATH = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_PATH / "data" / "raw"
CACHE_DIR = DATA_PATH / "cache"

# Updated API URL for JSON data
API_URL = "https://data.snb.ch/api/cube/rendoblid/data/json/en?dimSel=D0(1J,E)&fromDate=1999-01-01&toDate=2024-10-31"

# Initialize memoization cache
memory = Memory(CACHE_DIR, verbose=0)

@memory.cache
def fetch_json_data(url):
    """
    Fetches JSON data from the specified API URL and processes it into a DataFrame.
    Memoizes the result to avoid redundant API calls.
    
    Parameters:
    - url (str): The API endpoint to fetch data from.

    Returns:
    - pd.DataFrame: Processed data as a DataFrame.
    """
    print(f"Fetching data from API: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error if the request failed

        # Parse JSON response
        data_json = response.json()
        
        # Extract timeseries values
        timeseries = data_json.get("timeseries", [])
        
        # Convert timeseries data to a list of dictionaries for each date and value
        records = []
        for series in timeseries:
            for value in series.get("values", []):
                records.append({
                    "date": value["date"],
                    "value": value["value"]
                })
        
        # Convert to DataFrame
        data_df = pd.DataFrame(records)
        return data_df

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - URL: {url}")
        return None
    except Exception as err:
        print(f"Other error occurred: {err} - URL: {url}")
        return None

def save_data(data, filename="snb_yield_data.csv"):
    """
    Saves the DataFrame to a CSV file in the specified data directory.
    
    Parameters:
    - data (pd.DataFrame): Data to save.
    - filename (str): The filename to save the data as.
    """
    save_path = DATA_PATH / filename
    data.to_csv(save_path, index=False)
    print(f"Data saved to {save_path}")

def main():
    # Fetch and save SNB yield data
    print("Fetching SNB yield data...")
    data = fetch_json_data(API_URL)
    if data is not None:
        save_data(data)

if __name__ == "__main__":
    main()
