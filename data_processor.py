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
        
        art_crop = 'N/A' # Default
        
        # Check if key exists or is empty
        if card.get('card_faces') and len(card['card_faces']) > 0:
            # It's a two-faced card (Transform, Modal, etc.)
            # Get first face
            face_uris = card['card_faces'][0].get('image_uris', {})
            art_crop = face_uris.get('art_crop', 'N/A')
        else:
            # Regular one-faced card
            top_level_uris = card.get('image_uris', {})
            art_crop = top_level_uris.get('art_crop', 'N/A')
            
        processed_list.append({
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
    # Create index column to calculate physical album positioning
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
