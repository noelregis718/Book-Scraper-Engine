import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import urllib.parse
import sys

EXCEL_FILE = sys.argv[1] if len(sys.argv) > 1 else "e:/Internship/PocketFM/unter_agency_books.xlsx"

async def scrape_book(context, author, book_url):
    page = await context.new_page()
    try:
        await page.goto(book_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(2)
        
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
        
        series_link = ""
        series_elem = await page.query_selector('h3.Text__h3 a')
        if series_elem:
            href = await series_elem.get_attribute('href')
            if href and "series" in href:
                series_link = href
        
        num_primary_books = 1
        if series_link:
            full_series_link = series_link if series_link.startswith('http') else f"https://www.goodreads.com{series_link}"
            await page.goto(full_series_link, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(2)
            series_desc_elem = await page.query_selector('div.responsiveSeriesHeader__subtitle')
            if series_desc_elem:
                import re
                desc = await series_desc_elem.inner_text()
                match = re.search(r'(\d+)\s+primary\s+works', desc, re.IGNORECASE)
                if match:
                    num_primary_books = int(match.group(1))
                    
        try:
            rating_val = float(rating) if rating else None
        except:
            rating_val = None
            
        try:
            count_val = int(ratings_count) if ratings_count else None
        except:
            count_val = None
            
        return {
            "Name of Series": book_title,
            "Author Name": author,
            "GoodReads series link": book_url,
            "Number of PRIMARY books in the series": num_primary_books,
            "Rating (out of 5) of Primary Book 1": rating_val,
            "Ratings (#) of Primary Book 1": count_val,
            "Synopsis (if available)": str(synopsis)
        }
    except Exception as e:
        print(f"Error scraping book {book_url}: {e}")
        return None
    finally:
        await page.close()

async def scrape_author(context, author):
    page = await context.new_page()
    try:
        print(f"Searching Goodreads for author: {author}")
        search_url = f"https://www.goodreads.com/search?q={urllib.parse.quote_plus(author)}"
        await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(3)
        
        results = await page.query_selector_all('a.bookTitle')
        if not results:
            print(f"No books found on Goodreads for {author}. Trying DDG...")
            ddg_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(author + ' site:goodreads.com/author/show')}"
            await page.goto(ddg_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(2)
            ddg_links = await page.query_selector_all('a.result__url')
            if ddg_links:
                href = await ddg_links[0].get_attribute('href')
                if 'uddg=' in href:
                    author_url = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
                    await page.goto(author_url, wait_until="domcontentloaded", timeout=45000)
                    await asyncio.sleep(3)
                    results = await page.query_selector_all('a.bookTitle')
        
        if not results:
            print(f"Absolutely no books found for author {author}")
            return [{"Author Name": author, "Rating (out of 5) of Primary Book 1": 0.0}]
            
        book_urls = []
        for res in results[:3]:
            href = await res.get_attribute('href')
            full_link = "https://www.goodreads.com" + href if href.startswith('/') else href
            book_urls.append(full_link)
            
        print(f"Found {len(book_urls)} books for {author}. Spawning {len(book_urls)} tabs concurrently...")
        
        tasks = []
        for url in book_urls:
            tasks.append(scrape_book(context, author, url))
            
        scraped_books = await asyncio.gather(*tasks)
        
        valid_books = [b for b in scraped_books if b is not None]
        if not valid_books:
            return [{"Author Name": author, "Rating (out of 5) of Primary Book 1": 0.0}]
        return valid_books
    except Exception as e:
        print(f"Error searching author {author}: {e}")
        return [{"Author Name": author, "Rating (out of 5) of Primary Book 1": 0.0}]
    finally:
        await page.close()

async def main():
    df = pd.read_excel(EXCEL_FILE)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        while True:
            pending_authors = []
            for index, row in df.iterrows():
                val_title = row.get('Name of Series')
                val_rating = row.get('Rating (out of 5) of Primary Book 1')
                # If Name of Series is empty AND Rating is empty, it's an unprocessed author
                if pd.isna(val_title) and pd.isna(val_rating):
                    author = row.get('Author Name')
                    if pd.notna(author) and str(author).strip() != "" and str(author).strip() not in pending_authors:
                        pending_authors.append(str(author).strip())
                        
            if not pending_authors:
                print("All authors processed!")
                break
                
            batch_authors = pending_authors[:2]
            print(f"\n--- Starting batch of 2 authors (6 tabs max): {batch_authors} ---")
            
            tasks = []
            for author in batch_authors:
                tasks.append(scrape_author(context, author))
                
            results = await asyncio.gather(*tasks)
            
            # Remove the blank placeholder rows for these specific authors
            for author in batch_authors:
                df = df[~((df['Author Name'] == author) & (df['Name of Series'].isna()))]
            
            new_rows = []
            for author_books in results:
                for book in author_books:
                    new_rows.append(book)
                    
            df_new = pd.DataFrame(new_rows)
            for col in df.columns:
                if col not in df_new.columns:
                    df_new[col] = pd.NA
                    
            # Reorder columns to match original
            df_new = df_new[df.columns]
                    
            df = pd.concat([df, df_new], ignore_index=True)
            df.to_excel(EXCEL_FILE, index=False)
            print("Batch complete and saved to Excel!")
            
        await browser.close()

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(main())
