import pandas as pd
df = pd.read_excel('E:/Internship/PocketFM/Stonesong_Books.xlsx')
authors = [a for a in df['Author Name'].dropna().unique() if str(a).strip().lower() not in ['', 'nan', 'unknown', '[author name to be fetched]']]
print(f"Total: {len(authors)}, Christo is at index: {authors.index('Christo') if 'Christo' in authors else 'Not found'}")
