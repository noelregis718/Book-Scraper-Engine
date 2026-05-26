import pandas as pd
import sys

xls = pd.ExcelFile(r'E:\Internship\PocketFM\Triada_Upcoming_Books (2).xlsx')
for sheet in xls.sheet_names:
    print(f"--- {sheet} ---")
    df = pd.read_excel(xls, sheet_name=sheet, head=None)
    # Print first 15 rows to see where the headers are
    print(df.head(15).to_string())
    print("\n")
