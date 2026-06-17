import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import sys
import os
import requests
from bs4 import BeautifulSoup
import re
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

def clean_title_for_search(title):
    # Remove subtitles after colon
    clean = title.split(':')[0]
    # Remove parens
    clean = re.sub(r'\(.*?\)', '', clean)
    clean = re.sub(r'Book [IVX]+', '', clean)
    return clean.strip()

def search_duckduckgo(query):
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    data = {"q": query}
    try:
        r = requests.post(url, headers=headers, data=data, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all('a', class_='result__url'):
            link = a.get('href', '')
            if 'goodreads.com/book/show' in link or 'goodreads.com' in a.text:
                return "https://" + a.text.strip()
    except Exception as e:
        print(f"Error querying DDG: {e}")
    return None

async def run_scraper():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Standard_11_Column_Format_2.xlsx')
    
    print(f"Loading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)

    missing_mask = df['GoodReads series link'].isna() | (df['GoodReads series link'] == 'N/A') | (df['Synopsis (if available)'] == 'N/A')
    missing_indices = df.index[missing_mask].tolist()
    
    print(f"Found {len(missing_indices)} books missing full Goodreads data.")
    
    if len(missing_indices) == 0:
        print("No missing data found!")
        return

    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Login
        await scraper.login_to_goodreads(page)
        await page.close()
        
        for idx in missing_indices:
            raw_title = str(df.at[idx, 'Name of Series'])
            author = str(df.at[idx, 'Author Name']) if pd.notna(df.at[idx, 'Author Name']) else ""
            
            clean_title = clean_title_for_search(raw_title)
            query = f'site:goodreads.com/book/show/ "{clean_title}" {author}'.strip()
            
            print(f"\n[Fallback Scraper] Searching DDG for: {query}")
            link = search_duckduckgo(query)
            
            if link:
                if not link.startswith('http'): link = 'https://' + link
                print(f"  -> Found Direct URL: {link}")
                
                print(f"  -> Diving into Goodreads to extract full details...")
                data = await scraper.scrape_goodreads_data(context, title=raw_title, author=author, existing_url=link)
                
                if data:
                    df.at[idx, 'GoodReads series link'] = data.get("GoodReads_Book_URL", link)
                    df.at[idx, 'Number of PRIMARY books in the series'] = data.get("Num_Primary_Books", "N/A")
                    df.at[idx, 'Rating (out of 5) of Primary Book 1'] = data.get("Book1_Rating", "N/A")
                    df.at[idx, 'Ratings (#) of Primary Book 1'] = data.get("Book1_Num_Ratings", "N/A")
                    df.at[idx, 'Synopsis (if available)'] = data.get("Description", "N/A")
                    print(f"      [Success] Full details extracted for '{raw_title}'!")
                else:
                    # Save the link at least
                    df.at[idx, 'GoodReads series link'] = link
                    print(f"      [Partial] Could only save the link.")
            else:
                print(f"  -> [Failed] Could not locate URL for '{raw_title}' anywhere.")
                
            df.to_excel(excel_path, index=False)
            time.sleep(2)
            
        print(f"\n--- Scrape Complete! Excel file updated. ---")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
