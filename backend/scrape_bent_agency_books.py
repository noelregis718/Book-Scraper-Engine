import asyncio
import os
import sys
import pandas as pd
import re
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\bent_agency_authors.xlsx"

def normalize_title(title):
    if pd.isna(title) or not title:
        return ""
    t = str(title).lower()
    t = re.sub(r'[^\w\s]', '', t)
    return t.strip()

async def process_book(context, scraper, title, author, link):
    safe_title = title.encode('ascii', 'ignore').decode('ascii') if title else 'Unknown'
    safe_author = author.encode('ascii', 'ignore').decode('ascii') if author else 'Unknown'
    print(f"    [Scraping Book] '{safe_title}' by {safe_author}...")
    
    row_data = {
        "Name of Series": title,
        "Author Name": author,
        "Publisher": "",
        "GoodReads series link": "",
        "Number of PRIMARY books in the series": 1,
        "Rating (out of 5) of Primary Book 1": "N/A",
        "Ratings (#) of Primary Book 1": "N/A",
        "Synopsis (if available)": "N/A",
        "Romantasy = Yes or No?": "No",
        "Romantasy Sub-Genre of series": "",
        "Name of agent": "The Bent Agency"
    }
    
    try:
        data = await scraper.scrape_goodreads_data(context, title, author, existing_url=link)
        if data:
            link = data.get('GoodReads_Series_URL')
            if not link or link == 'N/A':
                link = data.get('GoodReads_Book_URL', 'N/A')
            if link == 'N/A': link = ''
                
            row_data['GoodReads series link'] = link
            row_data['Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
            
            rating = data.get('Book1_Rating', 'N/A')
            if rating == 'N/A': rating = data.get('GoodReads_Rating', 'N/A')
            row_data['Rating (out of 5) of Primary Book 1'] = rating
            
            count = data.get('Book1_Num_Ratings', 'N/A')
            if count == 'N/A': count = data.get('GoodReads_Rating_Count', 'N/A')
            row_data['Ratings (#) of Primary Book 1'] = count
            
            row_data['Synopsis (if available)'] = data.get('Description', 'N/A')
            row_data['Romantasy = Yes or No?'] = data.get('Romantasy_Subgenre', 'No')
            row_data['Romantasy Sub-Genre of series'] = data.get('Sub_Genre', '')
            
            print(f"    [Done] '{safe_title}'")
        else:
            print(f"    [Not Found] '{safe_title}'")
    except Exception as e:
        err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"    [Error] '{safe_title}': {err_msg}")
        
    return row_data

async def search_author_and_get_books(author, df, context, scraper):
    safe_author = author.encode('ascii', 'ignore').decode('ascii')
    print(f"  [Author Search] {safe_author}")
    search_page = await context.new_page()
    try:
        top_books = await scraper.search_author_books_with_links(search_page, author, max_books=3)
    finally:
        await search_page.close()
        
    books_to_scrape = []
    if top_books:
        existing_titles = df[df['Author Name'] == author]['Name of Series'].apply(normalize_title).tolist()
        for book in top_books:
            found_title = book['title']
            norm_found = normalize_title(found_title)
            
            exists = False
            for ex in existing_titles:
                if not ex or not norm_found: continue
                if ex in norm_found or norm_found in ex:
                    exists = True
                    break
                    
            if not exists:
                books_to_scrape.append({'title': found_title, 'author': author, 'link': book['link']})
            else:
                print(f"    [Skipping] '{found_title.encode('ascii', 'ignore').decode('ascii')}' - Already in sheet")
                
    return books_to_scrape

async def run_scrape():
    df = pd.read_excel(EXCEL_FILE)
    
    authors = df['Author Name'].dropna().unique()
    all_authors = [a for a in authors if str(a).strip() != '']
    
    # Only process authors who have 1 row (meaning they haven't been scraped successfully yet)
    # This prevents re-searching authors we already finished!
    counts = df['Author Name'].value_counts()
    processed_authors = set(counts[counts > 1].index)
    
    authors = [a for a in all_authors if a not in processed_authors]
    print(f"Found {len(all_authors)} unique authors. Skipping {len(processed_authors)} already processed. {len(authors)} remaining to scrape.")
    
    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        login_page = await context.new_page()
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        await login_page.close()
        
        # Process in chunks of 2 authors
        chunk_size = 2
        for i in range(0, len(authors), chunk_size):
            author_chunk = authors[i:i+chunk_size]
            print(f"\n--- Processing Batch {i//chunk_size + 1}: {[a.encode('ascii', 'ignore').decode('ascii') for a in author_chunk]} ---")
            
            search_tasks = [search_author_and_get_books(a, df, context, scraper) for a in author_chunk]
            search_results = await asyncio.gather(*search_tasks)
            
            books_to_scrape = []
            for res in search_results:
                books_to_scrape.extend(res)
                
            if not books_to_scrape:
                print("  No new books to scrape in this batch.")
                continue
                
            print(f"  Scraping {len(books_to_scrape)} books for this batch concurrently...")
            scrape_tasks = [process_book(context, scraper, b['title'], b['author'], b['link']) for b in books_to_scrape]
            scraped_rows = await asyncio.gather(*scrape_tasks)
            
            # Reload df to ensure we don't lose data if we run multiple instances or someone edits
            df = pd.read_excel(EXCEL_FILE)
            new_df = pd.DataFrame(scraped_rows)
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_excel(EXCEL_FILE, index=False)
            print(f"  Batch saved to Excel.")
            
        await browser.close()
        
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
    except: pass
    
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
