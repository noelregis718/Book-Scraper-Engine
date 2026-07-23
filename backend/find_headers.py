import pandas as pd

df = pd.read_excel(r"e:\Internship\PocketFM\All-Genre Licensing Tracker.xlsx", sheet_name="Romantasy v2", header=None)

for i in range(10):
    print(f"Row {i+1}:")
    print(df.iloc[i].dropna().tolist()[:10])
    print("-" * 20)
