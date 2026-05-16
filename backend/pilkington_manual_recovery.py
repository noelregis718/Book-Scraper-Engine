import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import os
from goodreads_scraper import GoodreadsScraper
from ai_classifier import identify_subgenre

CATALOG_FILE = "Pilkington_Agency_Catalog_Final.xlsx"

MANUAL_BOOKS = [
    {"title": "Hate You to Love You", "author": "Joshua Hortinela"},
    {"title": "Where Truth Ends", "author": "Mark Smith"},
    {"title": "The Forsaken", "author": "Matt Rogers"},
    {"title": "The Secrets of Strangers", "author": "Jess Kitching"},
    {"title": "Screen Smart Children", "author": "Dr Mark Williams & Gavin McCormack"},
    {"title": "The Line Up", "author": "Nicholas Timms"}
]

def format_row(data, author):
    # AGGRESSIVE LINK SAVING
    link = data.get('GoodReads_Series_URL')
    if not link or link == "N/A":
        link = data.get('GoodReads_Book_URL')
    
    # Classification
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

async def run_recovery():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = GoodreadsScraper(headless=False)
        
        # Login
        print("[System] Performing Mandatory Login for Recovery...")
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        await login_page.close()

        new_rows = []
        for item in MANUAL_BOOKS:
            print(f"  [Recovery] Searching for: {item['title']} by {item['author']}...")
            data = await scraper.scrape_goodreads_data(context, item['title'], item['author'])
            if data:
                new_rows.append(format_row(data, item['author']))
                print(f"    [Success] Captured {item['title']}.")
            else:
                print(f"    [Skip] Could not find {item['title']}.")

        if new_rows:
            if os.path.exists(CATALOG_FILE):
                df = pd.read_excel(CATALOG_FILE)
                # Filter out the NaN rows if any
                df = df[df['Author Name'].notna()]
                df_new = pd.DataFrame(new_rows)
                df_final = pd.concat([df, df_new], ignore_index=True)
                df_final.to_excel(CATALOG_FILE, index=False)
                print(f"Successfully added {len(new_rows)} recovered books to {CATALOG_FILE}")
            else:
                pd.DataFrame(new_rows).to_excel(CATALOG_FILE, index=False)

        await browser.close()
        os.startfile(CATALOG_FILE)

if __name__ == "__main__":
    asyncio.run(run_recovery())
