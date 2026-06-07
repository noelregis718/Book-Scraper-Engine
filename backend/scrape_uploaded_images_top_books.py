import asyncio
import os
import sys
import pandas as pd
import re
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\books_from_uploaded_images.xlsx"

def normalize_title(title):
    if pd.isna(title) or not title:
        return ""
    t = str(title).lower()
    t = re.sub(r'[^\w\s]', '', t)
    return t.strip()

async def scrape_book_directly(context, scraper, title, author, agent, book_link):
    safe_title = title.encode('ascii', 'ignore').decode('ascii') if title else 'Unknown'
    
    row_data = {
        "Name of Series": title,
        "Author Name": author,
        "Publisher": "",
        "GoodReads series link": book_link,
        "Number of PRIMARY books in the series": 1,
        "Rating (out of 5) of Primary Book 1": "N/A",
        "Ratings (#) of Primary Book 1": "N/A",
        "Synopsis (if available)": "N/A",
        "Romantasy = Yes or No?": "No",
        "Romantasy Sub-Genre of series": "",
        "Name of agent": agent
    }
    
    try:
        data = await scraper.scrape_goodreads_data(context, title, author, existing_url=book_link)
        if data:
            link = data.get('GoodReads_Series_URL')
            if not link or link == 'N/A':
                link = data.get('GoodReads_Book_URL', book_link)
            if link == 'N/A': link = book_link
                
            row_data['GoodReads series link'] = link
            row_data['Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
            
            rating = data.get('Book1_Rating', 'N/A')
            if rating == 'N/A': rating = data.get('GoodReads_Rating', 'N/A')
            row_data['Rating (out of 5) of Primary Book 1'] = rating
            
            count = data.get('Book1_Num_Ratings', 'N/A')
            if count == 'N/A': count = data.get('GoodReads_Rating_Count', 'N/A')
            row_data['Ratings (#) of Primary Book 1'] = count
            
            row_data['Synopsis (if available)'] = data.get('Description', 'N/A')
            row_data['Romantasy = Yes or No?'] = data.get('Romantasy_Subgenre', 'No')
            
            genre = data.get("Genre", "N/A")
            subgenre = data.get("Sub_Genre", "N/A")
            genre_str = ""
            if genre != "N/A": genre_str += genre
            if subgenre != "N/A": genre_str += f", {subgenre}" if genre_str else subgenre
            row_data['Romantasy Sub-Genre of series'] = genre_str
            
            print(f"    [Success] Scraped '{safe_title}'")
        else:
            print(f"    [Not Found] No details found for '{safe_title}'")
    except Exception as e:
        err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"    [Error] '{safe_title}': {err_msg}")
        
    return row_data

async def run_scrape():
    df = pd.read_excel(EXCEL_FILE)
    
    # Only process Liza Dawson Associates authors
    liza_authors = df[df['Name of agent'] == 'Liza Dawson Associates']['Author Name'].dropna().unique()
    authors = [a for a in liza_authors if str(a).strip() != '']
        
    print(f"Found {len(authors)} Liza Dawson authors to process.")
    
    scraper = GoodreadsScraper()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        
        for author in authors:
            safe_author = author.encode('ascii', 'ignore').decode('ascii')
            print(f"\n==========================================")
            print(f"Processing Author: {safe_author}")
            print(f"==========================================")
            
            df = pd.read_excel(EXCEL_FILE)
            
            author_rows = df[df['Author Name'] == author]
            agent = ""
            if not author_rows.empty:
                potential_agents = author_rows['Name of agent'].dropna().unique()
                potential_agents = [a for a in potential_agents if str(a).strip() != 'nan' and str(a).strip() != '']
                if potential_agents:
                    agent = potential_agents[0]
            
            print(f"  [Searching] Grabbing top 5 books for {safe_author}...")
            top_books = await scraper.search_author_books_with_links(login_page, author, max_books=5)
            
            if not top_books:
                print(f"  [No Books Found] Goodreads returned 0 books for {safe_author}")
                continue
                
            print(f"  [Scraping] Opening {len(top_books)} books concurrently in 5 tabs at a go...")
            tasks = []
            for b in top_books:
                tasks.append(scrape_book_directly(context, scraper, b['title'], author, agent, b['link']))
                
            new_rows = await asyncio.gather(*tasks)
            
            if new_rows:
                # Update existing rows or append new ones
                for row in new_rows:
                    title = row['Name of Series']
                    norm_title = normalize_title(title)
                    
                    # Find if it exists
                    exists = False
                    for idx, existing_row in df.iterrows():
                        if existing_row['Author Name'] == author:
                            ex_title = normalize_title(existing_row['Name of Series'])
                            if ex_title and norm_title and (ex_title in norm_title or norm_title in ex_title):
                                # Update existing
                                for col, val in row.items():
                                    if col != 'Name of Series' and col != 'Author Name':
                                        df.at[idx, col] = val
                                exists = True
                                break
                    
                    if not exists:
                        new_df = pd.DataFrame([row])
                        df = pd.concat([df, new_df], ignore_index=True)
                
                df.to_excel(EXCEL_FILE, index=False)
                print(f"  [Saved] Updated/Appended {len(new_rows)} books for {safe_author} to Excel.")
        
        await login_page.close()
        await browser.close()
    
    print("\nALL AUTHORS PROCESSED!")
    try:
        sys.path.append(r"E:\Internship\PocketFM")
        import format_excel_script
        print("--- Applied final styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")

if __name__ == '__main__':
    asyncio.run(run_scrape())
