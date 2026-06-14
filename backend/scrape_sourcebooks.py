import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import json
import re
import os

EXCEL_FILE = "e:/Internship/PocketFM/sourcebooks_romance.xlsx"

COLUMNS = [
    "Name of Series",
    "Author Name",
    "Publisher",
    "GoodReads series link",
    "Number of PRIMARY books in the series",
    "Rating (out of 5) of Primary Book 1",
    "Ratings (#) of Primary Book 1",
    "Synopsis (if available)",
    "Romantasy = Yes or No?",
    "Romantasy Sub-Genre of series",
    "Name of agent"
]

async def scrape_sourcebooks():
    if os.path.exists(EXCEL_FILE):
        df_existing = pd.read_excel(EXCEL_FILE)
    else:
        df_existing = pd.DataFrame(columns=COLUMNS)
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        main_page = await context.new_page()
        
        book_links = set()
        
        print("Navigating to Sourcebooks Romance page 1...")
        try:
            await main_page.goto("https://www.sourcebooks.com/fiction/romance", wait_until="networkidle", timeout=45000)
        except Exception as e:
            print(f"Goto finished with a timeout/warning: {e}")
        await asyncio.sleep(2)
        
        print("Skipping to page 11 (clicking Next 10 times)...")
        for i in range(10):
            # Scroll down to ensure pagination renders on the current page
            for _ in range(4):
                await main_page.evaluate("window.scrollBy(0, 1000);")
                await asyncio.sleep(1)
            
            try:
                await main_page.wait_for_selector('.navButton-icon-tob', timeout=10000)
            except:
                pass
                
            btns = await main_page.query_selector_all('.navButton-icon-tob')
            if len(btns) >= 3:
                print(f"Skipping page {i+1}...")
                await btns[2].click(force=True)
                await asyncio.sleep(3)
            else:
                print(f"Could not find Next button while skipping on step {i}.")
                break
                
        async def extract_links_on_page():
            for _ in range(4):
                await main_page.evaluate("window.scrollBy(0, 1000);")
                await asyncio.sleep(1)
            await asyncio.sleep(2)
            links = await main_page.query_selector_all('a')
            count = 0
            for l in links:
                href = await l.get_attribute('href')
                if href and re.search(r'\d{13}', href):
                    full_url = "https://www.sourcebooks.com" + href if href.startswith('/') else href
                    if "sourcebooks.com" in full_url and full_url not in book_links:
                        book_links.add(full_url)
                        count += 1
            return count

        print("Starting extraction from Page 11")
        new_links = await extract_links_on_page()
        print(f"Found {new_links} new book links on page 11.")

        for page_num in range(12, 21):
            print(f"Navigating to Sourcebooks Romance page {page_num}...")
            try:
                btns = await main_page.query_selector_all('.navButton-icon-tob')
                if len(btns) >= 3:
                    await btns[2].click(force=True)
                    await asyncio.sleep(3)
                    new_links = await extract_links_on_page()
                    print(f"Found {new_links} new book links on page {page_num}.")
                    if new_links == 0:
                        print("No more new books found, might have reached the end.")
                        break
                else:
                    print("Could not find the Next button.")
                    break
            except Exception as e:
                print(f"Failed to navigate to page {page_num}: {e}")
                break

        print(f"Found {len(book_links)} total book links across pages 11-20.")
        
        new_results = []
        for idx, url in enumerate(list(book_links)):
            print(f"Processing book {idx+1}/{len(book_links)}: {url}")
            book_page = await context.new_page()
            try:
                await book_page.goto(url, wait_until="domcontentloaded", timeout=60000)
                # Give it an extra moment to render the title
                await asyncio.sleep(2)
                
                title = ""
                author = ""
                
                scripts = await book_page.query_selector_all('script[type="application/ld+json"]')
                for s in scripts:
                    text = await s.inner_text()
                    try:
                        data = json.loads(text)
                        graph = data.get('@graph', [data])
                        for item in graph:
                            if isinstance(item, dict):
                                item_type = item.get('@type', [])
                                if 'Product' in item_type or 'Book' in item_type or item_type == 'Product' or item_type == 'Book':
                                    if not title:
                                        title = item.get('name', '')
                                    author_data = item.get('author', {})
                                    if isinstance(author_data, dict):
                                        author = author_data.get('name', '')
                                    elif isinstance(author_data, list) and len(author_data) > 0:
                                        author = author_data[0].get('name', '')
                    except Exception:
                        pass
                
                if not title or "Sourcebooks" in title:
                    try:
                        # Wait for the H1 to appear just in case it's slowly loaded via react
                        title_elem = await book_page.wait_for_selector('h1', timeout=5000)
                        if title_elem:
                            title = await title_elem.inner_text()
                    except:
                        title = await book_page.title()
                        
                title = title.split('\n')[0].strip()
                if "Sourcebooks" in title and "|" in title:
                    title = title.split("|")[0].strip()
                
                row = {col: "" for col in COLUMNS}
                row["Name of Series"] = title
                row["Author Name"] = author
                row["Publisher"] = "Sourcebooks"
                new_results.append(row)
                
                print(f"Extracted -> Title: {title} | Author: {author}")
                
            except Exception as e:
                print(f"Failed to process {url}: {e}")
                
            finally:
                await book_page.close()
            
            # Periodically save the progress by appending to df_existing
            if (idx + 1) % 10 == 0 or (idx + 1) == len(book_links):
                df_new = pd.DataFrame(new_results, columns=COLUMNS)
                df_final = pd.concat([df_existing, df_new], ignore_index=True)
                df_final.to_excel(EXCEL_FILE, index=False)
                
        print(f"Scraping complete! Added {len(new_results)} books to the sheet.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_sourcebooks())
