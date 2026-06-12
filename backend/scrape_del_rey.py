import asyncio
import pandas as pd
from playwright.async_api import async_playwright

EXCEL_FILE = r"e:\Internship\PocketFM\del_rey_romantasy_books.xlsx"

async def scrape_del_rey_romance():
    print("Starting scraper for Del Rey Romance books...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        print("Navigating to https://randomhousebooks.com/imprint/del-rey/")
        await page.goto("https://randomhousebooks.com/imprint/del-rey/", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        try:
            cookie_close = page.locator("button.close, .cookie-close, [aria-label='Close']")
            if await cookie_close.count() > 0:
                await cookie_close.first.click(force=True)
                await page.wait_for_timeout(1000)
        except Exception:
            pass
            
        print("Clicking Romance filter...")
        await page.evaluate("document.getElementById('romance').click()")
        await page.wait_for_timeout(5000)
        
        print("Clicking 'Load More' to load all books...")
        clicks = 0
        while True:
            try:
                load_more = page.locator("button:has-text('Load More')").first
                if await load_more.count() > 0:
                    if await load_more.is_visible():
                        await load_more.evaluate("el => el.click()")
                        clicks += 1
                        print(f"Clicked Load More {clicks} times...", flush=True)
                        await page.wait_for_timeout(3000)
                    else:
                        print("Load More is hidden. Assuming all books are loaded.", flush=True)
                        break
                else:
                    print("No Load More button found in DOM. All books loaded.", flush=True)
                    break
            except Exception as e:
                print(f"Stopped clicking Load More: {e}")
                break

        print("Extracting book data...", flush=True)
        books = []
        
        # Select all book elements based on HTML structure
        book_elements = await page.locator(".wp-block-dwt-book, .block__book").all()
        for el in book_elements:
            try:
                title_el = el.locator(".book-details__title").first
                title = await title_el.inner_text() if await title_el.count() > 0 else "N/A"
                
                author_el = el.locator(".book-details__author").first
                author = await author_el.inner_text() if await author_el.count() > 0 else "N/A"
                
                if title != "N/A" and title.strip():
                    books.append({
                        "Name of Series": title.strip(),
                        "Author Name": author.strip(),
                        "Publisher": "Del Rey",
                        "GoodReads series link": "N/A",
                        "Number of PRIMARY books in the series": "N/A",
                        "Rating (out of 5) of Primary Book 1": "N/A",
                        "Ratings (#) of Primary Book 1": "N/A",
                        "Synopsis (if available)": "N/A",
                        "Romantasy = Yes or No?": "N/A",
                        "Romantasy Sub-Genre of series": "N/A",
                        "Name of agent": "N/A",
                    })
            except Exception as e:
                continue
        
        df = pd.DataFrame(books).drop_duplicates(subset=['Name of Series'])
        
        if df.empty:
            print("WARNING: No books were found! Please check selectors.", flush=True)
        else:
            print(f"Total unique books scraped: {len(df)}", flush=True)
            
        df.to_excel(EXCEL_FILE, index=False)
        print(f"Successfully saved to {EXCEL_FILE}", flush=True)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_del_rey_romance())
