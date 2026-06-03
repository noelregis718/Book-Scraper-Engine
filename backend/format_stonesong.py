import pandas as pd

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

def format_stonesong():
    filepath = r"E:\Internship\PocketFM\Stonesong_Audited_Master_Catalog.xlsx"
    df = pd.read_excel(filepath)
    
    # Map columns
    if 'EXPLICIT BOOK NAME / TITLE' in df.columns:
        df.rename(columns={'EXPLICIT BOOK NAME / TITLE': 'Name of Series'}, inplace=True)
    if 'EXPLICIT AUTHOR NAME' in df.columns:
        df.rename(columns={'EXPLICIT AUTHOR NAME': 'Author Name'}, inplace=True)
        
    # Ensure all 11 columns exist
    for col in ELEVEN_COLUMN_HEADERS:
        if col not in df.columns:
            df[col] = ""
            
    # Set agent name
    df["Name of agent"] = "Stonesong"
    
    # Reorder columns: keep ONLY the 11 columns
    df = df[ELEVEN_COLUMN_HEADERS]
    
    # Fill NaN with empty strings
    df.fillna("", inplace=True)
    
    df.to_excel(filepath, index=False)
    print("Formatted Stonesong sheet with 11-column format, keeping existing columns.")

if __name__ == "__main__":
    format_stonesong()
