import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURATION ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1qQegfsBODu8GAfe1lMCxNtYV75MWCEtQOopiwH4JcWY/edit"
WORKSHEET_NAME = "Lifecycle Tracker - Master"
TRIGGER_STATUS = "Ready for Outreach"
CREDENTIALS_FILE = "credentials.json"
# ---------------------

def authenticate_google_sheets():
    """Authenticates with Google Sheets using a Service Account JSON file."""
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"ERROR: {CREDENTIALS_FILE} not found. Please place it in the same directory.")
        return None
        
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    gc = gspread.authorize(credentials)
    return gc

def generate_context_string_for_plugin(scenario, licensor, authors, books):
    """
    Instead of calling ChatGPT directly, this creates a perfectly bundled instruction string.
    We inject this string into the Google Sheet, and your ChatGPT Plugin reads it!
    """
    context = ""
    
    if scenario == 1:
        context += f"Direct Author Outreach. Recipient: {authors[0]}. Book to license: {books[0]}."
    elif scenario == 2:
        context += f"Agency Outreach. Recipient: {licensor}. Author they represent: {authors[0]}. Book to license: {books[0]}."
    elif scenario == 3:
        context += f"Agency Outreach (Multiple Authors/Books). Recipient: {licensor}. Books to license: "
        for i in range(len(books)):
            context += f"'{books[i]}' by {authors[i]}, "
    elif scenario == 4:
        context += f"Direct Author Outreach (Multiple Books). Recipient: {authors[0]}. Books to license: "
        for book in books:
            context += f"{book}, "
            
    return context.strip(", ")

def process_outreach_queue():
    gc = authenticate_google_sheets()
    if not gc:
        return
        
    print("Connecting to Google Sheet...")
    try:
        sheet = gc.open_by_url(SHEET_URL)
        worksheet = sheet.worksheet(WORKSHEET_NAME)
    except Exception as e:
        print(f"Failed to open worksheet: {e}")
        return

    # Fetch all data
    data = worksheet.get_all_records(head=3) # Assumes Row 3 is the header
    df = pd.DataFrame(data)
    
    # Check if necessary columns exist
    required_cols = ['Author Name', 'Title / IP', 'Licensor (Legal name)', 'Status']
    for col in required_cols:
        if col not in df.columns:
            print(f"ERROR: Missing required column '{col}' in the sheet.")
            return

    # Filter for rows that need processing
    queue_df = df[df['Status'] == TRIGGER_STATUS]
    
    if queue_df.empty:
        print("No rows found with Status == 'Ready for Outreach'. Sleeping...")
        return
        
    print(f"Found {len(queue_df)} rows to process. Grouping by Agency...")

    # Group by Licensor to handle Scenarios 3 & 4
    grouped = queue_df.groupby('Licensor (Legal name)')
    
    for licensor, group in grouped:
        authors = group['Author Name'].tolist()
        books = group['Title / IP'].tolist()
        row_indices = group.index.tolist() # To update the sheet later
        
        # Determine Scenario
        unique_authors = set(authors)
        is_direct = (len(unique_authors) == 1 and authors[0] == licensor)
        
        if is_direct and len(books) == 1:
            scenario = 1
            print(f"Executing Scenario 1 (Direct Single) for {authors[0]}")
        elif not is_direct and len(books) == 1:
            scenario = 2
            print(f"Executing Scenario 2 (Agency Single) for {licensor}")
        elif not is_direct and len(books) > 1:
            scenario = 3
            print(f"Executing Scenario 3 (Agency Multiple) for {licensor}")
        elif is_direct and len(books) > 1:
            scenario = 4
            print(f"Executing Scenario 4 (Direct Multiple) for {authors[0]}")
        else:
            scenario = 2 # Default fallback
            
        # Create the Context String
        print("Generating bundled context for the Sheets Plugin...")
        plugin_context = generate_context_string_for_plugin(scenario, licensor, authors, books)
        
        print("Context ready! Updating Google Sheet...")
        
        # In a real run, we will write `plugin_context` to the sheet using gspread
        # For example: worksheet.update_cell(row_index + 4, context_col_index, plugin_context)
        
        print("-" * 50)

if __name__ == "__main__":
    print("Starting PocketFM Auto-Drafter Engine...")
    # process_outreach_queue()
