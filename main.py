import requests
import gspread
import pandas as pd
import time
import sys
import json

def run_sync_prod(request):
    """
    Función principal para ser llamada por Google Cloud.
    Ejecuta el pipeline completo para el entorno PROD.
    """
    # Define las variables de PROD aquí dentro
    SHEET_NAME = "vampiros_mtg_prod"
    WORKSHEET_NAME = "master"
    CREDS_FILE = "credentials.json" # Google Cloud usará las suyas

    print("Modo PROD (Cloud Function): Llamando a la API de Scryfall...")
    raw_cards_data = fetch_all_vampires()

    if not raw_cards_data:
        print("Error: No se pudieron cargar los datos. Saliendo.")
        return "Error: No data from Scryfall", 500

    print(f"Procesando y actualizando el sheet '{SHEET_NAME}'...")
    processed_df = process_data(raw_cards_data)

    # OJO: ¿Dónde están las credenciales?
    # En Cloud Functions, no usas el JSON. 
    # Usas las credenciales "por defecto" de la cuenta de servicio de la función.
    # Debes cambiar tu función 'update_sheet' para que 'gc = gspread.oauth()'
    # (Esto es un cambio mayor, pero es el paso final)
    # Por ahora, asumamos que subes tu JSON junto al script.

    update_sheet(processed_df, SHEET_NAME, WORKSHEET_NAME, CREDS_FILE)

    print(f"\n--- Proceso completado para el entorno PROD ---")
    return "OK", 200

def load_cache_from_file(cache_file):
    """Carga los datos en crudo desde un archivo JSON de caché."""
    print(f"Modo DEV: Cargando datos desde el caché local '{cache_file}'...")
    # NOTA: En esta versión, dejamos que el 'try/except' se maneje 
    # en el bloque principal, para que podamos reaccionar al error.
    with open(cache_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Éxito: Cargados {len(data)} registros desde el caché.")
    return data

def save_cache_to_file(data, cache_file):
    """Guarda los datos en crudo en un archivo JSON de caché."""
    print(f"Guardando {len(data)} registros en '{cache_file}' para uso de DEV...")
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print("Caché local actualizado.")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el caché. {e}")

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
    list of dictionaries, using Scryfall API key names as columns.
    
    This version correctly handles 'transform' (two-faced) cards
    by checking the 'card_faces' array for image URIs.
    """
    processed_list = []
    for card in cards_json:
        
        art_crop = 'N/A' # Valor por defecto
        
        # Primero, comprueba si la clave 'card_faces' existe y no está vacía
        if card.get('card_faces') and len(card['card_faces']) > 0:
            # Es una carta de dos caras (Transform, Modal, etc.)
            # Cogemos las imágenes de la PRIMERA CARA
            face_uris = card['card_faces'][0].get('image_uris', {})
            art_crop = face_uris.get('art_crop', 'N/A')
        else:
            # Es una carta normal de una sola cara
            top_level_uris = card.get('image_uris', {})
            art_crop = top_level_uris.get('art_crop', 'N/A')
            
        processed_list.append({
            # Las otras claves (name, type_line, etc.) están bien
            # en el nivel superior, incluso para cartas transform.
            "name": card.get('name'), 
            "type_line": card.get('type_line'),
            "set": card.get('set_name'), 
            "collector_number": card.get('collector_number'),
            "artist": card.get('artist'),
            "finishes": 'foil' in card.get('finishes', []), 
            "art_crop": art_crop, # Usamos nuestra variable 'art_crop'
            "scryfall_uri": card.get('scryfall_uri')
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
    run_sync_prod(0)