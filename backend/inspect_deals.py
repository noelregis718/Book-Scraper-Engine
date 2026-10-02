import pandas as pd

filepath = "e:/Internship/PocketFM/JAS Self-Pub Revenue Payouts (1).xlsx"
print(f"--- Inspecting {filepath} ---")
try:
    # Read the first few rows to find the actual header
    df = pd.read_excel(filepath, sheet_name='US Lifecycle Deals', header=None, nrows=10)
    print("Top 10 rows of 'US Lifecycle Deals':")
    print(df.to_string())
    
    df2 = pd.read_excel(filepath, sheet_name='Calculations formats (reference', header=None, nrows=10)
    print("\nTop 10 rows of 'Calculations formats':")
    print(df2.to_string())
    
except Exception as e:
    print(f"Error: {e}")
