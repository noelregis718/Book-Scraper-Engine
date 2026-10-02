import pandas as pd
import json

jas_path = "e:/Internship/PocketFM/JAS Self-Pub Revenue Payouts (1).xlsx"
tracker_path = "e:/Internship/PocketFM/Internal Copy of US_Licensing_Lifecycle_Tracker  (2).xlsx"

def inspect_file(filepath):
    print(f"--- Inspecting {filepath} ---")
    try:
        xls = pd.ExcelFile(filepath)
        print("Sheet Names:", xls.sheet_names)
        
        # Print columns for each sheet to find the right ones
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, nrows=2)
            print(f"\nSheet: {sheet_name}")
            print(list(df.columns))
            
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

inspect_file(jas_path)
print("\n" + "="*50 + "\n")
inspect_file(tracker_path)
