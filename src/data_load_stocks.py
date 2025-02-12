import psycopg2
import pandas as pd

# Database connection details
DB_HOST = "dpg-cumfg8dds78s73cva18g-a.frankfurt-postgres.render.com"
DB_PORT = "5432"
DB_NAME = "postgre_grupo3"
DB_USER = "postgre_grupo3_user"
DB_PASSWORD = "h7U2hA3QVxVVf3w1ZMytkRueKeKexkVW"

# Path to the CSV file (update this to your actual file path)
CSV_FILE_PATH = "C:/Users/david/Documents/GitHub/dataops-company-info-gatherer/data/JMT.LS_monthly_adjusted_data.csv"

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    print("Connected to the database successfully!")

    # Create table (adjust column names & types based on your CSV)
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
    print("Table 'monthly_adjusted_data' is ready.")

    # Load data from CSV
    df = pd.read_csv(CSV_FILE_PATH)

    # Ensure column names match the database table
    df.columns = ["date", "open", "high", "low", "close", "adjusted_close", "volume", "dividend_amount"]

    # Insert data into the database
    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO monthly_adjusted_data (date, open, high, low, close, adjusted_close, volume, dividend_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (date) DO NOTHING;
            """,
            tuple(row)
        )
    
    conn.commit()
    print("Data inserted successfully!")

except Exception as e:
    print(f"Error: {e}")

finally:
    if conn:
        cursor.close()
        conn.close()
        print("Database connection closed.")
