import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import os
import time

def clean_title_for_search(title):
    # Remove subtitles after colon
    clean = title.split(':')[0]
    # Remove "Book I", "Book II"
    clean = re.sub(r'Book [IVX]+', '', clean)
    clean = re.sub(r'The Years of Us', '', clean)
    clean = re.sub(r'Elizabeth\'s Story', '', clean)
    return clean.strip()

def search_duckduckgo(query):
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    data = {"q": query}
    try:
        r = requests.post(url, headers=headers, data=data, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all('a', class_='result__url'):
            link = a.get('href', '')
            # duckduckgo formats links as /l/?uddg=ENCODED_URL
            if 'goodreads.com/book/show' in link or 'goodreads.com' in a.text:
                actual_link = "https://" + a.text.strip()
                return actual_link
    except Exception as e:
        print(f"Error querying DDG: {e}")
    return None

def main():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Standard_11_Column_Format.xlsx')
    print(f"Loading {excel_path}...")
    df = pd.read_excel(excel_path)
    
    missing_mask = df['GoodReads series link'].isna() | (df['GoodReads series link'] == 'N/A') | (df['GoodReads series link'] == '')
    missing_indices = df.index[missing_mask].tolist()
    
    print(f"Found {len(missing_indices)} rows missing Goodreads links. Attempting fast DDG search...")
    
    found_count = 0
    for idx in missing_indices:
        raw_title = str(df.at[idx, 'Name of Series'])
        author = str(df.at[idx, 'Author Name']) if pd.notna(df.at[idx, 'Author Name']) else ""
        
        clean_title = clean_title_for_search(raw_title)
        query = f'site:goodreads.com/book/show/ "{clean_title}" {author}'.strip()
        
        print(f"\nSearching DDG for: {query}")
        link = search_duckduckgo(query)
        
        if link:
            # Ensure it is a clean link
            if not link.startswith('http'):
                link = 'https://' + link
            df.at[idx, 'GoodReads series link'] = link
            print(f"  -> Found: {link}")
            found_count += 1
        else:
            print(f"  -> Still could not find link for '{raw_title}'")
            
        time.sleep(2) # Prevent DDG rate limiting
        
    if found_count > 0:
        df.to_excel(excel_path, index=False)
        print(f"\nSuccessfully added {found_count} links and saved to Excel!")
    else:
        print("\nNo new links were found.")

if __name__ == '__main__':
    main()
