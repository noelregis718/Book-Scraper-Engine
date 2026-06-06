import asyncio
import os
import sys
import pandas as pd
import re
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\rebecca_freidmann_authors.xlsx"

IMAGE_BOOKS = [
    {"title": "Fire Exit", "author": "Morgan Talty"},
    {"title": "Runaway Love", "author": "Melanie Harlow"},
    {"title": "Running", "author": "Cara Hoffman"},
    {"title": "Biology Lessons", "author": "Melissa Kantor"},
    {"title": "White Horse", "author": "Erika T. Wurth"},
    {"title": "Starlings", "author": "Amanda Linsmeier"},
    {"title": "Be Safe I Love You", "author": "Cara Hoffman"},
    {"title": "Stir: My Broken Brain and the Meals That Brought Me Home", "author": "Jessica Fechtor"},
    {"title": "The Scapegracers", "author": "Hannah Abigail Clarke"},
    {"title": "The Sex Myth", "author": "Rachel Hills"},
    {"title": "Joseph Smith for President", "author": "Spencer W. McBride"},
    {"title": "The Black Nile", "author": "Dan Morrison"},
    {"title": "The American Way of Eating", "author": "Tracie McMillan"},
    {"title": "Peaceful Parent, Happy Siblings", "author": "Laura Markham"}, # Removed Dr. for better search
    {"title": "Maybe One Day", "author": "Melissa Kantor"},
    {"title": "Opium Nation", "author": "Fariba Nawa"},
    {"title": "Eat the City", "author": "Robin Shulman"},
    {"title": "Among Thieves", "author": "M. J. Kuhn"}
]

async def process_book(context, scraper, title, author):
    safe_title = title.encode('ascii', 'ignore').decode('ascii')
    safe_author = author.encode('ascii', 'ignore').decode('ascii')
    print(f"    [Scraping Book] '{safe_title}' by {safe_author}...")
    
    row_data = {
        "Name of Series": title,
        "Author Name": author,
        "Publisher": "",
        "GoodReads series link": "",
        "Number of PRIMARY books in the series": 1,
        "Rating (out of 5) of Primary Book 1": "N/A",
        "Ratings (#) of Primary Book 1": "N/A",
        "Synopsis (if available)": "N/A",
        "Romantasy = Yes or No?": "No",
        "Romantasy Sub-Genre of series": "",
        "Name of agent": "Rebecca Freidmann"
    }
    
    try:
        data = await scraper.scrape_goodreads_data(context, title, author, existing_url=None)
        if data:
            found_link = data.get('GoodReads_Series_URL')
            if not found_link or found_link == 'N/A':
                found_link = data.get('GoodReads_Book_URL', 'N/A')
            if found_link == 'N/A': found_link = ''
                
            row_data['GoodReads series link'] = found_link
            row_data['Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
            
            rating = data.get('Book1_Rating', 'N/A')
            if rating == 'N/A': rating = data.get('GoodReads_Rating', 'N/A')
            row_data['Rating (out of 5) of Primary Book 1'] = rating
            
            count = data.get('Book1_Num_Ratings', 'N/A')
            if count == 'N/A': count = data.get('GoodReads_Rating_Count', 'N/A')
            row_data['Ratings (#) of Primary Book 1'] = count
            
            row_data['Synopsis (if available)'] = data.get('Description', 'N/A')
            row_data['Romantasy = Yes or No?'] = data.get('Romantasy_Subgenre', 'No')
            row_data['Romantasy Sub-Genre of series'] = data.get('Sub_Genre', '')
            
            print(f"    [Done] '{safe_title}'")
        else:
            print(f"    [Not Found] '{safe_title}'")
    except Exception as e:
        err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"    [Error] '{safe_title}': {err_msg}")
        
    return row_data

async def run_scrape():
    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        chunk_size = 3
        for i in range(0, len(IMAGE_BOOKS), chunk_size):
            chunk = IMAGE_BOOKS[i:i+chunk_size]
            print(f"\n--- Processing Image Batch {i//chunk_size + 1} ---")
            
            scrape_tasks = [process_book(context, scraper, b['title'], b['author']) for b in chunk]
            scraped_rows = await asyncio.gather(*scrape_tasks)
            
            df = pd.read_excel(EXCEL_FILE)
            new_df = pd.DataFrame(scraped_rows)
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_excel(EXCEL_FILE, index=False)
            print("  Batch saved to Excel.")
            
        await browser.close()
        
    try:
        from style_rebecca_freidmann import apply_styling
        apply_styling(EXCEL_FILE)
    except: pass
    
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
