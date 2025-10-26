import sys

from config import get_app_config, VAMPIRE_CACHE_FILE, CREDS_FILE
from scryfall_client import fetch_all_vampires, load_cache_from_file, save_cache_to_file
from data_processor import process_data
from google_sheets_client import update_sheet

# --- Main Execution Block ---
if __name__ == "__main__":
    # 1. Get configuration based on command-line arguments
    config, env_arg = get_app_config()
    sheet_name = config["sheet_name"]
    worksheet_name = config["worksheet_name"]

    raw_cards_data = None

    # 2. Load data from API or cache based on environment
    if env_arg == "pro":
        print("PROD Mode: Calling the Scryfall API (this may take a while)...")
        raw_cards_data = fetch_all_vampires()
    elif env_arg == "dev":
        try:
            raw_cards_data = load_cache_from_file(VAMPIRE_CACHE_FILE)
        except (FileNotFoundError, Exception) as e: # Broader exception for json issues
            print(f"Cache not found or corrupt: {e}. Calling API to create a new one...")
            raw_cards_data = fetch_all_vampires()
            if raw_cards_data:
                save_cache_to_file(raw_cards_data, VAMPIRE_CACHE_FILE)

    # 3. Process data and update the sheet
    if not raw_cards_data:
        print("Error: Could not load data. Exiting.")
        sys.exit(1)

    print(f"Processing and updating sheet '{sheet_name}'...")

    processed_df = process_data(raw_cards_data)
    update_sheet(processed_df, sheet_name, worksheet_name, CREDS_FILE)

    print(f"\n--- Process completed for the {env_arg.upper()} environment ---")