import pandas as pd
import urllib.parse
import os
import time
from playwright.sync_api import sync_playwright

excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Next_Agency.xlsx')

def main():
    if not os.path.exists(excel_path):
        print(f"Excel file not found at {excel_path}")
        return

    df = pd.read_excel(excel_path)
    
    # Get first 10 book names
    books = df['Name of Series'].dropna().head(10).tolist()
    print(f"Searching for {len(books)} books on Goodreads...")
    
    with sync_playwright() as p:
        # Launch browser in headed mode so it's visible
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        pages = []
        for book in books:
            print(f"Opening tab for: {book}")
            page = context.new_page()
            query = urllib.parse.quote_plus(book)
            search_url = f"https://www.goodreads.com/search?q={query}"
            try:
                page.goto(search_url, timeout=0)
            except Exception as e:
                print(f"Error loading {search_url}: {e}")
            pages.append(page)
        
        print("All 10 tabs opened. You can now view them.")
        print("The browser will remain open until you close the window or stop the script.")
        
        # Keep the browser open until the user manually closes it or terminates the script
        try:
            while len(context.pages) > 0:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Closing browser...")
        
        browser.close()

if __name__ == "__main__":
    main()
