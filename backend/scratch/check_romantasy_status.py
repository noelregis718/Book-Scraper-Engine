import pandas as pd
import os

file_path = r"E:\Internship\PocketFM\Amazon Keyword - Romantasy.xlsx"
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    print(f"Total Rows: {len(df)}")
    if 'Book Title' in df.columns:
        print(f"Last Title: {df['Book Title'].iloc[-1]}")
else:
    print("File not found")
