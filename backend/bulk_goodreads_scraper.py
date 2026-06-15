import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from goodreads_scraper import GoodreadsScraper
import os
import time

async def process_book(index, title, author, scraper, context, df, excel_path, excel_lock, semaphore):
    async with semaphore:
        print(f"Scraping [{index+1}/{len(df)}]: {title} by {author}")
        try:
            data = await scraper.scrape_goodreads_data(context, title, author)
            if data:
                async with excel_lock:
                    df.at[index, 'GoodReads series link'] = data.get('GoodReads_Series_URL')
                    df.at[index, 'Number of PRIMARY books in the series'] = data.get('Num_Primary_Books')
                    df.at[index, 'Rating (out of 5) of Primary Book 1'] = data.get('Book1_Rating')
                    df.at[index, 'Ratings (#) of Primary Book 1'] = data.get('Book1_Num_Ratings')
                    df.at[index, 'Synopsis (if available)'] = data.get('Description')
                    df.at[index, 'Romantasy = Yes or No?'] = data.get('Romantasy_Subgenre')
                    
                    genre = data.get('Genre', '')
                    sub_genre = data.get('Sub_Genre', '')
                    df.at[index, 'Romantasy Sub-Genre of series'] = f"{genre} / {sub_genre}".strip(' /')
                    
                    df.to_excel(excel_path, index=False)
                print(f"  -> Saved data for: {title}")
            else:
                print(f"  -> No data found for: {title}")
        except Exception as e:
            print(f"  -> Error scraping {title}: {e}")

async def main():
    excel_path = r"e:\Internship\PocketFM\Books_Scraping_Template.xlsx"
    if not os.path.exists(excel_path):
        print(f"Error: {excel_path} not found.")
        return
        
    df = pd.read_excel(excel_path)
    print(f"Loaded {len(df)} books from Excel.")
    
    scraper = GoodreadsScraper(headless=False)
    semaphore = asyncio.Semaphore(10)
    excel_lock = asyncio.Lock()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        tasks = []
        for index, row in df.iterrows():
            if pd.notna(row['Romantasy = Yes or No?']):
                continue
                
            title = row['Name of Series']
            author = row['Author Name']
            
            if pd.isna(title) or pd.isna(author):
                continue
                
            task = asyncio.create_task(process_book(index, title, author, scraper, context, df, excel_path, excel_lock, semaphore))
            tasks.append(task)
            
        await asyncio.gather(*tasks)
            
        await browser.close()
        print("Bulk scraping finished!")

if __name__ == "__main__":
    asyncio.run(main())
