import pandas as pd
df = pd.read_excel(r"e:\Internship\PocketFM\Romantasy_v2_Scraped.xlsx")
missing = 0
for index, row in df.iterrows():
    num_books = row.get('No. of books in the series', pd.NA)
    page_count = row.get('Page count', pd.NA)
    is_missing = pd.isna(num_books) or str(num_books).strip() == '' or str(num_books).strip().lower() == 'nan'
    if is_missing:
        missing += 1

print(f"Remaining missing rows: {missing} out of {len(df)}")
