import pandas as pd
import os

file_path = 'Agency Crawls.xlsx'
if os.path.exists(file_path):
    xls = pd.ExcelFile(file_path)
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        # Search for 'Plinkington', 'Pilkington', 'Pillington'
        for term in ['Plinkington', 'Pilkington', 'Pillington']:
            mask = df.apply(lambda row: row.astype(str).str.contains(term, case=False).any(), axis=1)
            if mask.any():
                print(f"Found '{term}' in sheet '{sheet_name}'")
else:
    print(f"File {file_path} not found")
