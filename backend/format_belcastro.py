import pandas as pd
import os

def format_belcastro():
    input_file = r"E:\Internship\PocketFM\Belcastro_Agency_Books_VERIFIED.xlsx"
    output_file = r"E:\Internship\PocketFM\Belcastro_Agency_Formatted.xlsx"
    
    print(f"Loading {input_file}...")
    df = pd.read_excel(input_file)
    
    # Map common column names to the 11-column format names
    column_mapping = {
        'Book Title': 'Name of Series',
        'Author': 'Author Name',
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)
            
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
    
    # Only keep the 11 columns in order
    new_columns = []
    for col in ELEVEN_COLUMN_HEADERS:
        new_columns.append(col)
        if col not in df.columns:
            df[col] = "" # Add missing column
            
    df = df[new_columns]
    df.fillna("", inplace=True)
    
    df.to_excel(output_file, index=False)
    print("Formatted successfully. Saved to:", output_file)

if __name__ == "__main__":
    format_belcastro()
