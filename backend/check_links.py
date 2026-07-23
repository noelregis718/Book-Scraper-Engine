import pandas as pd
df = pd.read_excel(r"e:\Internship\PocketFM\Romantasy_v2_Scraped.xlsx")
missing_both = 0
for index, row in df.iterrows():
    b1 = str(row.get('GR Book 1 link', '')).strip()
    series = str(row.get('GR Series Link', '')).strip()
    num_books = row.get('No. of books in the series', pd.NA)
    is_missing_books = pd.isna(num_books) or str(num_books).strip() == '' or str(num_books).strip().lower() == 'nan'
    if is_missing_books:
        if not b1.startswith('http') and not series.startswith('http'):
            missing_both += 1

print(f"Rows missing both links: {missing_both}")
