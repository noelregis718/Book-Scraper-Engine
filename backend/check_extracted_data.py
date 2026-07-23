import pandas as pd
df = pd.read_excel(r"e:\Internship\PocketFM\Romantasy_v2_extracted.xlsx", header=1)
for index, row in df.head(10).iterrows():
    book1_link = row.get('GR Book 1 link', '')
    series_link = row.get('GR Series Link', '')
    num_books = row.get('No. of books in the series', pd.NA)
    page_count = row.get('Page count', pd.NA)
    print(f"Row {index}:")
    print(f"  Book 1: {book1_link}")
    print(f"  Series: {series_link}")
    print(f"  Num books: {num_books}")
    print(f"  Page count: {page_count}")
