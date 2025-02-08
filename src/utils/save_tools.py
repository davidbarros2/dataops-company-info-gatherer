import os
import pandas as pd
from pathvalidate import sanitize_filename

OUTPUT_DIR = "./data"

def save_to_csv(df: pd.DataFrame, filename: str = None, ignore_overwrite=False, append_data: bool = False, index: bool = False):
    print("\n📝 Saving data to CSV...")
    try:
        if filename is None:
            print("❌ Error: No filename provided.")
            return
        
        # Sanitize the filename to prevent errors
        sanitized_filename = sanitize_filename(filename)

        os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure directory exists
        output_path = os.path.join(OUTPUT_DIR, sanitized_filename)

        # Determine if the header should be included
        file_exists = os.path.exists(output_path)
        header = not (append_data and file_exists)

        # Prevent accidental overwriting
        if file_exists and not append_data:
            if not ignore_overwrite:
                overwrite = input(f"File {output_path} already exists. Overwrite? (y/n): ").strip().lower()
                if overwrite != 'y':
                    print("File not saved.")
                    return

        file_write_mode = "a" if append_data else "w"
        df.to_csv(output_path, mode=file_write_mode, header=header, index=index)
        print("\n✅ Data saved to:", output_path)
    except Exception as e:
        print("❌ Error saving data to CSV:", e)

def load_existing_dataframe(filename, columns) -> pd.DataFrame:
    """Loads existing news from CSV if the file exists."""
    try:
        if filename is None:
            print("❌ Error: No filename provided.")
            return pd.DataFrame(columns=columns)
        
        # Sanitize the filename to prevent errors
        sanitized_filename = sanitize_filename(filename)
        os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure directory exists
        output_path = os.path.join(OUTPUT_DIR, sanitized_filename)

        if os.path.exists(output_path):
            return pd.read_csv(output_path)
        
        return pd.DataFrame(columns=columns)
    except Exception as e:
        print("❌ Error reading data from CSV:", e)
        return pd.DataFrame(columns=columns)

if __name__ == "__main__":
    # do nothing
    None