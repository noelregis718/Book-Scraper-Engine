import pandas as pd
df = pd.read_excel('All-Genre Licensing Tracker.xlsx', sheet_name='Romantasy v2', header=1)
df['S. No.'] = pd.to_numeric(df['S. No.'], errors='coerce')
df = df[(df['S. No.'] >= 233) & (df['S. No.'] <= 303)]

cols = ['GR Book 1 link', 'Agency (if)', 'GR Series Link', 'No. of books in the series', 'Page count']
missing_rows = []

for idx, row in df.iterrows():
    missing = []
    if pd.isna(row['GR Book 1 link']) or str(row['GR Book 1 link']).strip() == '' or str(row['GR Book 1 link']).strip() == 'nan':
        missing.append('GR Book 1 link')
    if pd.isna(row['Agency (if)']) or str(row['Agency (if)']).strip() == '' or str(row['Agency (if)']).strip() == 'nan':
        missing.append('Agency (if)')
    if pd.isna(row['GR Series Link']) or str(row['GR Series Link']).strip() == '' or str(row['GR Series Link']).strip() == 'nan':
        missing.append('GR Series Link')
    if pd.isna(row['No. of books in the series']) or row['No. of books in the series'] in [0, '0', 0.0]:
        missing.append('No. of books in the series')
    if pd.isna(row['Page count']) or row['Page count'] in [0, '0', 0.0]:
        missing.append('Page count')
        
    if missing:
        missing_rows.append({'S. No.': row['S. No.'], 'Title': row['Title'], 'Missing': ', '.join(missing)})

print(f'Found {len(missing_rows)} rows with missing details.')
for m in missing_rows:
    print(f"S. No. {m['S. No.']}: {m['Title']} -> Missing: {m['Missing']}")
