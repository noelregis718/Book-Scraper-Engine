import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from goodreads_scraper import GoodreadsScraper

async def main():
    excel_path = r"e:\Internship\PocketFM\Books_Scraping_Template.xlsx"
    df = pd.read_excel(excel_path)
    
    # Get first row
    title = df.iloc[0]['Name of Series']
    author = df.iloc[0]['Author Name']
    print(f"Target: {title} by {author}")
    
    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        # Launching headless=True might get blocked, but since it's a server we might not have a choice unless xvfb is used. Let's try headless=True first if we are on a server.
        # Actually playwright chromium headless usually works or fails depending on bot protections. The class has headless=False in some places. Let's try headless=True to avoid UI issues.
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # We might need to login, but let's try without login first as the original scraper has a login method but search_goodreads_data might work without it.
        # Wait, the scraper uses 'login_to_goodreads' ? No, the 'scrape_goodreads_data' doesn't call it. It does its own search.
        
        # Scrape Goodreads
        print("Starting aggressive scraper...")
        data = await scraper.scrape_goodreads_data(context, title, author)
        print("Data returned:")
        print(data)
        
        if data:
            df.at[0, 'GoodReads series link'] = data.get('GoodReads_Series_URL')
            df.at[0, 'Number of PRIMARY books in the series'] = data.get('Num_Primary_Books')
            df.at[0, 'Rating (out of 5) of Primary Book 1'] = data.get('Book1_Rating')
            df.at[0, 'Ratings (#) of Primary Book 1'] = data.get('Book1_Num_Ratings')
            df.at[0, 'Synopsis (if available)'] = data.get('Description')
            df.at[0, 'Romantasy = Yes or No?'] = data.get('Romantasy_Subgenre')
            df.at[0, 'Romantasy Sub-Genre of series'] = f"{data.get('Genre')} / {data.get('Sub_Genre')}"
            
            df.to_excel(excel_path, index=False)
            print("Successfully updated Excel sheet for the first book.")
        else:
            print("Failed to scrape data.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
