import sys
import operator
import os

from config import get_env_config
from scryfall_client import fetch_all_vampires, load_cache_from_file, save_cache_to_file
from data_processor import process_data
from google_sheets_client import update_sheet

# --- Main Execution Block ---
if __name__ == "__main__":
    # 1. Get configuration based on command-line arguments
    env_config = get_env_config()
    environment = os.getenv("ENVIRONMENT")
    spreadsheet_name = os.getenv("SPREADSHEET_NAME")
    sheet_name = os.getenv("SHEET_NAME")
    vampire_cache_file = os.getenv("VAMPIRE_CACHE_FILE")
    credentials_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


    raw_cards_data = None

    # 2. Load data from API or cache based on environment
    if environment == "pro":
        print("PROD Mode: Calling the Scryfall API (this may take a while)...")
        raw_cards_data = fetch_all_vampires()
    elif environment in ["dev", "pre"]:
        try:
            raw_cards_data = load_cache_from_file(vampire_cache_file)
        except (FileNotFoundError, Exception) as e: # Broader exception for json issues
            print(f"Cache not found or corrupt: {e}. Calling API to create a new one...")
            raw_cards_data = fetch_all_vampires()
            if raw_cards_data:
                save_cache_to_file(raw_cards_data, vampire_cache_file)
    else:
        print(f"Invalid environment: {environment}")
        sys.exit(1)


    # 3. Process data and update the sheet
    if not raw_cards_data:
         print("Error: Could not load data. Exiting.")
         sys.exit(1)

    print(f"Processing and updating sheet '{sheet_name}'...")

    processed_df = process_data(raw_cards_data)
    update_sheet(processed_df, spreadsheet_name, sheet_name, credentials_file)

    print(f"\n--- Process completed for the {environment.upper()} environment ---")