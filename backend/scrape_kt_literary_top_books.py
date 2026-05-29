import asyncio
import os
import sys
import pandas as pd
import re
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper
from classify_perez import classify_subgenre

EXCEL_FILE = r"E:\Internship\PocketFM\KT_Literary_Merged_Formatted.xlsx"
MAX_CONCURRENT = 5

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

def normalize_title(title):
    if pd.isna(title) or not title:
        return ""
    t = str(title).lower()
    t = re.sub(r'[^\w\s]', '', t)
    return t.strip()

async def process_new_book(context, scraper, title, author, agent, semaphore):
    async with semaphore:
        safe_title = title.encode('ascii', 'ignore').decode('ascii') if title else 'Unknown'
        safe_author = author.encode('ascii', 'ignore').decode('ascii') if author else 'Unknown'
        print(f"  [Scraping New Book] '{safe_title}' by {safe_author}...")
        
        row_data = {
            "Name of Series": title,
            "Author Name": author,
            "Publisher": "KT Literary Agency",
            "GoodReads series link": "N/A",
            "Number of PRIMARY books in the series": "N/A",
            "Rating (out of 5) of Primary Book 1": "N/A",
            "Ratings (#) of Primary Book 1": "N/A",
            "Synopsis (if available)": "N/A",
            "Romantasy = Yes or No?": "No",
            "Romantasy Sub-Genre of series": "",
            "Name of agent": agent
        }
        
        try:
            data = await scraper.scrape_goodreads_data(context, title, author)
            if data:
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
                
                # Classify the subgenre based on synopsis and title
                combined_text = str(synopsis) + " " + str(title)
                subgenre = classify_subgenre(combined_text)
                
                is_romantasy = data.get('Romantasy_Subgenre', 'No')
                if subgenre is not None:
                    row_data['Romantasy = Yes or No?'] = "Yes"
                    row_data['Romantasy Sub-Genre of series'] = subgenre
                elif is_romantasy == 'Yes':
                    row_data['Romantasy = Yes or No?'] = "Yes"
                    row_data['Romantasy Sub-Genre of series'] = "High Fantasy Court Adventure"
                else:
                    row_data['Romantasy = Yes or No?'] = "No"
                    row_data['Romantasy Sub-Genre of series'] = ""
                
                print(f"  [Done] Parsed details for '{safe_title}'")
            else:
                print(f"  [Not Found] Details for '{safe_title}'")
        except Exception as e:
            err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            print(f"  [Error] '{safe_title}': {err_msg}")
            
        return row_data

async def run_scrape():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return
        
    df = pd.read_excel(EXCEL_FILE)
    
    # Get unique authors and map them to their agent
    author_agent_map = {}
    for _, row in df.iterrows():
        author = row.get('Author Name')
        agent = row.get('Name of agent', 'N/A')
        if pd.notna(author) and str(author).strip() != '' and str(author).lower() != 'nan':
            if author not in author_agent_map:
                author_agent_map[author] = agent
                
    authors = list(author_agent_map.keys())
    print(f"Found {len(authors)} unique authors.")
    
    scraper = GoodreadsScraper(headless=False)
    new_books_to_scrape = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        login_page = await context.new_page()
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        
        print("--- Finding the top 3 books for each author to add if missing ---")
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        for author in authors:
            safe_author = author.encode('ascii', 'ignore').decode('ascii')
            print(f"\n--- Checking author: {safe_author} ---")
            
            # Request up to 3 books
            top_books = await scraper.search_author_books_with_links(login_page, author, max_books=3)
            
            if not top_books:
                print(f"  No books found on Goodreads for {safe_author}")
                continue
                
            # Reload df to get latest state just in case
            current_df = pd.read_excel(EXCEL_FILE)
            existing_titles = current_df[current_df['Author Name'] == author]['Name of Series'].apply(normalize_title).tolist()
            
            author_books_to_scrape = []
            books_processed = 0
            for book in top_books:
                found_title = book['title']
                norm_found = normalize_title(found_title)
                
                exists = False
                for ex in existing_titles:
                    if not ex or not norm_found: continue
                    if ex in norm_found or norm_found in ex:
                        exists = True
                        break
                        
                if exists:
                    print(f"  [Skipping] '{found_title.encode('ascii', 'ignore').decode('ascii')}' - Already in sheet")
                else:
                    print(f"  [Adding to Queue] '{found_title.encode('ascii', 'ignore').decode('ascii')}'")
                    author_books_to_scrape.append({'title': found_title, 'author': author, 'agent': author_agent_map[author]})
                    
                books_processed += 1
                if books_processed >= 3:
                    break
                    
            if author_books_to_scrape:
                print(f"  Scraping details for {len(author_books_to_scrape)} new books for {safe_author}...")
                tasks = []
                for b in author_books_to_scrape:
                    tasks.append(process_new_book(context, scraper, b['title'], b['author'], b['agent'], semaphore))
                
                new_rows = await asyncio.gather(*tasks)
                
                new_df = pd.DataFrame(new_rows)
                new_df = new_df.reindex(columns=FINAL_COLUMNS)
                
                # Append to current_df
                current_df = pd.concat([current_df, new_df], ignore_index=True)
                current_df = current_df.drop_duplicates(subset=["Name of Series", "Author Name"], keep='first')
                
                print(f"  Saving {safe_author}'s books to Excel incrementally...")
                current_df.to_excel(EXCEL_FILE, index=False)
                
                try:
                    from apply_jra_style import apply_styling
                    apply_styling(EXCEL_FILE)
                    print(f"  Applied styling for {safe_author}'s update.")
                except Exception as e:
                    print(f"  Could not apply styling: {e}")
            else:
                print(f"  All top 3 books for {safe_author} are already in the sheet!")
        
        await login_page.close()
        await browser.close()
            
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
