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

def format_stonesong_books():
    filepath = r"E:\Internship\PocketFM\Stonesong_Books.xlsx"
    df = pd.read_excel(filepath)
    
    # Map columns
    if 'Book Name' in df.columns:
        df.rename(columns={'Book Name': 'Name of Series'}, inplace=True)
        
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
    print("Formatted Stonesong_Books sheet with 11-column format.")

if __name__ == "__main__":
    format_stonesong_books()
