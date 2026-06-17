import pandas as pd

FILE_PATH = "e:/Internship/PocketFM/park_and_fine_books.xlsx"

STANDARD_COLUMNS = [
    'Name of Series',
    'Author Name',
    'Publisher',
    'GoodReads series link',
    'Number of PRIMARY books in the series',
    'Rating (out of 5) of Primary Book 1',
    'Ratings (#) of Primary Book 1',
    'Synopsis (if available)',
    'Romantasy = Yes or No?',
    'Romantasy Sub-Genre of series',
    'Name of agent'
]

def main():
    print("Loading Park & Fine excel...")
    df = pd.read_excel(FILE_PATH)
    
    # Create the new columns if they don't exist
    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
            
    # Map the existing data
    if 'Book Name' in df.columns:
        df['Name of Series'] = df['Book Name'].combine_first(df['Name of Series'])
    if 'Author' in df.columns:
        df['Author Name'] = df['Author'].combine_first(df['Author Name'])
        
    # Set static values
    df['Publisher'] = "Park & Fine Literary and Media"
    df['Name of agent'] = "Park & Fine"
    
    # Only keep the standard columns
    df = df[STANDARD_COLUMNS]
    
    df.to_excel(FILE_PATH, index=False)
    print("Format applied successfully!")

if __name__ == "__main__":
    main()
