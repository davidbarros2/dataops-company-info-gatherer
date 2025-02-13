from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, MetaData, Table, UniqueConstraint
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert

if os.path.exists(".env"):
    load_dotenv()
else:
    print("⚠️ Warning: .env file not found. Ensure your env keys are set in system environment variables.")

required_env_vars = [
    'DB_HOST',
    'DB_PORT',
    'DB_USER',
    'DB_PASSWORD',
    'DB_NAME',
]
for var in required_env_vars:
    if not os.getenv(var):
        raise Exception(f"Environment variable {var} is not set")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URI)
metadata = MetaData()

def does_table_exist(table_name: str) -> bool:
    """
    Check if a table exists in the database.

    :param table_name: Name of the table to check.
    """
    metadata.reflect(bind=engine)
    return table_name in metadata.tables

def create_table_if_not_exists(table_name: str, columns: list, unique_constraints: list = []):
    """
    Create a table if it does not exist.
    
    :param table_name: Name of the table to create.
    :param columns: List of SQLAlchemy Column objects.
    :param unique_constraints: List of SQLAlchemy UniqueConstraint objects.
    """
    try:
        if does_table_exist(table_name):
            print(f"✅ Table '{table_name}' already exists.")
            return
        
        constraints = [UniqueConstraint(*constraint) for constraint in unique_constraints]

        table = Table(table_name, metadata, *columns, *constraints)
        metadata.create_all(engine, tables=[table])
        print(f"🎉 Table '{table_name}' has been created successfully!")
    except SQLAlchemyError as e:
        print(f"❌ Error creating table '{table_name}': {e}")

def insert_data(table_name: str, data: list[dict], conflict_columns: list = []):
    """
    Insert data into a table.
    
    :param table_name: Name of the table to insert data into.
    :param data: Dictionary containing column names and values to insert.
    :param conflict_columns: List of column names to check for conflicts (unique constraints).
    """
    try:
        with engine.begin() as conn:  # Ensures transaction safety
            table = Table(table_name, metadata, autoload_with=engine)
            
            # Ensure only valid column names are inserted
            valid_columns = {col.name for col in table.columns}
            filtered_data = [{k: v for k, v in record.items() if k in valid_columns and k != "id"} for record in data]
            if not filtered_data:
                print(f"⚠️ No valid columns found in data for table '{table_name}'.")
                return
            
            # insert statement with conflict resolution
            stmt = insert(table).values(filtered_data) # bulk insert

            if conflict_columns:
                update_dict = {col: stmt.excluded[col] for col in valid_columns if col not in conflict_columns and col != "id"}
                stmt = stmt.on_conflict_do_update(index_elements=conflict_columns, set_=update_dict)

            conn.execute(stmt)
            # No need to commit the transaction, as the context manager does it automatically
            print("✅ Data inserted successfully!")
    except SQLAlchemyError as e:
        print(f"❌ Error inserting data into table '{table_name}': {e}")

if __name__ == "__main__":
    # do nothing
    None