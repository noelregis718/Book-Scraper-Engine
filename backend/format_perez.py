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

def format_perez():
    filepath = r"E:\Internship\PocketFM\new_books_master_list_perez_literary_scraped.xlsx"
    df = pd.read_excel(filepath)
    
    # Map Book Title to Name of Series
    if 'Book Title' in df.columns:
        df.rename(columns={'Book Title': 'Name of Series'}, inplace=True)
    
    # Reindex to get the 11 columns
    df = df.reindex(columns=ELEVEN_COLUMN_HEADERS)
    
    # Fill Name of agent column
    df["Name of agent"] = "Perez Literary"
    
    # Fill NaN with empty strings
    df.fillna("", inplace=True)
    
    df.to_excel(filepath, index=False)
    print("Formatted Perez Literary sheet.")

if __name__ == "__main__":
    format_perez()
