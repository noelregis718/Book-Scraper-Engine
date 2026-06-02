import pandas as pd
import sys

def format_ladderbird():
    filepath = r"E:\Internship\PocketFM\ladderbird_books_scrape.xlsx"
    df = pd.read_excel(filepath)
    print("Original columns:", df.columns.tolist())
    
    ELEVEN_COLUMN_HEADERS = [
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
        "Name of agent",
    ]
    
    # Map any existing columns to the new headers if they have slight variations
    column_mapping = {
        'Title': 'Name of Series',
        'Book Title': 'Name of Series',
        'Author': 'Author Name',
        'Goodreads Link': 'GoodReads series link',
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)
            
    # Now build the new column order
    # Only the 11 columns in order
    new_columns = []
    for col in ELEVEN_COLUMN_HEADERS:
        new_columns.append(col)
        if col not in df.columns:
            df[col] = "" # Add missing column
            
    df = df[new_columns]
    
    # Fill agent if missing or empty
    if "Name of agent" in df.columns:
        df["Name of agent"] = df["Name of agent"].replace("", "Ladderbird Agency")
        df["Name of agent"] = df["Name of agent"].fillna("Ladderbird Agency")
        
    df.fillna("", inplace=True)
    
    df.to_excel(filepath, index=False)
    print("Formatted Ladderbird sheet. New columns:", df.columns.tolist())

if __name__ == "__main__":
    format_ladderbird()
