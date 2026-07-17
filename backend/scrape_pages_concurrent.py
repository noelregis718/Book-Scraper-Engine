import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
import re
from bs4 import BeautifulSoup

async def process_row(index, row, df, context, semaphore, excel_path, lock):
    title = str(row.get("Book 1 Title", "")).strip()
    url = str(row.get("Goodreads Series URL", "")).strip()
    existing_pages = str(row.get("Number of Pages in Book 1", "")).strip()
    
    # Skip invalid rows or rows without URLs
    if not title or title.lower() == 'nan' or not url or url.lower() == 'nan' or url == 'N/A':
        return
        
    # Skip if we already have a valid number
    if existing_pages and existing_pages.lower() != 'nan' and existing_pages != 'None':
        if re.match(r'^\d+(\.\d+)?$', existing_pages):
            return

    async with semaphore:
        print(f"[{index+1}] Opening tab for: {title}", flush=True)
        page = await context.new_page()
        try:
            # Go directly to the URL we scraped previously
            await page.goto(url, wait_until="domcontentloaded", timeout=90000)
            await asyncio.sleep(2) # Let the page settle
            
            # If the URL happens to be a Series page, we must click the first book to get page counts
            if "/series/" in page.url:
                book_links = await page.query_selector_all('a[href*="/book/show/"]')
                book_url = None
                for link in book_links:
                    href = await link.evaluate("el => el.href")
                    if re.search(r'/show/\d+', href):
                        book_url = href
                        break
                
                # If strict regex didn't find it, just grab the first book link
                if not book_url and book_links:
                    book_url = await book_links[0].evaluate("el => el.href")
                        
                if book_url:
                    print(f"  [{index+1}] Navigating from series to Book 1: {book_url}", flush=True)
                    await page.goto(book_url, wait_until="domcontentloaded", timeout=90000)
                    await asyncio.sleep(3)
                else:
                    print(f"  [{index+1}] Failed to find book link on series page.", flush=True)
            
            # Now we should be on the specific Book page. Find the page count element
            pages_element = await page.query_selector("[data-testid='pagesFormat'], p[data-testid='pagesFormat'], .pagesFormat")
            num_pages = None
            
            if pages_element:
                pages_text = await pages_element.inner_text()
                match = re.search(r'(\d+)\s*pages', pages_text, re.IGNORECASE)
                if match:
                    num_pages = match.group(1)
            
            if not num_pages:
                # Scroll down slowly to ensure any lazy-loaded elements pop in
                await page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(1)
                await page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(1)

                # Robust Fallback: Scrape all text and look for "277 pages"
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text(separator=' ')
                matches = re.findall(r'(\d+)\s*pages', text, re.IGNORECASE)
                for m in matches:
                    if 10 < int(m) < 4000:  # Reasonable page count bounds
                        num_pages = m
                        break

            if num_pages:
                print(f"  [{index+1}] Success: {num_pages} pages found for '{title}'!", flush=True)
                async with lock:
                    df.at[index, "Number of Pages in Book 1"] = float(num_pages)
                    df.to_excel(excel_path, index=False)
            else:
                print(f"  [{index+1}] Could not find pages element for '{title}'. (CAPTCHA or wrong page layout?)")
        except Exception as e:
            print(f"  [{index+1}] Error for '{title}': {e}")
        finally:
            await page.close()

async def run_scraper():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(workspace_dir, "Small_Publishers_Crime_Scraped.xlsx")
    
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    df = pd.read_excel(input_path)
    
    # Fix pandas incompatible dtype issue when assigning strings/floats to NaN
    df["Number of Pages in Book 1"] = df["Number of Pages in Book 1"].astype(object)
    
    # Allow 4 browser tabs at once to reduce timeout crashes
    semaphore = asyncio.Semaphore(4)
    lock = asyncio.Lock()
    
    async with async_playwright() as p:
        # Launch headed browser so the user can see it and solve CAPTCHAs manually if needed
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        tasks = []
        for index, row in df.iterrows():
            tasks.append(process_row(index, row, df, context, semaphore, input_path, lock))
            
        print(f"Starting 4 concurrent tabs to extract remaining page counts...", flush=True)
        await asyncio.gather(*tasks)
        
        await browser.close()
        
    print("\nScraping complete. Final dataset saved.", flush=True)
    
    # Clean up styling so the excel sheet looks good
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from apply_premium_style_crime import apply_premium_fixed_style
        apply_premium_fixed_style(input_path)
    except Exception as e:
        pass

if __name__ == "__main__":
    asyncio.run(run_scraper())
