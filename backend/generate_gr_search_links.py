import pandas as pd
import urllib.parse
import re

excel_path = r"e:\Internship\PocketFM\Books_Scraping_Template.xlsx"
df = pd.read_excel(excel_path, engine='openpyxl')

missing_mask = df['GoodReads series link'].isna() | (df['GoodReads series link'] == 'N/A') | (df['GoodReads series link'] == '') | (~df['GoodReads series link'].astype(str).str.startswith('http'))

count = 0
for index, row in df[missing_mask].iterrows():
    title = str(row['Name of Series']) if pd.notna(row['Name of Series']) else ''
    author = str(row['Author Name']) if pd.notna(row['Author Name']) else ''
    
    # Clean up the string to remove weird characters
    clean_title = re.sub(r'[^\w\s]', '', title).strip()
    clean_author = re.sub(r'[^\w\s]', '', author).strip()
    
    if clean_title:
        # Create a direct search link on Goodreads
        query = f"{clean_title} {clean_author}".strip()
        encoded_query = urllib.parse.quote_plus(query)
        search_link = f"https://www.goodreads.com/search?q={encoded_query}"
        
        df.at[index, 'GoodReads series link'] = search_link
        count += 1

print(f"Instantly generated direct Goodreads search links for {count} books.")
print("Saving to Excel...")
df.to_excel(excel_path, index=False, engine='openpyxl')
print("Done!")
