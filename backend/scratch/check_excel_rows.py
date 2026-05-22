import pandas as pd
import os

file_path = r"E:\Internship\PocketFM\Amazon Keyword - Paranormal Romance.xlsx"
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    print(f"Total Rows: {len(df)}")
    print(f"Unique Titles: {df['Book Title'].nunique()}")
else:
    print("File not found")
