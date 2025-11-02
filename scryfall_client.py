import requests
import time
import json

def load_cache_from_file(cache_file):
    """Loads raw data from a JSON cache file."""
    print(f"DEV Mode: Loading data from local cache '{cache_file}'...")
    with open(cache_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Success: Loaded {len(data)} records from cache.")
    return data

def save_cache_to_file(data, cache_file):
    """Saves raw data to a JSON cache file."""
    print(f"Saving {len(data)} records to '{cache_file}' for DEV use...")
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print("Local cache updated.")
    except Exception as e:
        print(f"ERROR: Could not save the cache. {e}")

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
                time.sleep(0.1)  # 100ms delay
            else:
                search_url = None  # We're done, exit the loop

        except requests.exceptions.RequestException as e:
            print(f"Error contacting Scryfall: {e}")
            return None  # Exit the function returning nothing

    print(f"Scryfall query complete. Total illustrations: {len(all_cards)}")
    return all_cards