import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\books_authors_corrected.xlsx"

def format_sheet():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    desired_columns = [
        "Name of Series",
        "Author Name",
        "Publisher",
        "GoodReads series link",
        "Number of PRIMARY books in the series",
        "Rating (out of 5) of Primary Book 1",
        "Ratings (#) of Primary Book 1",
        "Synopsis (if available)",
        "Romantasy = Yes or No?",
        "Romantasy Sub-Genre of series",
        "Name of agent"
    ]
    
    # Standardize column names if there's any mismatch
    # For example, mapping "Book Title" to "Name of Series"
    col_mapping = {
        "Name": "Name of Series",
        "Title": "Name of Series",
        "Book": "Name of Series",
        "Author": "Author Name",
        "Link": "GoodReads series link",
        "Goodreads Link": "GoodReads series link",
        "URL": "GoodReads series link",
        "Books": "Number of PRIMARY books in the series",
        "Primary Books": "Number of PRIMARY books in the series",
        "Rating": "Rating (out of 5) of Primary Book 1",
        "Stars": "Rating (out of 5) of Primary Book 1",
        "Ratings": "Ratings (#) of Primary Book 1",
        "Count": "Ratings (#) of Primary Book 1",
        "Synopsis": "Synopsis (if available)",
        "Romantasy": "Romantasy = Yes or No?",
        "Sub-Genre": "Romantasy Sub-Genre of series",
        "Agent": "Name of agent"
    }
    
    for old_col, new_col in col_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)
            
    # Add any missing columns as empty strings
    for col in desired_columns:
        if col not in df.columns:
            df[col] = ""
            
    # Reorder columns to the standard 11-column format
    df = df[desired_columns]
    
    print("Applying 11-column format...")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
        print("Styling applied.")
    except Exception as e:
        print(f"Styling error: {e}")
        
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("All done!")

if __name__ == '__main__':
    format_sheet()
