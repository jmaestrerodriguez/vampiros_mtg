import requests
import gspread
import pandas as pd
import time

# --- CONFIGURATION ---
# The EXACT name of your Google Sheet
SHEET_NAME = "vampiros_mtg" 
# The name of the tab (worksheet) where the script will dump the data
WORKSHEET_NAME = "master"
# The name of your credentials file
CREDS_FILE = "credentials.json"
# ---------------------


def fetch_all_vampires():
    """
    Queries the Scryfall API and handles pagination to get all
    unique vampire illustrations.
    """
    all_cards = []
    # This is the magic query for Scryfall
    # q=t:vampire -> type is vampire
    # unique:art -> collapse results by unique illustration_id
    search_url = "https://api.scryfall.com/cards/search?q=t:vampire+(game:paper)&unique=art&order=released&dir=asc"

    print("Starting Scryfall query...")

    # Loop as long as Scryfall provides a 'next_page' URL
    while search_url:
        try:
            response = requests.get(search_url)
            # If something goes wrong (e.g., 500 error), the script will stop
            response.raise_for_status() 
            data = response.json()

            # Add the batch of cards from this page to our main list
            all_cards.extend(data['data'])

            # Pagination logic
            if data['has_more']:
                search_url = data['next_page']
                print(f"Loading next page... (Total: {len(all_cards)} cards)")
                # It's good practice to wait a bit between requests
                time.sleep(0.1) # 100ms delay
            else:
                search_url = None # We're done, exit the loop

        except requests.exceptions.RequestException as e:
            print(f"Error contacting Scryfall: {e}")
            return None # Exit the function returning nothing

    print(f"Scryfall query complete. Total illustrations: {len(all_cards)}")
    return all_cards


def process_data(cards_json):
    """
    Transforms the raw JSON response from Scryfall into a clean
    list of dictionaries, ready for a Pandas DataFrame.
    """
    processed_list = []
    for card in cards_json:
        # Use .get() to safely access keys that might not exist
        image_uris = card.get('image_uris', {}) # Default to empty dict
        
        processed_list.append({
            "art_crop": image_uris.get('art_crop', 'N/A'),
            # Check if 'foil' is in the list of available finishes
            "finishes": 'foil' in card.get('finishes', []), 
            "name": card.get('name'),
            "type_line": card.get('type_line'),
            "set": card.get('set_name'),
            "collector_number": card.get('collector_number'),
            "artist": card.get('artist'),
            "scryfall_uri": card.get('scryfall_uri'),
        })
    
    print(f"Processed {len(processed_list)} records.")
    
    # Convert the list into a Pandas DataFrame for easy handling
    df = pd.DataFrame(processed_list)
    # Convierte el índice (0,1,2...) en una columna "index"
    df = df.reset_index() 
    df['album_page'] = (df['index'] // 18) + 1
    df['album_position'] = (df['index'] % 18) + 1
    
    final_column_order = [
        # Aux
            'index', 
            'scryfall_uri',
            'art_crop',       
        # View    
            'album_page', 
            'album_position', 
            'finishes', 
            'name', 
            'type_line', 
            'set', 
            'collector_number', 
            'artist', 
        ]
    
    df = df[final_column_order]

    return df

def update_sheet(dataframe, sheet_name, worksheet_name, creds_path):
    """
    Authenticates with Google Sheets and updates the 'Master_List' tab
    with the data from the DataFrame.
    """
    try:
        # Authentication
        # Uses the JSON credentials file
        gc = gspread.service_account(filename=creds_path)

        # Open the Google Sheet by its name
        sh = gc.open(sheet_name)
        
        # Select the specific tab (worksheet)
        ws = sh.worksheet(worksheet_name)
        
        print(f"Opening Google Sheet '{sheet_name}' and tab '{worksheet_name}'...")

        # Clear ALL content from this specific tab
        # This is destructive and ensures we have fresh data
        ws.clear()
        
        # Prepare the data for gspread
        # (includes headers + all rows)
        headers = dataframe.columns.tolist()
        values = dataframe.values.tolist()
        
        # Update the sheet in one go (much faster than cell by cell)
        # We start at cell 'A1'
        # ws.update('A1', [headers] + values, value_input_option='USER_ENTERED')
        # La línea corregida (sin advertencia)
        ws.update(range_name='A1', values=[headers] + values, value_input_option='USER_ENTERED')
        
        print("Google Sheet updated successfully!")

    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Error: Google Sheet named '{sheet_name}' not found.")
        print("Make sure the name is correct and you have shared it with the service account email.")
    except gspread.exceptions.WorksheetNotFound:
        print(f"Error: Tab named '{worksheet_name}' not found in the Sheet.")
    except Exception as e:
        print(f"An unexpected error occurred with Google Sheets: {e}")


# --- Main Execution Block ---
# This code only runs when the script is executed directly
if __name__ == "__main__":
    
    # 1. Extract
    # Fetch the raw data from the API
    raw_cards_data = fetch_all_vampires()
    
    # Only proceed if the data was successfully fetched
    if raw_cards_data:
        # 2. Transform
        # Process the raw JSON into a clean list
        processed_df = process_data(raw_cards_data)
        
        # 3. Load
        # Upload the DataFrame to Google Sheets
        update_sheet(processed_df, SHEET_NAME, WORKSHEET_NAME, CREDS_FILE)
        
        print("\n--- Process completed ---")