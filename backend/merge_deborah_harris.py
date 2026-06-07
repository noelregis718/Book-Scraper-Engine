import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def merge_and_format():
    file1 = r'E:\Internship\PocketFM\deborah_harris_fiction_books_authors.xlsx'
    file2 = r'E:\Internship\PocketFM\deborah_harris_young_adult_complete.xlsx'
    out_file = r'E:\Internship\PocketFM\deborah_harris_merged.xlsx'
    
    print("Reading files...")
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)
    
    # Standardize column names
    df1 = df1.rename(columns={'Book Name': 'Name of Series'})
    df2 = df2.rename(columns={'Book Name': 'Name of Series'})
    
    print("Merging and dropping duplicates...")
    df = pd.concat([df1, df2], ignore_index=True)
    df = df.drop_duplicates()
    
    # 11 Column Structure
    requested_columns = [
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
    
    for col in requested_columns:
        if col not in df.columns:
            df[col] = ""
            
    df = df[requested_columns]
    
    print(f"Saving to {out_file}...")
    df.to_excel(out_file, index=False)
    
    try:
        from style_books_authors import apply_styling
        apply_styling(out_file)
    except Exception as e:
        print(f"Failed to style: {e}")

if __name__ == "__main__":
    merge_and_format()
