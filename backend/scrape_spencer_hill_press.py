import asyncio
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from playwright.async_api import async_playwright

EXCEL_FILE = r"e:\Internship\PocketFM\Spencer_Hill_Press.xlsx"

def scrape_book(link):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    for attempt in range(3):
        try:
            r = requests.get(link, headers=headers, timeout=15)
            if r.status_code == 503:
                print(f"503 Service Unavailable for {link}. Retrying...")
                time.sleep(2)
                continue
                
            soup = BeautifulSoup(r.content, 'html.parser')
            
            h1 = soup.find('h1')
            title = h1.text.strip() if h1 else link.strip('/').split('/')[-1].replace('-', ' ').title()
            
            if "Service Unavailable" in title:
                print(f"Service Unavailable page hit for {link}. Retrying...")
                time.sleep(2)
                continue
                
            h3_tags = soup.find_all('h3')
            if h3_tags:
                author = h3_tags[0].text.strip()
            else:
                author = "N/A"
                    
            synopsis = "N/A"
            p_tags = soup.find_all('p')
            for p in p_tags:
                text = p.get_text(strip=True)
                if len(text) > 100:
                    synopsis = text
                    break
                    
            return {
                "Name of Series": title,
                "Author Name": author,
                "Publisher": "Spencer Hill Press",
                "GoodReads series link": "N/A",
                "Number of PRIMARY books in the series": "N/A",
                "Rating (out of 5) of Primary Book 1": "N/A",
                "Ratings (#) of Primary Book 1": "N/A",
                "Synopsis (if available)": synopsis,
                "Romantasy = Yes or No?": "N/A",
                "Romantasy Sub-Genre of series": "N/A",
                "Name of agent": "N/A"
            }
        except Exception as e:
            print(f"Error scraping {link}: {e}")
            time.sleep(2)
    return None

async def main_async():
    print("Starting smart scraper for Spencer Hill Press books...")
    
    links = set()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        url = "https://www.spencerhillpress.com/for-readers/titles/"
        print(f"Navigating to {url} and scrolling...")
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        prev_height = -1
        max_scrolls = 50
        scroll_count = 0
        while scroll_count < max_scrolls:
            curr_height = await page.evaluate("document.body.scrollHeight")
            if curr_height == prev_height:
                break
            prev_height = curr_height
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)
            scroll_count += 1
            
        print("Extracting book links...", flush=True)
        
        book_links = await page.locator("a[href^='https://www.spencerhillpress.com/titles/']").evaluate_all(
            "elements => Array.from(new Set(elements.map(e => e.href)))"
        )
        
        for link in book_links:
            if link != "https://www.spencerhillpress.com/titles/":
                links.add(link)
                
        await browser.close()

    links = list(links)
    print(f"Found {len(links)} unique book links. Scraping sequentially to avoid 503 errors...")
    
    books = []
    for link in links:
        res = scrape_book(link)
        if res:
            books.append(res)
            print(f"Scraped: {res['Name of Series']} by {res['Author Name']}")
        time.sleep(0.5)
                
    if os.path.exists(EXCEL_FILE):
        df_existing = pd.read_excel(EXCEL_FILE)
        # Remove any previous "Service Unavailable" entries
        df_existing = df_existing[df_existing['Name of Series'] != 'Service Unavailable']
    else:
        df_existing = pd.DataFrame(columns=[
            "Name of Series", "Author Name", "Publisher", "GoodReads series link", 
            "Number of PRIMARY books in the series", "Rating (out of 5) of Primary Book 1", 
            "Ratings (#) of Primary Book 1", "Synopsis (if available)", 
            "Romantasy = Yes or No?", "Romantasy Sub-Genre of series", "Name of agent"
        ])
        
    df_new = pd.DataFrame(books)
    if not df_new.empty:
        for col in df_existing.columns:
            if col not in df_new.columns:
                df_new[col] = "N/A"
                
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined = df_combined.dropna(subset=['Name of Series'])
        df_combined = df_combined[df_combined['Name of Series'] != 'Service Unavailable']
        df_combined = df_combined.drop_duplicates(subset=['Name of Series'], keep='last')
        
        df_combined.to_excel(EXCEL_FILE, index=False)
        print(f"Successfully saved {len(df_combined)} books to {EXCEL_FILE}")
    else:
        print("No books scraped.")

if __name__ == "__main__":
    asyncio.run(main_async())
