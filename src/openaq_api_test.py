import pandas as pd
import requests

OPENAQ_API_KEY = "2df1e1ad492dbcc9293e82253f0ddffca796f334d424d0c1765e827c87a219ea"

# Base URL for OpenAQ API V3
BASE_URL = "https://api.openaq.org/v3/"

endpoint = f"{BASE_URL}parameters"

# Parameters for this endpoint are minimal
params = {
    "limit": 10 # Get up to 10 parameters
}

# API key goes in the headers
headers = {
    "X-API-Key": OPENAQ_API_KEY
}

print("Fetching air quality parameters from OpenAQ API...")

try:
    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status() # Check for HTTP errors

    api_data = response.json() # Get the raw JSON response

    # --- Create Pandas DataFrame directly from 'results' ---
    # The /parameters endpoint usually returns a list of dictionaries directly under 'results'
    if api_data and 'results' in api_data:
        df = pd.DataFrame(api_data['results'])
        #print("\nData successfully loaded into Pandas DataFrame:")
        #print(df.head()) # Print the first 5 rows
        #print(f"\nDataFrame shape: {df.shape}") # Show number of rows and columns
    else:
        print("No parameters data found or an unexpected API response format.")

except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
    if hasattr(response, 'text'):
        print(f"Response content: {response.text}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

print('\n', df)

df.to_csv('data.csv', sep=';', decimal=',', encoding='utf-8', index=False)