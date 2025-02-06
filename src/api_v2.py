from dotenv import load_dotenv
import os
import requests
import pandas as pd

if os.path.exists(".env"):
    load_dotenv()
else:
    print("⚠️ Warning: .env file not found. Ensure API keys are set in system environment variables.")

required_env_vars = ['ALPHA_VANTAGE_API_KEY', 'ALPHA_VANTAGE_URL']
for var in required_env_vars:
    if not os.getenv(var):
        raise Exception(f"Environment variable {var} is not set")

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
URL = os.getenv("ALPHA_VANTAGE_URL")

def fetch_monthly_adjusted_time_series(symbol: str) -> pd.DataFrame:
    params = {
        "function": "TIME_SERIES_MONTHLY_ADJUSTED",
        "symbol": symbol,
        "apikey": API_KEY,
        "datatype": "json"
    }

    try:
        response = requests.get(URL, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            return None

        if "Error Message" in data:
            raise ValueError(f"❌ Error: {data['Error Message']}")

        if "Monthly Adjusted Time Series" not in data:
            if "Information" in data:
                raise ValueError(f"❌ Unexpected API response format: {data.get('Information')}")
            else:
                raise ValueError("❌ Unexpected API response format. Check API key and parameters.")

        time_series = data["Monthly Adjusted Time Series"]
    
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df.index = pd.to_datetime(df.index)
        df.index.name = "date"
        df = df[["1. open", "2. high", "3. low", "4. close", "5. adjusted close", "6. volume"]]
        df.columns = ["open", "high", "low", "close", "adjusted_close", "volume"]
        df = df.sort_index()
        return df
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"❌ Error fetching data: {e}")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return None

def save_to_csv(df: pd.DataFrame, symbol: str):
    try:
        output_dir = "./data"
        os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists
        output_path = os.path.join(output_dir, f"monthly_adjusted_time_series_{symbol}.csv")

        # Prevent accidental overwriting
        if os.path.exists(output_path):
            overwrite = input(f"File {output_path} already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("File not saved.")
                return

        df.to_csv(output_path)
        print("\n✅ Data saved to:", output_path)
    except Exception as e:
        print("❌ Error saving data to CSV:", e)


def read_symbol_from_input():
    symbol = input("Enter the symbol of the stock you want to fetch or use the default (GALP.LS): ")
    return symbol if symbol else "GALP.LS"

if __name__ == "__main__":
    symbol = read_symbol_from_input()
    df = fetch_monthly_adjusted_time_series(symbol)
    if df is not None:
        print(df.head())
        save_to_csv(df, symbol)
    else:
        print("❌ No data available.")