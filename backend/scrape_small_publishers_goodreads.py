import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import sys
import os

# Add current directory to path to import GoodreadsScraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

async def run_scraper():
    # 1. Load CSV data
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(workspace_dir, 'Small & Mid Sized Publishers - Sheet5.csv')
    
    print(f"Loading CSV file: {csv_path}")
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    
    # 2. Extract authors from "Top books / authors" column
    authors_set = set()
    publisher_mapping = {} # To keep track of which publisher an author belongs to
    
    if 'Top books / authors' in df.columns:
        for idx, row in df.iterrows():
            top_info = str(row['Top books / authors'])
            publisher = str(row.get('Publisher name', 'Unknown'))
            if top_info.lower() not in ['nan', 'none', '']:
                # Assume comma-separated author names based on our inspection
                names = [name.strip() for name in top_info.split(',')]
                for name in names:
                    if name:
                        authors_set.add(name)
                        publisher_mapping[name] = publisher
    else:
        print("Column 'Top books / authors' not found in CSV.")
        return

    authors = list(authors_set)
    print(f"Found {len(authors)} unique authors to scrape.")
    if not authors:
        return

    # Output file path
    output_excel_path = os.path.join(workspace_dir, 'Small_Publishers_Books.xlsx')
    
    # Check if we already have partial progress
    if os.path.exists(output_excel_path):
        out_df = pd.read_excel(output_excel_path)
        existing_titles = [str(t).lower().strip() for t in out_df['Name of Series'].dropna().tolist()]
        new_rows = out_df.to_dict('records')
        print(f"Loaded {len(new_rows)} existing records from {output_excel_path}.")
    else:
        existing_titles = []
        new_rows = []
    
    scraper = GoodreadsScraper(headless=True) # running headless for stability
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Login
        await scraper.login_to_goodreads(page)
        
        for idx, author in enumerate(authors):
            print(f"\n[{idx + 1}/{len(authors)}] Processing Author: {author}")
            publisher = publisher_mapping.get(author, 'Unknown')
            
            try:
                # Search author and get top 3 books
                top_books = await scraper.search_author_books_with_links(page, author, max_books=3)
                
                if not top_books:
                    print(f"  -> Could not find books for {author}.")
                    continue
                    
                print(f"  -> Found {len(top_books)} books for {author}. Extracting details...")
                
                for book in top_books:
                    title = book['title']
                    link = book['link']
                    
                    if title.lower().strip() in existing_titles:
                        print(f"  -> Skipping '{title}' (already in output).")
                        continue
                        
                    print(f"    - Scraping details for: {title}")
                    
                    # Get detailed info
                    data = await scraper.scrape_goodreads_data(context, title=title, author=author, existing_url=link)
                    
                    if data:
                        new_row = {
                            'Name of Series': title,
                            'Author Name': author,
                            'Publisher': publisher,
                            'GoodReads series link': data.get("GoodReads_Book_URL", link),
                            'Number of PRIMARY books in the series': data.get("Num_Primary_Books", "N/A"),
                            'Rating (out of 5) of Primary Book 1': data.get("Book1_Rating", "N/A"),
                            'Ratings (#) of Primary Book 1': data.get("Book1_Num_Ratings", "N/A"),
                            'Synopsis (if available)': data.get("Description", "N/A"),
                            'Romantasy = Yes or No?': "N/A",
                            'Romantasy Sub-Genre of series': data.get("Romantasy_Subgenre", "N/A"),
                            'Name of agent': "N/A"
                        }
                        new_rows.append(new_row)
                        existing_titles.append(title.lower().strip())
                        print(f"      [Success] Added '{title}' to queue.")
                    else:
                        print(f"      [Failed] Could not extract details for '{title}'.")
                        
            except Exception as e:
                print(f"  -> Error processing author {author}: {e}")
                
            # Auto-save after each author
            if len(new_rows) > 0:
                temp_df = pd.DataFrame(new_rows)
                temp_df.to_excel(output_excel_path, index=False)
                print(f"  [Auto-Save] Progress saved. Total rows: {len(temp_df)}")
                
        await browser.close()
        
    print(f"\nScraping complete. Final dataset saved to {output_excel_path}")

if __name__ == "__main__":
    asyncio.run(run_scraper())
