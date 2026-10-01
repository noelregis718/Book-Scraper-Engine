import pandas as pd

try:
    df = pd.read_excel('Internal Copy of US_Licensing_Lifecycle_Tracker  (2).xlsx', sheet_name='Queue')
    print("Columns:")
    for col in df.columns:
        print(f" - {col}")
    print("\nFirst 3 rows:")
    print(df.head(3).to_string())
except Exception as e:
    print("Error:", e)
