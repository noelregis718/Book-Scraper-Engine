import asyncio
import pandas as pd
import sys
import os
import urllib.parse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from apply_jra_style import apply_styling
except ImportError:
    def apply_styling(p): pass

EXCEL_FILE = r'E:\Internship\PocketFM\dragonblade_books_combined.xlsx'

async def scrape_book(context, title, author):
    page = await context.new_page()
    try:
        # Search Goodreads with both title and author
        query_str = f"{title} {author}".replace('nan', '').strip()
        query = urllib.parse.quote_plus(query_str)
        await page.goto(f"https://www.goodreads.com/search?q={query}")
        await page.wait_for_timeout(2000)
        
        first_result = await page.query_selector('.tableList tr td a.bookTitle')
        if not first_result:
            return "N/A", "N/A", "N/A", "N/A"
            
        href = await first_result.get_attribute("href")
        book_url = f"https://www.goodreads.com{href}" if href.startswith('/') else href
        book_url = book_url.split('?')[0] # Clean the URL
        
        await page.goto(book_url)
        await page.wait_for_timeout(2000)
        
        # Scrape page
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        rating_elem = soup.select_one('div.RatingStatistics__rating')
        rating = rating_elem.text.strip() if rating_elem else "N/A"
        
        count_elem = soup.select_one('div.RatingStatistics__meta span[data-testid="ratingsCount"]')
        count = count_elem.text.strip().replace('ratings', '').replace('rating', '').replace(',', '').strip() if count_elem else "N/A"
        
        synopsis_elem = soup.select_one('div.DetailsLayoutRightParagraph__widthConstrained span.Formatted')
        synopsis = synopsis_elem.text.strip() if synopsis_elem else "N/A"
        
        return book_url, rating, count, synopsis
    except Exception as e:
        print(f"Error for {title}: {e}")
        return "N/A", "N/A", "N/A", "N/A"
    finally:
        await page.close()

async def worker(context, queue, df, lock):
    while True:
        item = await queue.get()
        if item is None:
            break
            
        index, title, author = item
        print(f"[{index}] Searching: '{title} {author}'")
        
        url, rating, count, syn = await scrape_book(context, title, author)
        
        async with lock:
            df.at[index, "GoodReads series link"] = url
            df.at[index, "Rating (out of 5) of Primary Book 1"] = rating
            df.at[index, "Ratings (#) of Primary Book 1"] = count
            df.at[index, "Synopsis (if available)"] = syn
            
            try:
                df.to_excel(EXCEL_FILE, index=False)
            except Exception as e:
                print(f"Save error on index {index}: {e}")
            
        print(f"[{index}] Done: '{title}'")
        queue.task_done()

async def main():
    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    missing = df[df["GoodReads series link"].isna() | (df["GoodReads series link"] == '') | (df["GoodReads series link"].astype(str) == 'nan')]
    if missing.empty:
        print("All books already scraped!")
        return

    print(f"Found {len(missing)} books to scrape.")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        queue = asyncio.Queue()
        for idx, row in missing.iterrows():
            title = str(row.get("Name of Series", "")).strip()
            author = str(row.get("Author Name", "")).strip()
            
            if title and title != "nan":
                await queue.put((idx, title, author))
                
        lock = asyncio.Lock()
        
        workers = []
        for _ in range(10): # 10 aggressive tabs
            workers.append(asyncio.create_task(worker(context, queue, df, lock)))
            
        await queue.join()
        
        for _ in range(10):
            await queue.put(None)
        await asyncio.gather(*workers)
        
        await browser.close()
        
    print("Scraping complete!")
    try:
        apply_styling(EXCEL_FILE)
        print("Styling reapplied.")
    except Exception as e:
        print(f"Styling error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
