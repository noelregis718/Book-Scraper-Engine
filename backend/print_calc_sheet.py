import pandas as pd

filepath = "e:/Internship/PocketFM/JAS Self-Pub Revenue Payouts (1).xlsx"
print(f"--- Inspecting {filepath} ---")
try:
    df = pd.read_excel(filepath, sheet_name='Calculations formats (reference', header=None)
    for index, row in df.iterrows():
        # filter out rows that are entirely NaN
        if not row.isnull().all():
            print(f"Row {index}: {row.dropna().to_dict()}")
except Exception as e:
    print(f"Error: {e}")
