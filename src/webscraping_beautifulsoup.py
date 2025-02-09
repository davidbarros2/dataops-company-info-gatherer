from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from datetime import datetime
from utils import save_tools

CURRENCY_PAGE_URL = "https://x-rates.com/calculator/"
CURRENCY_ELEMENT = {"tag": "span", "class": "ccOutputRslt"}

def fetch_currency_rates(curr_from: str, curr_to: str):
    params = {
        "from": curr_from,
        "to": curr_to,
        "amount": 1
    }

    try:
        response = requests.get(CURRENCY_PAGE_URL, params=params)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")

        rate_element = soup.find(CURRENCY_ELEMENT["tag"], class_=CURRENCY_ELEMENT["class"])
        if not rate_element:
            print("❌ Unable to find the exchange rate on the page.")
            return None
        
        rate = rate_element.text.strip().replace(f" {curr_to}", "").replace(",", "")
        rate = float(rate)

        print(f"- 1 {curr_from} = {rate} {curr_to}")

        conversionRate = [{
            "timestamp": int(time.time()),
            "insert_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from": curr_from,
            "to": curr_to,
            "rate": rate,
            "amount": 1
        }]

        df = pd.DataFrame(conversionRate)
        return df
    except (requests.exceptions.RequestException) as e:
        print(f"❌ Error fetching data: {e}")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return None
        
    return None

if __name__ == "__main__":
    currFrom = input("Enter the currency you want to convert from (e.g. EUR): ")
    currFrom = currFrom.upper() if currFrom else "EUR"

    currTo = input("Enter the currency you want to convert to (e.g. USD): ")
    currTo = currTo.upper() if currTo else "USD"

    df = fetch_currency_rates(currFrom, currTo)

    if df is not None:
        print("\n✅ Data fetched successfully.")
        print(df.head())

        save_tools.save_to_csv(df=df, filename=f"currency_exchange_rate_{currFrom}_{currTo}.csv", append_data=True)
    else:
        print("❌ Unable to fetch data.")