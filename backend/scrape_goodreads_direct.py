import asyncio
import pandas as pd
import os
import sys
import json
import random
import re
from playwright.async_api import async_playwright

col_url = 'GoodReads_Series_URL'
col_num_books = 'Num_Primary_Books'
col_pages = 'Total_Pages_Primary_Books'
col_b1_rate = 'Book1_Rating'
col_b1_num = 'Book1_Num_Ratings'

async def process_row(context, df, idx, target_path, lock, semaphore):
    async with semaphore:
        page = await context.new_page()
        try:
            series_name = str(df.at[idx, 'Series Name'])
            author_name = str(df.at[idx, 'Author Name'])
            book_title = str(df.at[idx, 'Representative Book Title']).split('(')[0].strip()
            
            print(f"[{idx}] Researching: {book_title} by {author_name}")
            
            search_query = f"{book_title} {author_name}"
            search_url = f"https://www.goodreads.com/search?q={search_query.replace(' ', '+')}"
            await page.goto(search_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(random.randint(2000, 4000))
            
            try:
                await page.click("a.bookTitle", timeout=5000)
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(random.randint(2000, 4000))
            except:
                print(f"[{idx}] Could not find book in search results.")
                async with lock:
                    df.at[idx, col_url] = ""
                    df.to_excel(target_path, index=False)
                return
                
            book_data = await page.evaluate('''() => {
                let rating = ""; let numRatings = ""; let pages = "0";
                let ratingEl = document.querySelector('div.RatingStatistics__rating');
                if (ratingEl) rating = ratingEl.innerText;
                let numEl = document.querySelector('[data-testid="ratingsCount"]');
                if (numEl) numRatings = numEl.innerText.split(' ')[0];
                let pageEl = document.querySelector('p[data-testid="pagesFormat"]');
                if (pageEl) {
                    let match = pageEl.innerText.match(/(\\d+)\\s+pages/);
                    if (match) pages = match[1];
                }
                return {rating, numRatings, pages};
            }''')
            
            clean_num_ratings = re.sub(r'[^0-9]', '', book_data['numRatings'])
            
            async with lock:
                df.at[idx, col_b1_rate] = book_data['rating']
                df.at[idx, col_b1_num] = clean_num_ratings
            
            try:
                series_href = await page.evaluate('''() => {
                    let links = document.querySelectorAll('a');
                    for (let a of links) {
                        if (a.href.includes('/series/')) return a.href;
                    }
                    return null;
                }''')
                
                if series_href:
                    await page.goto(series_href, wait_until="domcontentloaded")
                    await page.wait_for_timeout(random.randint(2000, 4000))
                else:
                    print(f"[{idx}] No series link on first try. Falling back to highest rated book search...")
                    raise Exception("FallbackTrigger")
            except:
                # FALLBACK LOGIC
                fallback_search_url = f"https://www.goodreads.com/search?q={book_title.replace(' ', '+')}"
                await page.goto(fallback_search_url, wait_until="domcontentloaded")
                await page.wait_for_timeout(random.randint(2000, 4000))
                
                best_href = await page.evaluate('''() => {
                    let bestHref = null; let maxRatings = -1;
                    let rows = document.querySelectorAll('tr[itemtype="http://schema.org/Book"]');
                    for (let row of rows) {
                        let link = row.querySelector('a.bookTitle');
                        let ratingSpan = row.querySelector('span.minirating');
                        if (link && ratingSpan) {
                            let text = ratingSpan.innerText;
                            let match = text.match(/—\\s*([0-9,]+)\\s*ratings/);
                            if (match) {
                                let num = parseInt(match[1].replace(/,/g, ''));
                                if (num > maxRatings) { maxRatings = num; bestHref = link.href; }
                            }
                        }
                    }
                    return bestHref;
                }''')
                
                if best_href:
                    print(f"[{idx}] Found highest rated fallback book. Navigating...")
                    await page.goto(best_href, wait_until="domcontentloaded")
                    await page.wait_for_timeout(random.randint(2000, 4000))
                    
                    book_data = await page.evaluate('''() => {
                        let rating = ""; let numRatings = ""; let pages = "0";
                        let ratingEl = document.querySelector('div.RatingStatistics__rating');
                        if (ratingEl) rating = ratingEl.innerText;
                        let numEl = document.querySelector('[data-testid="ratingsCount"]');
                        if (numEl) numRatings = numEl.innerText.split(' ')[0];
                        let pageEl = document.querySelector('p[data-testid="pagesFormat"]');
                        if (pageEl) {
                            let match = pageEl.innerText.match(/(\\d+)\\s+pages/);
                            if (match) pages = match[1];
                        }
                        return {rating, numRatings, pages};
                    }''')
                    clean_num_ratings = re.sub(r'[^0-9]', '', book_data['numRatings'])
                    
                    async with lock:
                        df.at[idx, col_b1_rate] = book_data['rating']
                        df.at[idx, col_b1_num] = clean_num_ratings
                    
                    series_href = await page.evaluate('''() => {
                        let links = document.querySelectorAll('a');
                        for (let a of links) {
                            if (a.href.includes('/series/')) return a.href;
                        }
                        return null;
                    }''')
                    
                    if series_href:
                        await page.goto(series_href, wait_until="domcontentloaded")
                        await page.wait_for_timeout(random.randint(2000, 4000))
                    else:
                        print(f"[{idx}] Still no series link on fallback book. Using Book URL instead.")
                        async with lock:
                            df.at[idx, col_url] = page.url
                            df.at[idx, col_num_books] = 1
                            try:
                                df.at[idx, col_pages] = int(book_data['pages']) if int(book_data['pages']) > 0 else ""
                            except:
                                df.at[idx, col_pages] = ""
                            df.to_excel(target_path, index=False)
                        print(f"Extracted Standalone -> Rating: {book_data['rating']}, NumRatings: {clean_num_ratings}, URL: {page.url}")
                        return
                else:
                    print(f"[{idx}] Fallback search yielded no books.")
                    async with lock:
                        df.at[idx, col_url] = ""
                        df.to_excel(target_path, index=False)
                    return
                
            series_data = await page.evaluate('''() => {
                let url = window.location.href; let numBooks = "";
                let text = document.body.innerText;
                let match = text.match(/(\\d+)\\s+primary works/);
                if (match) numBooks = match[1];
                return {url, numBooks};
            }''')
            
            async with lock:
                df.at[idx, col_url] = series_data['url']
                df.at[idx, col_num_books] = series_data['numBooks']
                try:
                    num_bks = int(series_data['numBooks'])
                    b1_pages = int(book_data['pages'])
                    if num_bks > 0 and b1_pages > 0:
                        df.at[idx, col_pages] = num_bks * b1_pages
                    else:
                        df.at[idx, col_pages] = ""
                except:
                    df.at[idx, col_pages] = ""
                
                print(f"Extracted -> Rating: {book_data['rating']}, NumRatings: {clean_num_ratings}, URL: {series_data['url']}")
                df.to_excel(target_path, index=False)
                
        except Exception as e:
            print(f"[{idx}] Error during scraping:", e)
        finally:
            await page.close()

async def run_scraper():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_path = os.path.join(base_dir, 'CT_Series_Base_Part_6_of_6.xlsx')
    user_data_dir = os.path.join(base_dir, 'playwright_goodreads_profile')
    
    print(f"Loading {target_path}...")
    df = pd.read_excel(target_path)
    for c in [col_url, col_num_books, col_pages, col_b1_rate, col_b1_num]:
        if c not in df.columns:
            df[c] = ''
        df[c] = df[c].astype(object)
        
    # FORCE SCRAPE FIRST 10 ROWS
    indices_to_scrape = list(range(10))
            
    print(f"Found {len(indices_to_scrape)} series needing direct Goodreads research.")
    if not indices_to_scrape:
        print("No rows left to scrape!")
        return

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            viewport={'width': 1280, 'height': 800}
        )
        
        login_flag = os.path.join(base_dir, 'goodreads_login_done.txt')
        if not os.path.exists(login_flag):
            page = await context.new_page()
            print("\\n*** AUTOMATED LOGIN ***")
            print("Loading credentials...")
            creds_path = os.path.join(base_dir, 'backend', 'gr_creds.json')
            with open(creds_path, 'r') as f:
                creds = json.load(f)
                
            print("Navigating to Goodreads Login...")
            await page.goto("https://www.goodreads.com/user/sign_in")
            try:
                await page.click("text='Sign in with email'", timeout=5000)
                await page.wait_for_load_state("domcontentloaded")
            except:
                pass
            print("Filling credentials...")
            try:
                await page.fill("input[type='email']", creds['email'], timeout=5000)
                await page.fill("input[type='password']", creds['password'], timeout=5000)
                await page.click("input[id='signInSubmit']", timeout=5000)
            except:
                try:
                    await page.fill("#user_email", creds['email'], timeout=5000)
                    await page.fill("#user_password", creds['password'], timeout=5000)
                    await page.click("input[name='commit']", timeout=5000)
                except Exception as e:
                    print("Failed to auto-login. Selectors might have changed.", e)
            print("Waiting for login to complete...")
            await page.wait_for_timeout(5000)
            with open(login_flag, 'w') as f:
                f.write('done')
            print("Login automated! Continuing...\\n")
            await page.close()
            
        semaphore = asyncio.Semaphore(5)
        lock = asyncio.Lock()
        
        print(f"Starting CONCURRENT scraper for {len(indices_to_scrape)} rows (5 tabs at once)...")
        tasks = []
        for idx in indices_to_scrape:
            tasks.append(asyncio.create_task(process_row(context, df, idx, target_path, lock, semaphore)))
            
        await asyncio.gather(*tasks)
        await context.close()
        
if __name__ == "__main__":
    asyncio.run(run_scraper())
