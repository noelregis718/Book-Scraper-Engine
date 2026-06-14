import asyncio
import pandas as pd
import urllib.parse
from playwright.async_api import async_playwright

EXCEL_FILE = "e:/Internship/PocketFM/books_from_images.xlsx"

async def fill_book(context, df, index, title, author, existing_link):
    page = await context.new_page()
    try:
        book_link = existing_link
        
        # If no link exists, search for it
        if pd.isna(book_link) or str(book_link).strip() == "" or not str(book_link).startswith("http"):
            query = f"{title} {author}".strip()
            print(f"[{index}] No link. Searching DDG for: {query}")
            ddg_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query + ' site:goodreads.com/book/show')}"
            await page.goto(ddg_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(3)
            ddg_links = await page.query_selector_all('a.result__url')
            
            if ddg_links:
                href = await ddg_links[0].get_attribute('href')
                if 'uddg=' in href:
                    book_link = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
                    print(f"[{index}] Found link: {book_link}")
                    df.at[index, 'GoodReads series link'] = book_link
                else:
                    print(f"[{index}] DDG returned unparseable link.")
                    return
            else:
                print(f"[{index}] No DDG links found.")
                return

        print(f"[{index}] Visiting: {book_link}")
        await page.goto(book_link, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(3)
        
        # Extract rating
        rating_elem = await page.query_selector('div.RatingStatistics__rating')
        rating = await rating_elem.inner_text() if rating_elem else ""
        
        # Extract count
        ratings_count_elem = await page.query_selector('div.RatingStatistics__meta [data-testid="ratingsCount"]')
        ratings_count = await ratings_count_elem.inner_text() if ratings_count_elem else ""
        ratings_count = ratings_count.replace("ratings", "").replace(",", "").replace("rating", "").strip()
        
        # Extract synopsis
        synopsis_elem = await page.query_selector('div.DetailsLayoutRightParagraph__widthConstrained span.Formatted')
        if not synopsis_elem:
            synopsis_elem = await page.query_selector('div[data-testid="description"]')
        synopsis = await synopsis_elem.inner_text() if synopsis_elem else ""
        
        print(f"[{index}] Scraped - Rating: {rating}, Count: {ratings_count}")
        
        try:
            rating_val = float(rating) if rating else None
        except:
            rating_val = None
            
        try:
            count_val = int(ratings_count) if ratings_count else None
        except:
            count_val = None
            
        if rating_val is not None and rating_val > 0:
            df.at[index, 'Rating (out of 5) of Primary Book 1'] = rating_val
        if count_val is not None and count_val > 0:
            df.at[index, 'Ratings (#) of Primary Book 1'] = count_val
        if synopsis:
            df.at[index, 'Synopsis (if available)'] = str(synopsis)

    except Exception as e:
        print(f"[{index}] Error: {e}")
    finally:
        await page.close()


async def main():
    print("Loading excel file...")
    df = pd.read_excel(EXCEL_FILE)
    
    # Identify missing rows
    missing_indices = []
    for index, row in df.iterrows():
        rating = row.get('Rating (out of 5) of Primary Book 1')
        count = row.get('Ratings (#) of Primary Book 1')
        synopsis = str(row.get('Synopsis (if available)', ''))
        
        is_missing = False
        if pd.isna(rating) or rating == 0.0 or rating == 0:
            is_missing = True
        elif pd.isna(count) or count == 0:
            is_missing = True
        elif not synopsis or synopsis.strip() == "" or synopsis == "nan":
            is_missing = True
            
        if is_missing:
            missing_indices.append(index)
            
    print(f"Found {len(missing_indices)} rows with missing data.")
    
    if not missing_indices:
        print("Nothing to do!")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        batch_size = 6
        for i in range(0, len(missing_indices), batch_size):
            batch = missing_indices[i:i+batch_size]
            print(f"\n--- Starting new batch of {len(batch)} books concurrently ---")
            
            tasks = []
            for index in batch:
                title = str(df.at[index, 'Name of Series'])
                author = str(df.at[index, 'Author Name'])
                link = df.at[index, 'GoodReads series link']
                tasks.append(fill_book(context, df, index, title, author, link))
                
            await asyncio.gather(*tasks)
            
            # Save after every batch
            df.to_excel(EXCEL_FILE, index=False)
            print("Batch complete and saved to Excel!")
            
        await browser.close()
        print("Finished filling all missing data!")

if __name__ == "__main__":
    asyncio.run(main())
