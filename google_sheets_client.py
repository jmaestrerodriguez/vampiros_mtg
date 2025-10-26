import gspread

def update_sheet(dataframe, sheet_name, worksheet_name, creds_path):
    """
    Authenticates with Google Sheets and updates a worksheet
    with the data from the given DataFrame.
    """
    try:
        # Authentication
        gc = gspread.service_account(filename=creds_path)

        # Open the Google Sheet by its name
        sh = gc.open(sheet_name)

        # Select the specific tab (worksheet)
        ws = sh.worksheet(worksheet_name)

        print(f"Opening Google Sheet '{sheet_name}' and worksheet '{worksheet_name}'...")

        # Clear ALL content from this specific tab
        ws.clear()

        # Prepare the data for gspread (headers + all rows)
        headers = dataframe.columns.tolist()
        values = dataframe.values.tolist()

        # Update the sheet in one go
        ws.update(range_name='A1', values=[headers] + values, value_input_option='USER_ENTERED')

        print("Google Sheet updated successfully!")

    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Error: Google Sheet named '{sheet_name}' not found.")
        print("Make sure the name is correct and you have shared it with the service account email.")
    except gspread.exceptions.WorksheetNotFound:
        print(f"Error: Tab named '{worksheet_name}' not found in the Sheet.")
    except Exception as e:
        print(f"An unexpected error occurred with Google Sheets: {e}")

