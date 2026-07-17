import pandas as pd
import os
import re
import time
from duckduckgo_search import DDGS
from openpyxl import load_workbook
from openpyxl.styles import Alignment

def run_scraper():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(workspace_dir, "Small_Publishers_Crime_Scraped.xlsx")

    print(f"Loading input file: {input_path}")
    if not os.path.exists(input_path):
        print("Input file not found.")
        return

    df = pd.read_excel(input_path)
    ddgs = DDGS()
    
    for index, row in df.iterrows():
        title = str(row.get("Book 1 Title", "")).strip()
        author = str(row.get("Author Name", "")).strip()
        existing_pages = str(row.get("Number of Pages in Book 1", "")).strip()
        
        if not title or title.lower() == 'nan':
            continue
            
        if existing_pages and existing_pages.lower() != 'nan' and existing_pages != 'None':
            if re.match(r'^\d+$', existing_pages):
                continue
            
        print(f"\n[{index + 1}/{len(df)}] Searching for: '{title}' by '{author}'", flush=True)
        
        query = f'"{title}" {author} pages site:goodreads.com/book'
        try:
            results = list(ddgs.text(query, max_results=3))
            found_pages = None
            
            for res in results:
                body = res.get('body', '')
                # Often appears in the snippet like "300 pages, Paperback" or "Pages: 300"
                match = re.search(r'(\d+)\s*pages', body, re.IGNORECASE)
                if match:
                    found_pages = match.group(1)
                    break
                    
            if found_pages:
                df.at[index, "Number of Pages in Book 1"] = found_pages
                print(f"  [Success] Found {found_pages} pages from snippet.")
            else:
                print(f"  [Failed] Could not find page count in search snippets.")
                
        except Exception as e:
            print(f"  [Error] Failed: {e}")
            
        time.sleep(1) # Be nice to DDG
        df.to_excel(input_path, index=False)
        
    print(f"\nScraping complete. Final dataset saved to {input_path}")
    
    # Re-apply the fixed styling
    print("Re-applying premium fixed styles...")
    try:
        from apply_premium_style_crime import apply_premium_fixed_style
        apply_premium_fixed_style(input_path)
    except:
        pass

if __name__ == "__main__":
    run_scraper()
