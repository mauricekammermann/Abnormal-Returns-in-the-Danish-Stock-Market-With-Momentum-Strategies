# first line: 17
@memory.cache
def fetch_data(url):
    """
    Fetches data from the specified API URL and returns it as a DataFrame.
    Memoizes the result to avoid redundant API calls.
    
    Parameters:
    - url (str): The API endpoint to fetch data from.

    Returns:
    - pd.DataFrame: Data retrieved from the API.
    """
    print(f"Fetching data from API: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error if the request failed

        # Load CSV data directly into a DataFrame
        data = pd.read_csv(pd.compat.StringIO(response.text), delimiter=";")
        return data

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - URL: {url}")
    except Exception as err:
        print(f"Other error occurred: {err} - URL: {url}")
