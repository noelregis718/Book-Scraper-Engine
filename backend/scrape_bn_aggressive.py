import asyncio
import os
import sys
import pandas as pd
import re
import urllib.parse
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

EXCEL_FILE = r"E:\Internship\PocketFM\Next_Agency.xlsx"
MAX_CONCURRENT_GR = 5
TARGET_BOOKS = 1200

# Base URL for BN Bestsellers Fantasy Romance
BN_BASE_URL = "https://www.barnesandnoble.com/pages/bestsellers?orderBy=attributes.mfield_bnb__salesRank&attributes.subjectCategoryDisplayName=Fantasy+Romance"

def normalize_title(title):
    if pd.isna(title) or not title:
        return ""
    t = str(title).lower()
    t = re.sub(r'[^\w\s]', '', t)
    return t.strip()

async def get_bn_books(page, target_count):
    books = []
    print(f"\n[B&N] Navigating to: {BN_BASE_URL}")
    
    try:
        await page.goto(BN_BASE_URL, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        
        # Sort by bestsellers if the option is there
        try:
            await page.evaluate('''() => {
                let sortBtn = document.querySelector('select#sortMenu');
                if(sortBtn) {
                    sortBtn.value = "Best Sellers";
                    sortBtn.dispatchEvent(new Event('change'));
                }
            }''')
            await page.wait_for_timeout(3000)
        except:
            pass
            
        prev_book_count = 0
        stuck_counter = 0
        
        while len(books) < target_count:
            # Scroll to bottom
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight - 1000)")
            await page.wait_for_timeout(1000)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
            # Extract current books on the page
            current_books = await page.evaluate('''() => {
                let items = [];
                let seenTitles = new Set();
                
                // Book links always start with /w/ on B&N
                let bookLinks = Array.from(document.querySelectorAll('a[href^="/w/"]'));
                
                bookLinks.forEach(a => {
                    let title = a.innerText.trim() || a.getAttribute('title');
                    if (!title || title.length < 2) return;
                    
                    if (seenTitles.has(title)) return;
                    seenTitles.add(title);
                    
                    let author = "Unknown Author";
                    // Try to find author link nearby. Usually it's in the same container.
                    let container = a.closest('div[class*="product"], div[class*="item"], div, section, article');
                    if (container) {
                        let authorEl = container.querySelector('a[href^="/authors/"], a[href*="/contributor/"]');
                        if (authorEl) {
                            author = authorEl.innerText.trim();
                        } else {
                            // Backup: sometimes the author is just the next link in the DOM after the wishlist buttons
                            let allLinks = Array.from(document.querySelectorAll('a'));
                            let myIdx = allLinks.indexOf(a);
                            if (myIdx > -1) {
                                for (let i = myIdx + 1; i < Math.min(myIdx + 5, allLinks.length); i++) {
                                    let nextLink = allLinks[i];
                                    if (nextLink.getAttribute('href') && (nextLink.getAttribute('href').startsWith('/authors/') || nextLink.getAttribute('href').includes('/contributor/'))) {
                                        author = nextLink.innerText.trim();
                                        break;
                                    }
                                }
                            }
                        }
                    }
                    
                    items.push({title: title, author: author});
                });
                return items;
            }''')
            
            # Since this might be pagination, we append new unique books
            for b in current_books:
                if b not in books and len(books) < target_count:
                    books.append(b)
            
            print(f"[B&N] Currently gathered {len(books)} books... (Target: {target_count})")
            
            if len(books) >= target_count:
                print("[B&N] Reached target count!")
                break
                
            if len(books) == prev_book_count:
                stuck_counter += 1
                if stuck_counter > 3:
                    print("[B&N] Book count hasn't increased. We might have reached the end of the category.")
                    break
            else:
                stuck_counter = 0
                
            prev_book_count = len(books)
            
            # Click the 'Next' page or 'Load More' button
            clicked = await page.evaluate('''() => {
                let nextBtn = document.querySelector('a.next-button, button.next-button, a[aria-label="Next"], a[title*="Next"]');
                if (nextBtn) {
                    nextBtn.click();
                    return true;
                }
                
                let btns = Array.from(document.querySelectorAll('button, a'));
                let loadBtn = btns.find(b => {
                    if (!b.innerText) return false;
                    let text = b.innerText.toLowerCase();
                    return text.includes('load more') || (text.includes('show more') && !b.closest('.sidebar, .filters-container, aside'));
                });
                
                if (loadBtn) {
                    loadBtn.click();
                    return true;
                }
                return false;
            }''')
            
            if clicked:
                print("[B&N] Clicked 'Next' or 'Load more'. Waiting for new page to render...")
                await page.wait_for_timeout(5000)
            else:
                print("[B&N] Could not find a 'Next' or 'Load more' button. Scraping finished.")
                break
            
    except Exception as e:
        print(f"[B&N] Error during extraction: {e}")
            
    return books[:target_count]

