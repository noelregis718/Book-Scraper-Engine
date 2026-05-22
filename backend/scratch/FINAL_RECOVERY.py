import asyncio
import os
import pandas as pd
import re
from playwright.async_api import async_playwright

BASE_URL = "https://awfulagent.com/jabclients/"
OUTPUT_FILE = r"E:\Internship\PocketFM\awful agents.xlsx"

async def scrape_bibliography(page):
    books = []
    elements = await page.query_selector_all('div.book-title')
    for el in elements:
        text = (await el.evaluate("el => el.innerText")).strip()
        if text: books.append(text)
    return list(dict.fromkeys(books))

async def full_restore():
    print("Starting FULL Structural Restore (1,406+ books)...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(BASE_URL, wait_until="domcontentloaded")
        
        links = await page.query_selector_all('a.authorlink')
        authors = []
        for link in links:
            name = (await link.evaluate("el => el.innerText")).strip()
            url = await link.evaluate("el => el.href")
            if name and url: authors.append({'name': name, 'url': url})
        
        print(f"  [System] Found {len(authors)} authors. Rebuilding catalog in parallel batches...")
        
        context = await browser.new_context()
        rows = []
        BATCH_SIZE = 10
        for i in range(0, len(authors), BATCH_SIZE):
            batch = authors[i:i+BATCH_SIZE]
            print(f"  [Batch {i//BATCH_SIZE + 1}] Scanning authors: {', '.join([a['name'] for a in batch])}")
            
            async def process_author(author):
                # Create a dedicated page for each author in the batch
                auth_page = await context.new_page()
                try:
                    await auth_page.goto(author['url'], wait_until="domcontentloaded", timeout=45000)
                    titles = await scrape_bibliography(auth_page)
                    author_rows = []
                    for title in titles:
                        clean_title = re.sub(r'\(\d{4}\)', '', title).strip()
                        author_rows.append({
                            'Name of Series': clean_title,
                            'Author Name': author['name'],
                            'Publisher': 'Jabberwocky',
                            'GoodReads series link': 'N/A',
                            'Number of PRIMARY books in the series': '1',
                            'Rating (out of 5) of Primary Book 1': 'N/A',
                            'Ratings (#) of Primary Book 1': 'N/A',
                            'Synopsis (if available)': 'N/A',
                            'Is it Romantasy ?': 'No',
                            'Romantasy Sub-Genre of series': 'N/A',
                            'Name of agent': 'Jabberwocky'
                        })
                    return author_rows
                except Exception as e:
                    print(f"    [Error] Failed {author['name']}: {e}")
                    return []
                finally:
                    await auth_page.close()

            # Process the batch in parallel
            batch_results = await asyncio.gather(*[process_author(a) for a in batch])
            for res in batch_results:
                rows.extend(res)
            
        df = pd.DataFrame(rows)
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"MISSION COMPLETE: Restored {len(df)} titles to {OUTPUT_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(full_restore())
