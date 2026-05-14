import pandas as pd
import numpy as np
import os

file_path = r"E:\Internship\PocketFM\Knight Agency.xlsx"
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    total_books = len(df)
    
    # Check for both 'N/A' string and actual NaN values
    has_link = df['GoodReads series link'].apply(lambda x: str(x).strip() != 'N/A' and pd.notnull(x) and str(x).strip() != 'nan')
    
    with_links = has_link.sum()
    without_links = (~has_link).sum()
    
    print(f"Total Books: {total_books}")
    print(f"Books with Goodreads Links: {with_links}")
    print(f"Books without Goodreads Links (Missing): {without_links}")
else:
    print("File not found.")
