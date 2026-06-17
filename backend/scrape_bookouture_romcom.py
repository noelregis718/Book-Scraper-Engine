import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from bs4 import BeautifulSoup
import os

async def run_scraper():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Standard_11_Column_Format_2.xlsx')
    
    print("Launching visible browser for Bookouture Romantic Comedy...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        url = "https://bookouture.com/books/?genre=romantic-comedy"
        print(f"Navigating to {url}")
        await page.goto(url)
        
        print("Waiting for Cloudflare and initial load... (Solve CAPTCHA if needed)")
        try:
            await page.wait_for_load_state("networkidle", timeout=60000)
        except:
            pass
            
        print("Scrolling to load all books...")
        current_height = await page.evaluate("document.body.scrollHeight")
        scroll_attempts = 0
        
        while scroll_attempts < 100:
            try:
                load_more = await page.query_selector(".facetwp-load-more, button:has-text('Load More')")
                if load_more and await load_more.is_visible():
                    await load_more.click()
                    await asyncio.sleep(4)
                    continue
            except: pass
            
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == current_height:
                print("Reached the bottom.")
                break
            current_height = new_height
            scroll_attempts += 1

        print("Extraction phase...")
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Use the exact selectors that worked for the Romance page
        authors_elements = soup.find_all('p', class_='MannequinContentPreview__book__author')
        
        books_data = []
        seen = set()
        
        # Check if we already have the titles from the Excel to prevent duplicates if any overlap
        try:
            existing_df = pd.read_excel(excel_path)
            existing_titles = set(existing_df['Name of Series'].dropna().str.strip().str.lower().tolist())
        except:
            existing_titles = set()
            existing_df = None

        for author_elem in authors_elements:
            author = author_elem.get_text(strip=True)
            title_elem = author_elem.find_previous_sibling('h4')
            if title_elem:
                title = title_elem.get_text(strip=True)
                
                # Check for absolute duplicates inside this run
                if title not in seen:
                    seen.add(title)
                    # Check for duplicates across the existing Excel sheet
                    if title.strip().lower() not in existing_titles:
                        books_data.append({
                            'Name of Series': title,
                            'Author Name': author,
                            'Publisher': 'Bookouture',
                            'GoodReads series link': 'N/A',
                            'Number of PRIMARY books in the series': 'N/A',
                            'Rating (out of 5) of Primary Book 1': 'N/A',
                            'Ratings (#) of Primary Book 1': 'N/A',
                            'Synopsis (if available)': 'N/A',
                            'Romantasy = Yes or No?': 'N/A',
                            'Romantasy Sub-Genre of series': 'N/A',
                            'Name of agent': 'N/A'
                        })
                        existing_titles.add(title.strip().lower())

        print(f"Extracted {len(books_data)} new Romantic Comedy books.")
        
        if len(books_data) > 0:
            if existing_df is not None:
                new_df = pd.DataFrame(books_data)
                df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                df = pd.DataFrame(books_data)
                
            df.to_excel(excel_path, index=False)
            print("Saved to Excel.")
        else:
            print("Failed to extract any new books.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
