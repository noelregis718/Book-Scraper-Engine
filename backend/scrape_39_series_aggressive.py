import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
import re
import json

def clean_text(text):
    if not text: return ""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

async def process_row(index, row, df, context, semaphore, excel_path, lock):
    series_name = str(row.get("Name of Series", "")).strip()
    series_url = str(row.get("GoodReads series link", "")).strip()
    
    if not series_url or not series_url.startswith('http'):
        return

    # Skip if we already scraped it
    existing_rating = str(row.get("Rating (out of 5) of Primary Book 1", "")).strip()
    if existing_rating and existing_rating.lower() != 'nan' and existing_rating != 'None':
        return

    async with semaphore:
        print(f"[{index+1}] Processing Series: '{series_name}'", flush=True)
        page = await context.new_page()
        try:
            # 1. Go to Series Page
            print(f"  [{index+1}] Navigating to Series URL: {series_url}", flush=True)
            await page.goto(series_url, wait_until="domcontentloaded", timeout=90000)
            
            # Extract Number of Primary Books
            content = await page.content()
            num_primary = "N/A"
            m = re.search(r'(\d+)\s+primary\s+works', content, re.IGNORECASE)
            if m:
                num_primary = m.group(1)
            
            # Find Book 1 Link
            book_links = await page.query_selector_all('a[href*="/book/show/"]')
            book1_url = None
            for link in book_links:
                href = await link.evaluate("el => el.href")
                if re.search(r'/show/\d+', href):
                    book1_url = href
                    break
                    
            if not book1_url:
                print(f"  [{index+1}] Could not find Book 1 link on the series page.", flush=True)
                return
                
            # 2. Go to Book 1 Page
            print(f"  [{index+1}] Found Book 1 link. Navigating to Book Page...", flush=True)
            await page.goto(book1_url, wait_until="domcontentloaded", timeout=90000)
            await asyncio.sleep(1)
            
            # Extract Details
            avg_rating = "N/A"
            rating_count = "N/A"
            try:
                ld_el = await page.query_selector('script[type="application/ld+json"]')
                if ld_el:
                    ld_data = json.loads(await ld_el.inner_text())
                    if isinstance(ld_data, list): ld_data = ld_data[0]
                    avg_rating = str(ld_data.get('aggregateRating', {}).get('ratingValue', 'N/A'))
                    rating_count = str(ld_data.get('aggregateRating', {}).get('ratingCount', 'N/A'))
            except: pass

            description = "N/A"
            desc_el = await page.query_selector('[data-testid="description"] .Formatted, .readable')
            if desc_el: description = clean_text(await desc_el.inner_text())

            # 3. Save to DataFrame safely
            async with lock:
                df.at[index, "Number of PRIMARY books in the series"] = num_primary
                df.at[index, "Rating (out of 5) of Primary Book 1"] = avg_rating
                df.at[index, "Ratings (#) of Primary Book 1"] = rating_count
                df.at[index, "Synopsis (if available)"] = description
                df.at[index, "Book goodreads link"] = page.url
                df.to_excel(excel_path, index=False)
                
            print(f"  [{index+1}] Success for '{series_name}'. Rating: {avg_rating}, Primary Books: {num_primary}", flush=True)

        except Exception as e:
            print(f"  [{index+1}] Error for '{series_name}': {e}", flush=True)
        finally:
            await page.close()

async def run_scraper():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(workspace_dir, "Selected_Titles_Blank_Template.xlsx")
    
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    df = pd.read_excel(input_path)
    
    # Allow 8 tabs at once as requested
    semaphore = asyncio.Semaphore(8)
    lock = asyncio.Lock()
    
    async with async_playwright() as p:
        # Launch browser headless=False so user can see it
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        tasks = []
        for index, row in df.iterrows():
            tasks.append(process_row(index, row, df, context, semaphore, input_path, lock))
            
        print(f"\nStarting aggressive series scraper for {len(df)} series with 8 tabs...", flush=True)
        await asyncio.gather(*tasks)
        
        await browser.close()
        
    # Reapply styling at the end
    try:
        from apply_premium_style_crime import apply_premium_fixed_style
        apply_premium_fixed_style(input_path)
    except:
        pass
    print("\nScraping complete. Final dataset saved.", flush=True)

if __name__ == "__main__":
    asyncio.run(run_scraper())
