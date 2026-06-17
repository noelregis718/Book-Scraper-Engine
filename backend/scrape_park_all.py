import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import urllib.parse
import sys

EXCEL_FILE = sys.argv[1] if len(sys.argv) > 1 else "e:/Internship/PocketFM/park_and_fine_books.xlsx"

async def scrape_book(context, df, index, title, author):
    page = await context.new_page()
    try:
        query = f"{title} {author}".strip()
        print(f"[{index}] Searching Goodreads directly for: {query}")
        
        search_url = f"https://www.goodreads.com/search?q={urllib.parse.quote_plus(query)}"
        await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(3)
        
        results = await page.query_selector_all('a.bookTitle')
        if not results:
            # Fallback to DuckDuckGo
            print(f"[{index}] No search results on Goodreads. Falling back to DuckDuckGo for: {query}")
            ddg_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query + ' site:goodreads.com/book/show')}"
            await page.goto(ddg_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(3)
            
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
        else:
            first_link = await results[0].get_attribute('href')
            full_link = "https://www.goodreads.com" + first_link if first_link.startswith('/') else first_link
            print(f"[{index}] Found book on Goodreads! Going to: {full_link}")
            await page.goto(full_link, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(3)
            
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
            
        df.at[index, 'GoodReads series link'] = page.url
        
        print(f"[{index}] Scraped Book: {book_title}, Rating: {rating}")
        
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
        
        # Avoid charmap encoding issues when printing or saving synopsis
        df.at[index, 'Synopsis (if available)'] = str(synopsis)
                    
    except Exception as e:
        print(f"[{index}] Error scraping {query}: {e}")
        df.at[index, 'Rating (out of 5) of Primary Book 1'] = 0.0
        
    finally:
        await page.close()

async def main():
    df = pd.read_excel(EXCEL_FILE)
    
    # Ensure columns are object type so we can insert strings if needed
    for col in ['Name of Series', 'Synopsis (if available)', 'GoodReads series link', 'Number of PRIMARY books in the series', 'Rating (out of 5) of Primary Book 1', 'Ratings (#) of Primary Book 1']:
        if col in df.columns and df[col].dtype != 'object':
            df[col] = df[col].astype('object')
            
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        while True:
            books_to_scrape = []
            for index, row in df.iterrows():
                # Start from index 70 as requested (which corresponds to row 72 in Excel due to 0-index + header)
                # But to be safe, we just check if it's unscraped. The original 70 are scraped.
                # Let's explicitly check index >= 70 since user asked for authors added "after row 70"
                if index < 70:
                    continue
                    
                # Check if already scraped
                val = row.get('Rating (out of 5) of Primary Book 1')
                if pd.notna(val) and str(val).strip() != "" and str(val).strip() != "nan":
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
    # Fix console encoding to avoid charmap errors
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(main())
