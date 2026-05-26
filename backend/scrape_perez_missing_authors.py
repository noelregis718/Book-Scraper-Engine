import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper
from classify_perez import classify_subgenre

EXCEL_FILE = r"E:\Internship\PocketFM\new_books_master_list_perez_literary_scraped.xlsx"
MAX_CONCURRENT = 5

async def process_new_book(context, scraper, title, author, semaphore):
    async with semaphore:
        safe_title = title.encode('ascii', 'ignore').decode('ascii') if title else 'Unknown'
        safe_author = author.encode('ascii', 'ignore').decode('ascii') if author else 'Unknown'
        print(f"  [Scraping New Book] '{safe_title}' by {safe_author}...")
        
        row_data = {
            "Name of Series": title,
            "Author Name": author,
            "Publisher": "Perez Literary",
            "GoodReads series link": "",
            "Number of PRIMARY books in the series": 1,
            "Rating (out of 5) of Primary Book 1": "N/A",
            "Ratings (#) of Primary Book 1": "N/A",
            "Synopsis (if available)": "N/A",
            "Romantasy = Yes or No?": "No",
            "Romantasy Sub-Genre of series": "",
            "Name of agent": "Kristina Perez"
        }
        
        try:
            data = await scraper.scrape_goodreads_data(context, title, author)
            if data:
                link = data.get('GoodReads_Series_URL')
                if not link or link == 'N/A':
                    link = data.get('GoodReads_Book_URL', 'N/A')
                if link == 'N/A': link = ''
                    
                row_data['GoodReads series link'] = link
                row_data['Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
                
                rating = data.get('Book1_Rating', 'N/A')
                if rating == 'N/A': rating = data.get('GoodReads_Rating', 'N/A')
                row_data['Rating (out of 5) of Primary Book 1'] = rating
                
                count = data.get('Book1_Num_Ratings', 'N/A')
                if count == 'N/A': count = data.get('GoodReads_Rating_Count', 'N/A')
                row_data['Ratings (#) of Primary Book 1'] = count
                
                synopsis = data.get('Description', 'N/A')
                row_data['Synopsis (if available)'] = synopsis
                
                # Classify
                combined_text = str(synopsis) + " " + str(title)
                subgenre = classify_subgenre(combined_text)
                
                if subgenre:
                    row_data['Romantasy = Yes or No?'] = "Yes"
                    row_data['Romantasy Sub-Genre of series'] = subgenre
                else:
                    row_data['Romantasy = Yes or No?'] = "No"
                    row_data['Romantasy Sub-Genre of series'] = ""
                
                print(f"  [Done] '{safe_title}' -> {row_data['Romantasy = Yes or No?']} ({row_data['Romantasy Sub-Genre of series']})")
            else:
                print(f"  [Not Found] '{safe_title}'")
        except Exception as e:
            print(f"  [Error] '{safe_title}': {e}")
            
        return row_data

async def run_scrape():
    df = pd.read_excel(EXCEL_FILE)
    
    # Find rows with missing series name
    missing_series_mask = df['Name of Series'].isna() | (df['Name of Series'] == '') | (df['Name of Series'] == 'NaN')
    missing_df = df[missing_series_mask]
    
    authors_to_scrape = missing_df['Author Name'].dropna().unique().tolist()
    print(f"Found {len(authors_to_scrape)} authors with no books: {authors_to_scrape}")
    
    if not authors_to_scrape:
        print("No missing authors to process.")
        return
        
    # Drop these empty rows from the main dataframe
    df = df[~missing_series_mask]
    
    scraper = GoodreadsScraper(headless=False)
    books_to_scrape = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        login_page = await context.new_page()
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        
        print("--- Finding top 3 books for each missing author ---")
        for author in authors_to_scrape:
            safe_author = author.encode('ascii', 'ignore').decode('ascii')
            print(f"Searching author: {safe_author}")
            # Fetch up to 3 books
            top_books = await scraper.search_author_books_with_links(login_page, author, max_books=3)
            
            if not top_books:
                print(f"  No books found for {safe_author}")
                continue
            
            for book in top_books:
                books_to_scrape.append({'title': book['title'], 'author': author})
        
        await login_page.close()
        
        if not books_to_scrape:
            print("Could not find any books for the missing authors.")
        else:
            print(f"--- Scraping {len(books_to_scrape)} books ---")
            semaphore = asyncio.Semaphore(MAX_CONCURRENT)
            tasks = []
            
            for b in books_to_scrape:
                tasks.append(process_new_book(context, scraper, b['title'], b['author'], semaphore))
                
            new_rows = await asyncio.gather(*tasks)
            
            # Append to dataframe
            new_df = pd.DataFrame(new_rows)
            df = pd.concat([df, new_df], ignore_index=True)
            
            print("--- Rebuilding Excel File with new data ---")
            df.to_excel(EXCEL_FILE, index=False)
            
            try:
                from apply_jra_style import apply_styling
                apply_styling(EXCEL_FILE)
                print("--- Applied styling ---")
            except Exception as e:
                print(f"Could not apply styling: {e}")
                
        await browser.close()
    
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
