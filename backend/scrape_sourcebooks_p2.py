import asyncio
import json
import pandas as pd
from playwright.async_api import async_playwright

EXCEL_FILE = "e:/Internship/PocketFM/sourcebooks_romance.xlsx"

async def run():
    # Read existing excel
    df = pd.read_excel(EXCEL_FILE)
    
    # Keep only the first 30 books
    df = df.iloc[:30].copy()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        book_names = []
        
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
                                if name and name not in book_names:
                                    book_names.append(name)
                except Exception as e:
                    pass
                    
        page.on("response", handle_response)
        
        print("Navigating to Sourcebooks Page 1...")
        await page.goto("https://www.sourcebooks.com/fiction/romance", wait_until="domcontentloaded")
        await asyncio.sleep(5)
        
        print("Clicking Next to go to Page 2...")
        try:
            # We wait for the pagination button to render
            for _ in range(4):
                await page.evaluate("window.scrollBy(0, 1000);")
                await asyncio.sleep(1)
            
            btns = await page.query_selector_all('.navButton-icon-tob')
            if len(btns) >= 3:
                await btns[2].click(force=True)
                print("Clicked Next!")
                await asyncio.sleep(8)
            else:
                print("Could not find Next button, maybe rate limited. Exiting.")
        except Exception as e:
            print("Error clicking next:", e)
        
        await browser.close()
        
    print(f"Extracted {len(book_names)} book names from Page 2!")
    
    # Append the new book names to df
    new_rows = []
    for name in book_names:
        row = {col: "" for col in df.columns}
        row["Name of Series"] = name
        new_rows.append(row)
        
    if new_rows:
        df_new = pd.DataFrame(new_rows)
        df = pd.concat([df, df_new], ignore_index=True)
        
    df.to_excel(EXCEL_FILE, index=False)
    print("Saved to excel!")

if __name__ == "__main__":
    asyncio.run(run())
