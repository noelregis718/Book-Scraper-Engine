import pandas as pd
import requests
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from format_madwoman import format_madwoman

EXCEL_FILE = r"e:\Internship\PocketFM\madeleine_milburn_combined.xlsx"
MAX_ROWS = 106

def get_author_from_openlibrary(title):
    try:
        url = f"https://openlibrary.org/search.json?title={requests.utils.quote(title)}&limit=1"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            docs = data.get('docs', [])
            if docs:
                authors = docs[0].get('author_name', [])
                if authors:
                    return authors[0]
    except Exception as e:
        print(f"  [API Error] {title}: {e}")
    return None

def main():
    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    updates = 0
    
    print(f"--- Fast API Search for Authors (First {MAX_ROWS} rows) ---")
    for idx in range(min(MAX_ROWS, len(df))):
        title = str(df.at[idx, 'Name of Series']).strip()
        author = str(df.at[idx, 'Author Name']).strip()
        
        if (not author or author.lower() == 'nan') and title and title.lower() != 'nan':
            # Use OpenLibrary API
            found_author = get_author_from_openlibrary(title)
            
            if found_author:
                df.at[idx, 'Author Name'] = found_author
                print(f"  [Found] {title} -> {found_author}")
                updates += 1
            else:
                print(f"  [Not Found] {title}")
                
            time.sleep(0.5) # Be gentle on the free API
            
    if updates > 0:
        print(f"--- Saving Excel ({updates} authors found) ---")
        df.to_excel(EXCEL_FILE, index=False)
        format_madwoman(EXCEL_FILE, EXCEL_FILE)
        
        # Copy to downloads aggressively
        os.system(r'powershell -Command "Copy-Item e:\Internship\PocketFM\madeleine_milburn_combined.xlsx -Destination C:\Users\noelr\Downloads\madeleine_milburn_combined.xlsx -Force"')
        print("ALL DONE!")
    else:
        print("No new authors found or needed.")

if __name__ == "__main__":
    main()
