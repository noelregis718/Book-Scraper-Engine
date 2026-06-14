import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\Spencer_Hill_Press.xlsx"

async def scrape_book(semaphore, scraper, context, idx, row):
    async with semaphore:
        title = row['Name of Series']
        author = row['Author Name']
        
        print(f"[{idx}] Searching Goodreads for: {title} by {author}")
        details = await scraper.scrape_goodreads_data(context, title, author)
        
        if details:
            if details.get("GoodReads_Series_URL", "N/A") != "N/A":
                gr_link = details["GoodReads_Series_URL"]
            else:
                gr_link = details.get("GoodReads_Book_URL", "N/A")
                
            rating = details.get("Book1_Rating", details.get("GoodReads_Rating", "N/A"))
            count = details.get("Book1_Num_Ratings", details.get("GoodReads_Rating_Count", "N/A"))
            num_books = details.get("Num_Primary_Books", "N/A")
            
            print(f"[{idx}] Found: Rating {rating} ({count}) - {gr_link}")
            return idx, {
                'GoodReads series link': gr_link,
                'Rating (out of 5) of Primary Book 1': rating,
                'Ratings (#) of Primary Book 1': count,
                'Number of PRIMARY books in the series': num_books
            }
        else:
            print(f"[{idx}] Not found or error for: {title}")
            return idx, None

async def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    tasks = []
    indices_to_scrape = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        scraper = GoodreadsScraper()
        
        # 5 concurrent workers for aggressive scraping
        semaphore = asyncio.Semaphore(5)
        
        for idx, row in df.iterrows():
            link = str(row.get('GoodReads series link', 'N/A'))
            if link == 'N/A' or pd.isna(row['GoodReads series link']):
                indices_to_scrape.append(idx)
                tasks.append(scrape_book(semaphore, scraper, context, idx, row))
                
        print(f"Found {len(tasks)} books missing Goodreads data. Launching aggressive scraper...")
        
        results = await asyncio.gather(*tasks)
        
        for idx, res in results:
            if res:
                for col, val in res.items():
                    df.at[idx, col] = val
                    
        await browser.close()
        
    print("Saving Excel file...")
    df.to_excel(EXCEL_FILE, index=False)
    print("Done! All Goodreads data has been saved.")

if __name__ == '__main__':
    asyncio.run(main())
