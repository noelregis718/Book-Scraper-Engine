import pandas as pd
import os

catalog_path = r"E:\Internship\PocketFM\Seymour_Media_Catalog.xlsx"
if os.path.exists(catalog_path):
    df = pd.read_excel(catalog_path)
    print(f"Total Rows in spreadsheet: {len(df)}")
    
    # We want rows where Name of Series is empty/nan/N/A, and Goodreads series link is not a valid URL
    # Let's clean the checks
    df['Name of Series_str'] = df['Name of Series'].astype(str).str.strip()
    df['GoodReads series link_str'] = df['GoodReads series link'].astype(str).str.strip()
    
    missing_book_rows = df[
        (df['Name of Series'].isna() | (df['Name of Series_str'] == "") | (df['Name of Series_str'] == "nan") | (df['Name of Series_str'] == "N/A")) &
        (df['Author Name'].notna() & (df['Author Name'].astype(str).str.strip() != "") & (df['Author Name'].astype(str).str.strip() != "nan")) &
        (df['GoodReads series link'].isna() | (df['GoodReads series link_str'] == "") | (df['GoodReads series link_str'] == "nan") | (df['GoodReads series link_str'] == "N/A") | (~df['GoodReads series link_str'].str.startswith("http")))
    ]
    
    print(f"Total rows with missing book names and no Goodreads links: {len(missing_book_rows)}")
    if len(missing_book_rows) > 0:
        print("First 20 matching rows:")
        for idx in missing_book_rows.index[:20]:
            print(f"Row {idx+2}: Author='{df.loc[idx, 'Author Name']}', Book='{df.loc[idx, 'Name of Series']}', Goodreads='{df.loc[idx, 'GoodReads series link']}'")
    else:
        print("No matching rows found!")
else:
    print("Catalog not found")
