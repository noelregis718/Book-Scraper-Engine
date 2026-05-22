import pandas as pd
import os

file_path = r'E:\Internship\PocketFM\Amazon Keyword - paranormal Romance.xlsx'
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    print(f"Total Rows: {len(df)}")
    print("Last 2 rows:")
    print(df[['Book Title', 'Amazon URL']].tail(2))
else:
    print("File not found")
