import pandas as pd
import os

FILE_PATH = r"E:\Internship\PocketFM\awful agents.xlsx"

if os.path.exists(FILE_PATH):
    df = pd.read_excel(FILE_PATH)
    # Check for NaN, "N/A", or empty strings
    mask = df["GoodReads series link"].astype(str).str.lower().isin(["nan", "n/a", "", "none"])
    missing_count = mask.sum()
    print(f"Total Rows: {len(df)}")
    print(f"Rows missing Goodreads link: {missing_count}")
else:
    print("File not found.")
