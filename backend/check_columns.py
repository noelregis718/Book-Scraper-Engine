import pandas as pd

try:
    df_raw = pd.read_excel('Next_Agency_backup.xlsx', header=0)
    print("Original Column names:")
    print(df_raw.columns.tolist())
except Exception as e:
    print(e)
