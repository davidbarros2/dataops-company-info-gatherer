import os
import pandas as pd

OUTPUT_DIR = "./data"

def save_to_csv(df: pd.DataFrame, filename: str = None, append_data: bool = False, index: bool = False):
    print("\n📝 Saving data to CSV...")
    try:
        if filename is None:
            print("❌ Error: No filename provided.")
            return
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure directory exists
        output_path = os.path.join(OUTPUT_DIR, filename)

        # Determine if the header should be included
        file_exists = os.path.exists(output_path)
        header = not (append_data and file_exists)

        # Prevent accidental overwriting
        if file_exists and not append_data:
            overwrite = input(f"File {output_path} already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("File not saved.")
                return

        file_write_mode = "a" if append_data else "w"
        df.to_csv(output_path, mode=file_write_mode, header=header, index=index)
        print("\n✅ Data saved to:", output_path)
    except Exception as e:
        print("❌ Error saving data to CSV:", e)

if __name__ == "__main__":
    # do nothing
    None