import asyncio
import json
import pandas as pd
from playwright.async_api import async_playwright

EXCEL_FILE = "e:/Internship/PocketFM/Sourcebooks_Romance_Deep_Dive_Catalog.xlsx"

async def run():
    df = pd.read_excel(EXCEL_FILE)
    
    # We already have book names in the sheet
    existing_books = set(df['Name of Series'].dropna().tolist())
    new_book_names = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        async def handle_response(response):
            if 'graphql' in response.url:
                try:
                    text = await response.text()
                    data = json.loads(text)
                    if 'data' in data and 'products' in data['data']:
                        items = data['data']['products'].get('items', [])
                        if len(items) > 0:
                            for item in items:
                                name = item.get('name')
                                if name and name not in existing_books and name not in new_book_names:
                                    new_book_names.append(name)
                                    print(f"Scraped new book: {name}")
                except Exception as e:
                    pass
                    
        page.on("response", handle_response)
        
        # Start from page 3 and go up to page 10
        for pnum in range(3, 11):
            print(f"\nNavigating to Sourcebooks Page {pnum}...")
            await page.goto(f"https://www.sourcebooks.com/fiction/romance?p={pnum}", wait_until="domcontentloaded")
            await asyncio.sleep(5)
            
            # Scroll to trigger graphql load if it's lazy
            for _ in range(4):
                await page.evaluate("window.scrollBy(0, 1000);")
                await asyncio.sleep(1)
            
            if len(existing_books) + len(new_book_names) >= 200:
                print("Reached 200 total books!")
                break
                
        await browser.close()
        
    print(f"Extracted {len(new_book_names)} NEW book names from pages 3-10!")
    
    new_rows = []
    for name in new_book_names:
        row = {col: "" for col in df.columns}
        row["Name of Series"] = name
        new_rows.append(row)
        
    if new_rows:
        df_new = pd.DataFrame(new_rows)
        df = pd.concat([df, df_new], ignore_index=True)
        # Limit to strictly 200 rows if requested
        df = df.head(200)
        df.to_excel(EXCEL_FILE, index=False)
        print(f"Saved to excel! Total rows now: {len(df)}")
    else:
        print("No new books found.")

if __name__ == "__main__":
    asyncio.run(run())
