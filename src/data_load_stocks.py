import os
import psycopg2
import pandas as pd
import traceback
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database credentials from .env
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Define relative path to the CSV file (inside the project folder)
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "JMT.LS_monthly_adjusted_data.csv")

# Verify if all required environment variables are loaded
if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("Error: One or more environment variables were not loaded correctly.")

# Connect to PostgreSQL database
try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    print("Connected to the database successfully.")

    # Create table if it does not exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS monthly_adjusted_data (
        date DATE PRIMARY KEY,
        open NUMERIC,
        high NUMERIC,
        low NUMERIC,
        close NUMERIC,
        adjusted_close NUMERIC,
        volume BIGINT,
        dividend_amount NUMERIC
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    print("Table 'monthly_adjusted_data' verified/created successfully.")

    # Load CSV data into a pandas DataFrame
    df = pd.read_csv(CSV_FILE_PATH)

    # Rename columns to match the database table
    df.columns = ["date", "open", "high", "low", "close", "adjusted_close", "volume", "dividend_amount"]

    # Convert columns to appropriate data types if necessary
    df["date"] = pd.to_datetime(df["date"]).dt.date  # Ensure date is in the correct format

    # Prepare bulk insert query
    insert_query = """
    INSERT INTO monthly_adjusted_data (date, open, high, low, close, adjusted_close, volume, dividend_amount)
    VALUES %s
    ON CONFLICT (date) DO NOTHING;
    """

    # Convert DataFrame rows to a list of tuples
    data_tuples = [tuple(row) for row in df.to_numpy()]

    # Execute bulk insert
    execute_values(cursor, insert_query, data_tuples)
    conn.commit()
    print(f"{len(df)} records inserted successfully.")

except Exception as e:
    print("An error occurred.")
    print(traceback.format_exc())  # Print full error traceback for debugging

finally:
    # Close database connection
    if conn:
        cursor.close()
        conn.close()
        print("Database connection closed.")
