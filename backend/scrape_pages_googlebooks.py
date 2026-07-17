import pandas as pd
import os
import re
import requests
import time

def get_page_count_google_books(title, author):
    # Try strict
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title.replace(' ', '+')}+inauthor:{author.replace(' ', '+')}"
    try:
        r = requests.get(url)
        data = r.json()
        if 'items' in data:
            for item in data['items']:
                pc = item.get('volumeInfo', {}).get('pageCount')
                if pc: return pc
    except Exception as e:
        print(f"Error querying Google Books: {e}")
        
    # Try broad
    url = f"https://www.googleapis.com/books/v1/volumes?q={title.replace(' ', '+')}+{author.replace(' ', '+')}"
    try:
        r = requests.get(url)
        data = r.json()
        if 'items' in data:
            for item in data['items']:
                pc = item.get('volumeInfo', {}).get('pageCount')
                if pc: return pc
    except:
        pass
        
    return None

def run_scraper():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(workspace_dir, "Small_Publishers_Crime_Scraped.xlsx")

    print(f"Loading input file: {input_path}")
    if not os.path.exists(input_path):
        print("Input file not found.")
        return

    df = pd.read_excel(input_path)
    
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
        
        pages = get_page_count_google_books(title, author)
        
        if pages:
            df.at[index, "Number of Pages in Book 1"] = str(pages)
            print(f"  [Success] Found {pages} pages from Google Books.")
        else:
            print(f"  [Failed] Could not find page count.")
            
        time.sleep(0.5)
        df.to_excel(input_path, index=False)
        
    print(f"\nScraping complete. Final dataset saved to {input_path}")
    
    # Re-apply styling
    print("Re-applying premium fixed styles...")
    try:
        from apply_premium_style_crime import apply_premium_fixed_style
        apply_premium_fixed_style(input_path)
    except:
        pass

if __name__ == "__main__":
    run_scraper()
