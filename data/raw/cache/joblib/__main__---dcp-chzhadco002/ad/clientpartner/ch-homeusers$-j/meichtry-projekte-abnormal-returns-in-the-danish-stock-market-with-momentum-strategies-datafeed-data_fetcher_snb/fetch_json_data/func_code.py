# first line: 17
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
    except Exception as err:
        print(f"Other error occurred: {err} - URL: {url}")
