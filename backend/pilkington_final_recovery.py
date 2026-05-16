import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import os
from goodreads_scraper import GoodreadsScraper
from ai_classifier import identify_subgenre

CATALOG_FILE = "Pilkington_Agency_Catalog_Final.xlsx"

REMAINING_AUTHORS = [
    "Josh Hortinela",
    "Dr Mark Williams",
    "Dr Mark Williams & Gavin McCormack"
]

def format_row(data, author):
    link = data.get('GoodReads_Series_URL')
    if not link or link == "N/A":
        link = data.get('GoodReads_Book_URL')
    
    synopsis = data.get('Description', 'N/A')
    genre = data.get('Genre', 'N/A')
    subgenre = identify_subgenre(synopsis, [genre])
    
    return {
        'Name of Series': data.get('Book_Title', 'N/A'),
        'Author Name': author,
        'Publisher': 'Pilkington Agency',
        'GoodReads series link': link,
        'Number of PRIMARY books in the series': data.get('Num_Primary_Books', '1'),
        'Rating (out of 5) of Primary Book 1': data.get('GoodReads_Rating', 'N/A'),
        'Ratings (#) of Primary Book 1': data.get('GoodReads_Rating_Count', 'N/A'),
        'Synopsis (if available)': synopsis,
        'Romantasy = Yes or No?': "Yes" if subgenre != "N/A" else "No",
        'Romantasy Sub-Genre of series': subgenre,
        'Name of agent': 'Alice Pilkington'
    }

async def run_final_recovery():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = GoodreadsScraper(headless=False)
        
        # Login
        print("[System] Performing Mandatory Login for Final Recovery...")
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        await login_page.close()

        new_rows = []
        for author in REMAINING_AUTHORS:
            print(f"  [Deep Dive] Searching for author: {author}...")
            # Try to find their top 5 books
            temp_page = await context.new_page()
            titles = await scraper.search_author_books_with_links(temp_page, author, max_books=5)
            await temp_page.close()
            
            if titles:
                print(f"    [Success] Found {len(titles)} books for {author}. Scraping...")
                for item in titles:
                    data = await scraper.scrape_goodreads_data(context, item['title'], author)
                    if data:
                        new_rows.append(format_row(data, author))
            else:
                # Try a direct search for anything related to the name
                print(f"    [Retry] Trying direct title-less search for {author}...")
                data = await scraper.scrape_goodreads_data(context, "N/A", author)
                if data:
                    new_rows.append(format_row(data, author))

        if new_rows:
            df = pd.read_excel(CATALOG_FILE)
            df_new = pd.DataFrame(new_rows)
            df_final = pd.concat([df, df_new], ignore_index=True)
            df_final.to_excel(CATALOG_FILE, index=False)
            print(f"Successfully added {len(new_rows)} books for the remaining authors.")

        await browser.close()
        os.startfile(CATALOG_FILE)

if __name__ == "__main__":
    asyncio.run(run_final_recovery())
