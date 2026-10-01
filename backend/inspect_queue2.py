import pandas as pd

try:
    df = pd.read_excel('Internal Copy of US_Licensing_Lifecycle_Tracker  (2).xlsx', sheet_name='Queue')
    print("Columns:", list(df.columns))
except Exception as e:
    print("Error:", e)
