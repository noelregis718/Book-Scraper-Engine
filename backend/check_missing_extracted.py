import pandas as pd
import numpy as np

file_path = r"e:\Internship\PocketFM\Romantasy_v2_extracted.xlsx"
df = pd.read_excel(file_path, header=0)

missing_count = 0
for index, row in df.iterrows():
    book1_link = str(row.get('GR Book 1 link', '')).strip()
    series_link = str(row.get('GR Series Link', '')).strip()
    num_books = row.get('No. of books in the series', pd.NA)
    page_count = row.get('Page count', pd.NA)
    
    is_missing_books = pd.isna(num_books) or str(num_books).strip() == '' or str(num_books).strip().lower() == 'nan'
    is_missing_pages = pd.isna(page_count) or str(page_count).strip() == '' or str(page_count).strip().lower() == 'nan'
    is_missing_series = series_link == '' or series_link.lower() == 'nan' or 'missing' in series_link.lower()
    
    if is_missing_series or is_missing_books or is_missing_pages or book1_link == '' or book1_link.lower() == 'nan':
        missing_count += 1
        # print(f"Row {index+2} missing data. Title: {row.get('Title')}")
        
print(f"Total rows still missing data: {missing_count} out of {len(df)}")
