import requests
import pandas as pd
from datetime import datetime

# Alpha Vantage API key
API_KEY = 'W38JLMPWTRQN4FQI'

# Symbol for Jerónimo Martins on the Lisbon Stock Exchange
symbol = 'JMT.LS'

# API endpoint for free daily time series data
url = f'https://www.alphavantage.co/query'

# Parameters for the API call
params = {
    'function': 'TIME_SERIES_DAILY',  # Free endpoint
    'symbol': symbol,
    'apikey': API_KEY,
    'outputsize': 'full',  # 'compact' for last 100 data points, 'full' for entire history
    'datatype': 'json'
}

# Make the API request
response = requests.get(url, params=params)
data = response.json()

# Check if the response contains the correct data
if 'Time Series (Daily)' not in data:
    print("Error fetching data:", data.get("Error Message", data.get("Note", data.get("Information", "Unknown error occurred."))))
else:
    # Extract the time series data
    time_series = data['Time Series (Daily)']

    # Convert the time series data to a pandas DataFrame
    df = pd.DataFrame.from_dict(time_series, orient='index')

    # Rename columns for clarity
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

    # Convert index to datetime
    df.index = pd.to_datetime(df.index)

    # Sort by date
    df.sort_index(ascending=True, inplace=True)

    # Save to CSV
    filename = f'JMT_LS_stock_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(filename)

    print(f"Data saved to {filename}")
