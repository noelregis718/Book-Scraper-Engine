import pandas as pd
import os

SOURCE_FILE = "authors_only.xlsx"
OUTPUT_FILE = "Pilkington_Agency_Catalog_Final.xlsx"

def init_pilkington():
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: {SOURCE_FILE} not found!")
        return

    df = pd.read_excel(SOURCE_FILE)
    
    # Rename 'Authors' to 'Author Name' for consistency if it exists
    if 'Authors' in df.columns:
        df = df.rename(columns={'Authors': 'Author Name'})
    
    # Ensure 'Name of Series' (Book Name) column exists
    if 'Name of Series' not in df.columns:
        df['Name of Series'] = "N/A"

    # Add the 11 Professional Columns
    new_cols = [
        'Publisher',
        'GoodReads series link', 
        'Number of PRIMARY books in the series', 
        'Rating (out of 5) of Primary Book 1', 
        'Ratings (#) of Primary Book 1', 
        'Synopsis (if available)', 
        'Romantasy = Yes or No?', 
        'Romantasy Sub-Genre of series',
        'Name of agent',
        'Date Scraped',
        'Notes'
    ]
    
    for col in new_cols:
        if col not in df.columns:
            df[col] = "N/A"
            
    # Reorder columns to match your preferred layout
    ordered_cols = ['Name of Series', 'Author Name', 'Publisher', 'GoodReads series link', 
                    'Number of PRIMARY books in the series', 'Rating (out of 5) of Primary Book 1', 
                    'Ratings (#) of Primary Book 1', 'Synopsis (if available)', 
                    'Romantasy = Yes or No?', 'Romantasy Sub-Genre of series', 'Name of agent']
    
    # Only keep the ones we have
    df = df[ordered_cols]
    
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Successfully initialized {OUTPUT_FILE} with {len(df)} authors and 11 columns.")

if __name__ == "__main__":
    init_pilkington()
