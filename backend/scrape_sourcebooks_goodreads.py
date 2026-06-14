import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import urllib.parse
import os
import re

EXCEL_FILE = "e:/Internship/PocketFM/books_from_images.xlsx"

async def scrape_book(context, df, index, title, author):
    page = await context.new_page()
    query = f"{title} {author}".strip()
    print(f"[{index}] Searching Goodreads for: {query}")
    search_url = f"https://www.goodreads.com/search?q={urllib.parse.quote_plus(query)}"
    
    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(3)
        
        # Check if it directly redirected to the book page or showed search results
        if "/book/show/" not in page.url:
            # Click the first search result
            results = await page.query_selector_all('a.bookTitle')
            if not results and author:
                # Aggressive fallback: search without author
                fallback_query = title
                print(f"[{index}] Trying fallback search for: {fallback_query}")
                search_url = f"https://www.goodreads.com/search?q={urllib.parse.quote_plus(fallback_query)}"
                await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(3)
                results = await page.query_selector_all('a.bookTitle')
                
            if not results:
                # ULTIMATE Aggressive fallback: DuckDuckGo search
                print(f"[{index}] Trying DuckDuckGo fallback for: {query}")
                ddg_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query + ' site:goodreads.com/book/show')}"
                await page.goto(ddg_url, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(3)
                ddg_links = await page.query_selector_all('a.result__url')
                
                if ddg_links:
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
                    print(f"[{index}] No search results found anywhere for {query}")
                    df.at[index, 'Rating (out of 5) of Primary Book 1'] = 0.0
                    await page.close()
                    return
            else:
                first_link = await results[0].get_attribute('href')
                full_link = "https://www.goodreads.com" + first_link if first_link.startswith('/') else first_link
                await page.goto(full_link, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(3)
        
        # We are now on the book page
        rating_elem = await page.query_selector('div.RatingStatistics__rating')
        rating = await rating_elem.inner_text() if rating_elem else ""
        
        ratings_count_elem = await page.query_selector('div.RatingStatistics__meta [data-testid="ratingsCount"]')
        ratings_count = await ratings_count_elem.inner_text() if ratings_count_elem else ""
        ratings_count = ratings_count.replace("ratings", "").replace(",", "").replace("rating", "").strip()
        
        synopsis_elem = await page.query_selector('div.DetailsLayoutRightParagraph__widthConstrained span.Formatted')
        if not synopsis_elem:
            synopsis_elem = await page.query_selector('div[data-testid="description"]')
        synopsis = await synopsis_elem.inner_text() if synopsis_elem else ""
        
        # We always want the Goodreads book link, so we'll store the page.url!
        book_link = page.url
        df.at[index, 'GoodReads series link'] = book_link
        
        series_link = ""
        num_primary_books = ""
        series_elem = await page.query_selector('h3.Text__h3 a')
        if series_elem:
            href = await series_elem.get_attribute('href')
            if href and "series" in href:
                series_link = href
        
        print(f"[{index}] Found Rating: {rating}, Count: {ratings_count}")
        
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
        
        if series_link:
            full_series_link = series_link if series_link.startswith('http') else f"https://www.goodreads.com{series_link}"
            # Don't overwrite the book URL we just saved with the series URL, keep the Book URL
            # but we can still fetch series length
            await page.goto(full_series_link, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(3)
            
            series_desc_elem = await page.query_selector('div.responsiveSeriesHeader__subtitle')
            if series_desc_elem:
                desc = await series_desc_elem.inner_text()
                match = re.search(r'(\d+)\s+primary\s+works', desc, re.IGNORECASE)
                if match:
                    num_primary_books = match.group(1)
                    df.at[index, 'Number of PRIMARY books in the series'] = num_primary_books
                    print(f"[{index}] Series found! Primary books: {num_primary_books}")
                    
    except Exception as e:
        print(f"[{index}] Error scraping {query}: {e}")
        df.at[index, 'Rating (out of 5) of Primary Book 1'] = 0.0
        
    finally:
        await page.close()


async def scrape_goodreads():
    df = pd.read_excel(EXCEL_FILE)
    
    # Ensure columns are object type so we can insert strings if needed
    for col in ['Synopsis (if available)', 'GoodReads series link', 'Number of PRIMARY books in the series', 'Rating (out of 5) of Primary Book 1', 'Ratings (#) of Primary Book 1']:
        if col in df.columns and df[col].dtype != 'object':
            df[col] = df[col].astype('object')
            
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        while True:
            books_to_scrape = []
            for index, row in df.iterrows():
                # Only scrape from row 32 onwards (which is index 30)
                if index < 30:
                    continue
                    
                # Check if already scraped
                if pd.notna(row.get('Rating (out of 5) of Primary Book 1')) and str(row.get('Rating (out of 5) of Primary Book 1')).strip() != "":
                    # Special case where rating is 0.0 might mean not found, but we'll count it as scraped for now to avoid infinite loops,
                    # actually let's skip them
                    continue
                if pd.isna(row.get('Name of Series')) or str(row.get('Name of Series')).strip() == "" or "Sourcebooks" in str(row.get('Name of Series')):
                    continue
                    
                title = str(row.get('Name of Series', '')).strip()
                author = "" if pd.isna(row.get('Author Name')) else str(row.get('Author Name')).strip()
                
                books_to_scrape.append((index, title, author))
                
                if len(books_to_scrape) == 10:
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
