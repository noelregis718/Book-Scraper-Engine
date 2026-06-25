import pandas as pd

files = [
    "e:/Internship/PocketFM/LDLA_Author_Books.xlsx",
    "e:/Internship/PocketFM/LDLA_Books_and_Authors.xlsx",
    "e:/Internship/PocketFM/Laura_Dail_Agency_Books.xlsx"
]

for f in files:
    try:
        df = pd.read_excel(f, nrows=5)
        print(f"\nFile: {f.split('/')[-1]}")
        print("Columns:", df.columns.tolist())
    except Exception as e:
        print(f"Error reading {f}: {e}")
