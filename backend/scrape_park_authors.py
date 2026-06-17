import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import bs4

EXCEL_FILE = "e:/Internship/PocketFM/park_and_fine_books.xlsx"

async def scrape_authors():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        print("Visiting Park & Fine authors page...")
        await page.goto("https://parkfinebrower.com/authors/", wait_until="domcontentloaded", timeout=45000)
        
        # Scroll to bottom repeatedly to ensure all lazy loaded items appear
        for _ in range(5):
            await page.keyboard.press("End")
            await asyncio.sleep(1)
            
        html = await page.content()
        soup = bs4.BeautifulSoup(html, 'html.parser')
        
        author_tags = soup.select('h5.card-title')
        authors = [tag.text.strip() for tag in author_tags if tag.text.strip()]
        
        # Distinct list
        authors = list(dict.fromkeys(authors))
        print(f"Extracted {len(authors)} authors from the website.")
        
        await browser.close()
        
        # Append to Excel
        print("Loading Excel file...")
        df = pd.read_excel(EXCEL_FILE)
        
        existing_authors = set(df['Author Name'].dropna().tolist())
        new_authors = [a for a in authors if a not in existing_authors]
        
        if not new_authors:
            print("No new authors to add.")
            return
            
        print(f"Adding {len(new_authors)} NEW authors to Excel...")
        
        new_rows = []
        for author in new_authors:
            row = {col: pd.NA for col in df.columns}
            row['Author Name'] = author
            row['Publisher'] = "Park & Fine Literary and Media"
            row['Name of agent'] = "Park & Fine"
            new_rows.append(row)
            
        new_df = pd.DataFrame(new_rows)
        df = pd.concat([df, new_df], ignore_index=True)
        
        df.to_excel(EXCEL_FILE, index=False)
        print(f"Appended {len(new_authors)} authors to {EXCEL_FILE} successfully!")

if __name__ == "__main__":
    asyncio.run(scrape_authors())
