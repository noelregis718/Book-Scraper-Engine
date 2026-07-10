import pandas as pd
import time

excel_path = 'e:/Internship/PocketFM/Next_Agency.xlsx'
df = None

for i in range(10):
    try:
        df = pd.read_excel(excel_path)
        break
    except Exception as e:
        time.sleep(1)

if df is not None:
    total = len(df)
    processed = len(df[df['Romantasy = Yes or No?'].astype(str).str.strip().str.lower() == 'yes'])
    print(f'Processed: {processed} | Total: {total} | Left: {total - processed}')
else:
    print('Failed to read Excel file due to lock.')
