import pandas as pd
import os

INPUT_FILE = r"E:\Internship\PocketFM\Amazon Keyword - Vampire.xlsx"
if os.path.exists(INPUT_FILE):
    df = pd.read_excel(INPUT_FILE)
    START_ROW = 2500
    END_ROW = 3500
    range_mask = (df.index >= (START_ROW - 2)) & (df.index <= (END_ROW - 2))
    subset = df.loc[range_mask]
    
    def needs_repair(val):
        if pd.isna(val): return True
        s = str(val).strip().lower()
        if s in ["", "n/a", "nan"]: return True
        if "inr" in s or "₹" in s: return True
        if "$" not in s: return True
        return False

    to_repair = subset[subset['Price_Tier'].apply(needs_repair)]
    print(f"Total rows in range: {len(subset)}")
    print(f"Rows needing repair: {len(to_repair)}")
    if len(to_repair) > 0:
        print("Sample broken prices:")
        print(to_repair['Price_Tier'].head(5))
else:
    print("File not found")
