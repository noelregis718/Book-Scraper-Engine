import pandas as pd
import os
import sys

def merge_and_format_corvisiero():
    file1 = r"E:\Internship\PocketFM\corvisieroagency_book_author_scrape.xlsx"
    file2 = r"E:\Internship\PocketFM\corvisiero_added_books.xlsx"
    output_file = r"E:\Internship\PocketFM\corvisiero_merged.xlsx"
    
    print(f"Loading {file1}...")
    df1 = pd.read_excel(file1)
    print("Columns 1:", df1.columns.tolist())
    
    print(f"Loading {file2}...")
    df2 = pd.read_excel(file2)
    print("Columns 2:", df2.columns.tolist())
    
    # Concatenate
    df = pd.concat([df1, df2], ignore_index=True)
    
    # Map common column names to the 11-column format names
    column_mapping = {
        'Title': 'Name of Series',
        'Book Title': 'Name of Series',
        'Book Name': 'Name of Series',
        'Author': 'Author Name',
        'Goodreads Link': 'GoodReads series link',
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            # If the new column already exists, we might need to coalesce.
            df.rename(columns={old_col: new_col}, inplace=True)
        elif old_col in df.columns and new_col in df.columns:
            # Combine them
            df[new_col] = df[new_col].combine_first(df[old_col])
            
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
    
    # Deduplicate just in case, based on Name of Series and Author Name
    initial_len = len(df)
    df.drop_duplicates(subset=["Name of Series", "Author Name"], keep='first', inplace=True)
    print(f"Dropped {initial_len - len(df)} duplicates.")
    
    df.fillna("", inplace=True)
    
    df.to_excel(output_file, index=False)
    print("Merged and formatted successfully. Saved to:", output_file)

if __name__ == "__main__":
    merge_and_format_corvisiero()
