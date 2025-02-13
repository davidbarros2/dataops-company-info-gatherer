from sqlalchemy import create_engine, Column, String, Text, BigInteger, DateTime
from utils.sqlalchemy.config import engine, create_table_if_not_exists, insert_data
from utils.save_tools import load_existing_dataframe
import pandas as pd
import re

FILES_TO_DEPLOY = {
    "news": {
        "filename": "jerónimo martins_news.csv",
        "columns": ["Date", "Title", "Link", "Summary"]
    },
}
TABLE_NAME = "news"

def load_saved_news() -> pd.DataFrame:
    df = load_existing_dataframe(FILES_TO_DEPLOY["news"]["filename"], FILES_TO_DEPLOY["news"]["columns"])
    print(f"\n📰 Saved news loaded: found {len(df)} news in file")
    # print(df.head())
    return df

def to_snake_case(text: str) -> str:
    """
    Convert text to snake_case.

    :param text: Text to convert.
    """
    text = text.lower().strip()             # to lowercase and stip spaces
    text = re.sub(r"[^\w\s]", "", text)     # remove special characters
    text = re.sub(r"\s+", "_", text)        # replace spaces with underscores
    return text

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y %H:%M", errors="coerce")
    df.sort_values(by="Date", ascending=True, inplace=True)
    df.drop_duplicates(subset=["Title", "Summary"], keep="last", inplace=True)
    df.columns = [to_snake_case(col) for col in df.columns]
    return df

def deploy_to_database(df: pd.DataFrame):
    try:
        conn = engine.connect()
        print("🚀 Connected to the database!")
    except Exception as e:
        print("❌ Error connecting to the database:", e)
        exit(1)
    
    columns = [
        Column("id", BigInteger, primary_key=True, autoincrement=True),
        Column("date", DateTime, nullable=False),
        Column("title", String, nullable=False),
        Column("link", String),
        Column("summary", Text),
    ]
    create_table_if_not_exists(TABLE_NAME, columns, unique_constraints=[("date", "title")])

    insert_data(TABLE_NAME, df.to_dict(orient="records"), conflict_columns=["date", "title"])

    try:
        conn.close()
    except Exception as e:
        print("❌ Error closing database:", e)
        exit(1)

def main():
    df = load_saved_news()
    df = clean_data(df)

    deploy_to_database(df)

if __name__ == "__main__":
    main()