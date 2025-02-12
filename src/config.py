import psycopg2
from psycopg2 import OperationalError

# Database connection details
host = "dpg-cumfg8dds78s73cva18g-a.frankfurt-postgres.render.com"
dbname = "teste"
user = "postgre_grupo3_user"
password = "h7U2hA3QVxVVf3w1ZMytkRueKeKexkVW"
port = "5432"

def create_connection():
    """Create and return a connection to the PostgreSQL database with SSL."""
    try:
        # Connect to the PostgreSQL database with SSL mode enabled
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=dbname,
            user=user,
            password=password,
            sslmode='require'  # Enforces SSL connection
        )
        return connection
    except OperationalError as e:
        print(f"Error: {e}")
        return None

def test_connection():
    """Test the connection to the PostgreSQL database."""
    connection = create_connection()
    if connection:
        print("Connection successful!")
        connection.close()  # Close the connection after testing
    else:
        print("Failed to connect to the database.")

# Run the test
test_connection()

