import gspread

def update_sheet(dataframe, spreadsheet_name, sheet_name, credentials_file):
    """
    Authenticates with Google Sheets and updates the 'Master_List' tab
    with the data from the DataFrame.
    """
    try:
        # Authentication
        # Uses the JSON credentials file
        gc = gspread.service_account(credentials_file)

        # Open the Google Sheet by its name
        sh = gc.open(spreadsheet_name)
        
        # Select the specific tab (worksheet)
        ws = sh.worksheet(sheet_name)
        
        print(f"Opening Google Sheet '{spreadsheet_name}' and tab '{sheet_name}'...")

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
        print(f"Error: Tab named '{sheet_name}' not found in the Sheet.")
    except Exception as e:
        print(f"An unexpected error occurred with Google Sheets: {e}")
