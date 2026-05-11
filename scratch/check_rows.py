import pandas as pd
try:
    df = pd.read_excel(r"E:\Internship\PocketFM\Amazon Keyword - Dark Romance.xlsx")
    print(f"Total Rows: {len(df)}")
except Exception as e:
    print(e)
