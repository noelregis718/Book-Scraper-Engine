import pandas as pd
import os

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

def format_maass():
    filepath = r"E:\Internship\PocketFM\Maass_Agency_Complete_List_With_Image_Books.xlsx"
    df = pd.read_excel(filepath)
    
    # Map Book Name to Name of Series
    if 'Book Name' in df.columns:
        df.rename(columns={'Book Name': 'Name of Series'}, inplace=True)
    
    # Reindex to get the 11 columns
    df = df.reindex(columns=ELEVEN_COLUMN_HEADERS)
    
    # Fill NaN with empty strings
    df.fillna("", inplace=True)
    
    df.to_excel(filepath, index=False)
    print("Formatted Maass Agency sheet.")

if __name__ == "__main__":
    format_maass()
