import pandas as pd
import os

file_path = r"E:\Internship\PocketFM\Knight Agency.xlsx"
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    print("Last 10 entries:")
    print(df[['Name of Series', 'Author Name', 'GoodReads series link']].tail(10))
else:
    print("File not found.")
