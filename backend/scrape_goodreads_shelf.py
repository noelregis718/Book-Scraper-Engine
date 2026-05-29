import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper
from classify_perez import classify_subgenre

EXCEL_FILE = r"E:\Internship\PocketFM\Solstice_Romance_Formatted.xlsx"

FINAL_COLUMNS = [
    "Name of Series",
    "Author Name",
    "Publisher",
    "GoodReads series link",
    "Number of PRIMARY books in the series",
    "Rating (out of 5) of Primary Book 1",
    "Ratings (#) of Primary Book 1",
    "Synopsis (if available)",
    "Romantasy = Yes or No?",
    "Romantasy Sub-Genre of series",
    "Name of agent"
]

async def process_book(context, scraper, url):
    print(f"  [Scraping URL] {url}...")
    
    row_data = {
        "Name of Series": "Unknown",
        "Author Name": "Unknown",
        "Publisher": "Solstice Romance",
        "GoodReads series link": "N/A",
        "Number of PRIMARY books in the series": "N/A",
        "Rating (out of 5) of Primary Book 1": "N/A",
        "Ratings (#) of Primary Book 1": "N/A",
        "Synopsis (if available)": "N/A",
        "Romantasy = Yes or No?": "No",
        "Romantasy Sub-Genre of series": "",
        "Name of agent": "N/A"
    }
    
    try:
        # Pass existing_url so it skips searching entirely
        data = await scraper.scrape_goodreads_data(context, title="ShelfBook", author="Unknown", existing_url=url)
        if data:
            title = data.get('Book_Title', "Unknown")
            author = data.get('Author_Found', "Unknown")
            
            row_data['Name of Series'] = title
            row_data['Author Name'] = author
            
            link = data.get('GoodReads_Series_URL')
            if not link or link == 'N/A':
                link = data.get('GoodReads_Book_URL', 'N/A')
            if link == 'N/A': link = ''
                
            row_data['GoodReads series link'] = link if link else "N/A"
            row_data['Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
            
            rating = data.get('Book1_Rating')
            if not rating or rating == 'N/A': rating = data.get('GoodReads_Rating', 'N/A')
            row_data['Rating (out of 5) of Primary Book 1'] = rating
            
            count = data.get('Book1_Num_Ratings')
            if not count or count == 'N/A': count = data.get('GoodReads_Rating_Count', 'N/A')
            row_data['Ratings (#) of Primary Book 1'] = count
            
            synopsis = data.get('Description', 'N/A')
            row_data['Synopsis (if available)'] = synopsis
            
            combined_text = str(synopsis) + " " + str(title)
            subgenre = classify_subgenre(combined_text)
            
            is_romantasy = data.get('Romantasy_Subgenre', 'No')
            if subgenre is not None:
                row_data['Romantasy = Yes or No?'] = "Yes"
                row_data['Romantasy Sub-Genre of series'] = subgenre
            elif is_romantasy == 'Yes':
                row_data['Romantasy = Yes or No?'] = "Yes"
                row_data['Romantasy Sub-Genre of series'] = "High Fantasy Court Adventure"
            
            print(f"  [Done] Parsed details for '{title}' by {author}")
        else:
            print(f"  [Not Found] Details for URL: {url}")
    except Exception as e:
        print(f"  [Error] URL {url}: {e}")
        
    return row_data

async def run_scrape():
    url = "https://www.goodreads.com/shelf/show/solstice-romance"
    print(f"Scraping Shelf: {url}")
    
    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        login_page = await context.new_page()
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        
        print("Extracting book URLs from shelf page...")
        await login_page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # Look for .bookTitle links
        links_data = await login_page.evaluate('''() => {
            let els = document.querySelectorAll('a.bookTitle');
            return Array.from(els).map(a => a.href);
        }''')
        
        if not links_data:
            print("No links found on the shelf. Maybe a CAPTCHA or incorrect selector?")
            await asyncio.sleep(5) # Let user see browser if headless=False
            return
            
        print(f"Found {len(links_data)} books on the shelf.")
        
        # Parallel execution: start all tasks concurrently
        # The scraper creates a new page (tab) for each call
        print(f"Opening {len(links_data)} tabs concurrently...")
        tasks = []
        for book_url in links_data:
            if book_url.startswith("/"):
                book_url = "https://www.goodreads.com" + book_url
            tasks.append(process_book(context, scraper, book_url))
            
        results = await asyncio.gather(*tasks)
        
        print(f"Writing {len(results)} rows to {EXCEL_FILE}...")
        df = pd.DataFrame(results)
        df = df.reindex(columns=FINAL_COLUMNS)
        
        df.to_excel(EXCEL_FILE, index=False)
        
        try:
            from apply_jra_style import apply_styling
            apply_styling(EXCEL_FILE)
            print("Applied styling successfully.")
        except Exception as e:
            print(f"Could not apply styling: {e}")
            
        await login_page.close()
        await browser.close()
        
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
