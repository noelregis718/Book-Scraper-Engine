import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import urllib.parse
import sys

EXCEL_FILE = sys.argv[1] if len(sys.argv) > 1 else "e:/Internship/PocketFM/park_and_fine_books.xlsx"

async def scrape_book(context, df, index, title, author):
    page = await context.new_page()
    try:
        # If title is empty, we just search the author name
        query = f"{title} {author}".strip()
        print(f"[{index}] Searching DuckDuckGo for: {query}")
        
        # We go directly to DuckDuckGo to find the goodreads book page
        ddg_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query + ' site:goodreads.com/book/show')}"
        await page.goto(ddg_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(2)
        
        ddg_links = await page.query_selector_all('a.result__url')
        if not ddg_links:
            print(f"[{index}] No search results found anywhere for {query}")
            df.at[index, 'Rating (out of 5) of Primary Book 1'] = 0.0
            await page.close()
            return
            
        href = await ddg_links[0].get_attribute('href')
        if 'uddg=' in href:
            actual_url = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
            print(f"[{index}] Found via DDG! Going to: {actual_url}")
            await page.goto(actual_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(3)
        else:
            print(f"[{index}] DDG returned unparseable link.")
            df.at[index, 'Rating (out of 5) of Primary Book 1'] = 0.0
            await page.close()
            return
            
        # We are now on the book page
        book_title_elem = await page.query_selector('h1[data-testid="bookTitle"]')
        book_title = await book_title_elem.inner_text() if book_title_elem else ""
        
        rating_elem = await page.query_selector('div.RatingStatistics__rating')
        rating = await rating_elem.inner_text() if rating_elem else ""
        
        ratings_count_elem = await page.query_selector('div.RatingStatistics__meta [data-testid="ratingsCount"]')
        ratings_count = await ratings_count_elem.inner_text() if ratings_count_elem else ""
        ratings_count = ratings_count.replace("ratings", "").replace(",", "").replace("rating", "").strip()
        
        synopsis_elem = await page.query_selector('div.DetailsLayoutRightParagraph__widthConstrained span.Formatted')
        if not synopsis_elem:
            synopsis_elem = await page.query_selector('div[data-testid="description"]')
        synopsis = await synopsis_elem.inner_text() if synopsis_elem else ""
        
        # Save the scraped book title if it was missing
        if not title and book_title:
            df.at[index, 'Name of Series'] = book_title
            
        # We always want the Goodreads book link, so we'll store the page.url!
        df.at[index, 'GoodReads series link'] = page.url
        
        print(f"[{index}] Found Book: {book_title}, Rating: {rating}, Count: {ratings_count}")
        
        # Safely convert to numeric types for Pandas
        try:
            rating_val = float(rating) if rating else None
        except:
            rating_val = None
            
        try:
            count_val = int(ratings_count) if ratings_count else None
        except:
            count_val = None
        
        df.at[index, 'Rating (out of 5) of Primary Book 1'] = rating_val
        df.at[index, 'Ratings (#) of Primary Book 1'] = count_val
        df.at[index, 'Synopsis (if available)'] = str(synopsis)
                    
    except Exception as e:
        print(f"[{index}] Error scraping {query}: {e}")
        df.at[index, 'Rating (out of 5) of Primary Book 1'] = 0.0
        
    finally:
        await page.close()

async def scrape_goodreads():
    df = pd.read_excel(EXCEL_FILE)
    
    # Ensure columns are object type so we can insert strings if needed
    for col in ['Name of Series', 'Synopsis (if available)', 'GoodReads series link', 'Number of PRIMARY books in the series', 'Rating (out of 5) of Primary Book 1', 'Ratings (#) of Primary Book 1']:
        if col in df.columns and df[col].dtype != 'object':
            df[col] = df[col].astype('object')
            
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        while True:
            books_to_scrape = []
            for index, row in df.iterrows():
                # Check if already scraped
                if pd.notna(row.get('Rating (out of 5) of Primary Book 1')) and str(row.get('Rating (out of 5) of Primary Book 1')).strip() != "":
                    continue
                    
                title = "" if pd.isna(row.get('Name of Series')) else str(row.get('Name of Series')).strip()
                author = "" if pd.isna(row.get('Author Name')) else str(row.get('Author Name')).strip()
                
                if not title and not author:
                    continue
                
                books_to_scrape.append((index, title, author))
                
                if len(books_to_scrape) == 6:
                    break
                    
            if not books_to_scrape:
                print("No more books to scrape!")
                break
                
            print(f"\n--- Starting new batch of {len(books_to_scrape)} books concurrently ---")
            tasks = []
            for index, title, author in books_to_scrape:
                tasks.append(scrape_book(context, df, index, title, author))
                
            await asyncio.gather(*tasks)
            
            df.to_excel(EXCEL_FILE, index=False)
            print("Batch complete and saved to Excel!")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_goodreads())
