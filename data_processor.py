import pandas as pd

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

        prices = card.get('prices', {}) # Get the prices object, or empty dict
        # Prioritize foil price in euros
        eur_price = prices.get('eur_foil') # Try to get foil price
        # If foil price is None or not available, try the regular euro price
        if not eur_price:
            eur_price = prices.get('eur', 'N/A') # Fallback to regular price, then 'N/A'

        processed_list.append({
            # Las otras claves (name, type_line, etc.) están bien
            # en el nivel superior, incluso para cartas transform.
            "name": card.get('name'), 
            "type_line": card.get('type_line'),
            "set": card.get('set_name'), 
            "collector_number": card.get('collector_number'),
            "artist": card.get('artist'),
            "is_foil": 'foil' in card.get('finishes', []), 
            "art_crop": art_crop, # Usamos nuestra variable 'art_crop'
            "scryfall_uri": card.get('scryfall_uri'),
            "rarity": card.get('rarity'),
            "eur_price": eur_price,
        })
    
    print(f"Processed {len(processed_list)} records.")
    
    # Convert the list into a Pandas DataFrame for easy handling
    df = pd.DataFrame(processed_list)
    # Convierte el índice (0,1,2...) en una columna "index"
    df = df.reset_index() 
    df['album_position'] = (df['index'] % 18) + 1
    df['album_sheet'] = (df['index'] // 18) + 1
    df['album_slot'] = ['Front' if (pos < 9) else 'Back' for pos in (df['index'] % 18)]
    df['album_page']= (df['index'] // 9) + 1
    df['slot_position'] = (df['index'] % 9) + 1
    
    final_column_order = [
        # Aux
            'index', 
            'scryfall_uri',
            'art_crop',       
        # View    
            'album_sheet', 
            'album_position', 
            'album_page', 
            'album_slot', 
            'slot_position',
        # Card info                 
            'is_foil', 
            'name', 
            'type_line', 
            'set', 
            'collector_number', 
            'artist',
            'rarity',
            'eur_price',
        ]
    
    df = df[final_column_order]
    df = df.fillna("")

    return df
