import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# URL for the EUR to USD conversion
url = 'https://www.x-rates.com/calculator/?from=EUR&to=USD&amount=1'

# Send a GET request to the website
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the element that contains the conversion rate
    rate_element = soup.find('span', class_='ccOutputTrail').previous_sibling

    if rate_element:
        conversion_rate = rate_element.text.strip()
        print(f"1 EUR = {conversion_rate} USD")
        
        # Create a DataFrame to store the data
        data = {
            'Date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'From Currency': ['EUR'],
            'To Currency': ['USD'],
            'Conversion Rate': [conversion_rate]
        }
        
        df = pd.DataFrame(data)
        
        # Save to CSV
        csv_filename = 'eur_to_usd_conversion.csv'
        df.to_csv(csv_filename, index=False)
        
        print(f"Conversion rate saved to {csv_filename}")
    else:
        print("Could not find the conversion rate on the page.")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