# -----------------
# Goodreads Tiered Scraping Worker
# -----------------
async def worker(worker_id, queue, page):
    while True:
        try:
            item = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
            
        book_index = item['index']
        title = item['title']
        author = item['author'].replace('by ', '').strip()
        print(f"  [Scraping Book {book_index}] '{title}' by {author}...")
        
        search_query = f"{title} {author}"
        encoded_query = urllib.parse.quote_plus(search_query)
        search_url = f"https://www.goodreads.com/search?q={encoded_query}"
        
        try:
            await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
            
            # Check CAPTCHA
            page_text = await page.content()
            if "Verify you are human" in page_text or "captcha-delivery" in page_text:
                print(f"    [!!! ACTION REQUIRED !!!] CAPTCHA detected for '{title}'! Please solve it in the browser window. (5 minute timeout)")
                try:
                    await page.wait_for_selector(".tableList", timeout=300000)
                    print(f"    [Success] CAPTCHA cleared for '{title}'!")
                except:
                    print(f"    [Timeout] CAPTCHA not solved in 5 minutes. Falling back to Tier 2...")
                    item['result'] = None
                    queue.task_done()
                    continue
            
            # Extract first result
            data = await page.evaluate('''() => {
                let firstRow = document.querySelector('.tableList tr');
                if (!firstRow) return null;
                
                let titleEl = firstRow.querySelector('.bookTitle');
                let minfo = firstRow.querySelector('.minirating');
                if (!titleEl || !minfo) return null;
                
                let rawTitle = titleEl.innerText.trim();
                let link = titleEl.href;
                let ratingText = minfo.innerText.trim();
                
                let avgMatch = ratingText.match(/([\d\.]+)\s*avg rating/);
                let countMatch = ratingText.match(/([\d\,]+)\s*ratings/);
                
                let avg = avgMatch ? avgMatch[1] : "";
                let count = countMatch ? countMatch[1].replace(/,/g, '') : "";
                
                // Parse series from title if exists e.g. "Book Title (Series, #1)"
                let seriesName = "";
                let sMatch = rawTitle.match(/\(([^,]+),?\s*#?[\d\.]+\)$/);
                if (sMatch) seriesName = sMatch[1].trim();
                
                return {
                    title: rawTitle,
                    link: link,
                    avg: avg,
                    count: count,
                    series: seriesName
                };
            }''')
            
            if not data:
                print(f"  [Not Found] '{title}'")
                item['result'] = None
            else:
                print(f"    [Goodreads] Matched: '{data['title']}' ({data['avg']} avg rating)")
                
                # If we matched, let's navigate to the book page to get the synopsis
                synopsis = ""
                try:
                    await page.goto(data['link'], wait_until="domcontentloaded", timeout=30000)
                    synopsis = await page.evaluate('''() => {
                        let syn = document.querySelector('div[data-testid="description"]');
                        return syn ? syn.innerText.trim() : "";
                    }''')
                except Exception as e:
                    print(f"    [Warning] Could not load book page for synopsis: {e}")
                
                data['synopsis'] = synopsis
                item['result'] = data
                print(f"  [Done] '{title}'")
                
        except Exception as e:
            print(f"  [Error] Failed on '{title}': {e}")
            item['result'] = None
            
        queue.task_done()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # 1. Fetch from B&N
        bn_page = await context.new_page()
        print(f"\n=== PHASE 1: Fetching {TARGET_BOOKS} books from Barnes & Noble ===")
        bn_books = await get_bn_books(bn_page, TARGET_BOOKS)
        await bn_page.close()
        
        print(f"\n=== PHASE 2: Enriching {len(bn_books)} books via Goodreads ({MAX_CONCURRENT_GR} concurrent tabs) ===")
        
        # Prepare queue
        queue = asyncio.Queue()
        tasks_data = []
        for i, book in enumerate(bn_books):
            t_data = {
                'index': i+1,
                'title': book['title'],
                'author': book['author'],
                'result': None
            }
            tasks_data.append(t_data)
            queue.put_nowait(t_data)
            
        # Launch GR workers
        pages = []
        workers = []
        for i in range(MAX_CONCURRENT_GR):
            page = await context.new_page()
            pages.append(page)
            workers.append(asyncio.create_task(worker(i, queue, page)))
            
        await queue.join()
        
        for w in workers:
            w.cancel()
        for page in pages:
            await page.close()
            
        await browser.close()
        
        print("\n=== PHASE 3: Saving to Excel ===")
        
        # Prepare dataframe
        records = []
        for item in tasks_data:
            orig_title = item['title']
            orig_author = item['author']
            res = item['result']
            
            if res:
                series = res['series']
                link = res['link']
                avg = res['avg']
                count = res['count']
                synopsis = res['synopsis']
            else:
                series = ""
                link = ""
                avg = ""
                count = ""
                synopsis = ""
                
            records.append({
                'Name of Series': series,
                'Author Name': orig_author,
                'Publisher': "", # Not scraped from BN grid easily
                'GoodReads series link': link,
                'Number of PRIMARY books in the series': 1,
                'Rating (out of 5) of Primary Book 1': avg,
                'Ratings (#) of Primary Book 1': count,
                'Synopsis (if available)': synopsis,
                'Romantasy = Yes or No?': "Yes", # Force Yes since it's the Fantasy Romance category
                'Romantasy Sub-Genre of series': "",
                'Name of agent in the main folder': orig_title # Store original title here for reference!
            })
            
        df = pd.DataFrame(records)
        df.to_excel(EXCEL_FILE, index=False)
        print(f"Data saved to {EXCEL_FILE}")
        
        try:
            print("Applying JRA premium styling...")
            apply_styling(EXCEL_FILE)
            print("Styling applied successfully.")
        except Exception as e:
            print(f"Failed to apply styling: {e}")
            
        print("\nALL DONE!")

if __name__ == "__main__":
    asyncio.run(main())
