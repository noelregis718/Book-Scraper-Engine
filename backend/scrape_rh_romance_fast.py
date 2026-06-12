import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

EXCEL_FILE = r"e:\Internship\PocketFM\del_rey_romantasy_books.xlsx"

async def scrape_rh_romance_full():
    print("Starting safe full scraper for Random House Romance books...")
    
    if os.path.exists(EXCEL_FILE):
        df_existing = pd.read_excel(EXCEL_FILE)
    else:
        df_existing = pd.DataFrame()
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        url = "https://randomhousebooks.com/book-category/romance/"
        print(f"Navigating to {url}")
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        print("Clicking 'Load More' to load books in chunks...", flush=True)
        clicks = 0
        MAX_CLICKS = 40  # prevent out-of-memory crash
        
        while clicks < MAX_CLICKS:
            try:
                load_more = page.locator("button:has-text('Load More')").first
                if await load_more.count() > 0:
                    if await load_more.is_visible():
                        await load_more.evaluate("el => el.click()")
                        clicks += 1
                        if clicks % 5 == 0:
                            print(f"Clicked Load More {clicks}/{MAX_CLICKS} times...", flush=True)
                        await page.wait_for_timeout(3000)
                    else:
                        print("Load More is hidden. All books are loaded.", flush=True)
                        break
                else:
                    print("No Load More button found. All books loaded.", flush=True)
                    break
            except Exception as e:
                print(f"Stopped clicking Load More: {e}")
                break

        print("Extracting book data...", flush=True)
        books = []
        
        # In case the browser crashed, check if we can still evaluate
        try:
            book_elements = await page.locator(".wp-block-dwt-book, .block__book").all()
            for el in book_elements:
                try:
                    title_el = el.locator(".book-details__title").first
                    title = await title_el.inner_text() if await title_el.count() > 0 else "N/A"
                    
                    author_el = el.locator(".book-details__author").first
                    author = await author_el.inner_text() if await author_el.count() > 0 else "N/A"
                    
                    link_el = el.locator("a").first
                    link = await link_el.get_attribute("href") if await link_el.count() > 0 else "N/A"
                    if link and not link.startswith("http") and link != "N/A":
                        link = "https://randomhousebooks.com" + link
                        
                    if title != "N/A" and title.strip():
                        books.append({
                            "Name of Series": title.strip(),
                            "Author Name": author.strip(),
                            "Publisher": "Random House",
                            "GoodReads series link": "N/A",
                            "Number of PRIMARY books in the series": "N/A",
                            "Rating (out of 5) of Primary Book 1": "N/A",
                            "Ratings (#) of Primary Book 1": "N/A",
                            "Synopsis (if available)": "N/A",
                            "Romantasy = Yes or No?": "N/A",
                            "Romantasy Sub-Genre of series": "N/A",
                            "Name of agent": "N/A",
                            "Source Link": link
                        })
                except Exception as e:
                    continue
        except Exception as e:
            print(f"Error during extraction (maybe page crashed): {e}")
            
        df_new = pd.DataFrame(books)
        
        if df_new.empty:
            print("WARNING: No books were found! Memory crash likely occurred previously.", flush=True)
        else:
            print(f"Total books scraped from this session: {len(df_new)}", flush=True)
            
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined = df_combined.drop_duplicates(subset=['Name of Series'], keep='first')
            
            df_combined.to_excel(EXCEL_FILE, index=False)
            print(f"Successfully appended and saved {len(df_combined)} total unique books to {EXCEL_FILE}", flush=True)
            
            try:
                os.startfile(EXCEL_FILE)
            except Exception as e:
                pass
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_rh_romance_full())
