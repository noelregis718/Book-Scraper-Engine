import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import logging
import json
import re
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

BASE_URL = 'https://www.goodreads.com'
SHELF_URL = 'https://www.goodreads.com/shelf/show/berkley-romance?page=3'
EXCEL_FILE = 'e:/Internship/PocketFM/berkley_romance_books.xlsx'

COLUMNS = [
    'Name of Series',
    'Author Name',
    'Publisher',
    'GoodReads series link',
    'Number of PRIMARY books in the series',
    'Rating (out of 5) of Primary Book 1',
    'Ratings (#) of Primary Book 1',
    'Synopsis (if available)',
    'Romantasy = Yes or No?',
    'Romantasy Sub-Genre of series',
    'Name of agent'
]

async def scroll_page(page):
    logging.info("Scrolling down the page to load all books...")
    last_height = await page.evaluate("document.body.scrollHeight")
    scroll_attempts = 0
    while scroll_attempts < 20:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)
        new_height = await page.evaluate("document.body.scrollHeight")
        try:
            load_more = await page.query_selector('button:has-text("Show more"), button:has-text("Load more")')
            if load_more and await load_more.is_visible():
                await load_more.click()
                await asyncio.sleep(2)
                new_height = await page.evaluate("document.body.scrollHeight")
        except: pass
        if new_height == last_height:
            scroll_attempts += 1
            if scroll_attempts > 3: break
        else:
            scroll_attempts = 0
        last_height = new_height
    logging.info("Finished scrolling.")

async def parse_book_page(page, url):
    await page.goto(url, wait_until="domcontentloaded")
    data = {col: '' for col in COLUMNS}
    try:
        modal_close = await page.query_selector('.modal__close, .Overlay__close')
        if modal_close: await modal_close.click()
    except: pass
    title_elem = await page.query_selector('h1[data-testid="bookTitle"]')
    if title_elem: data['Name of Series'] = await title_elem.inner_text()
    author_elem = await page.query_selector('span[data-testid="name"]')
    if author_elem: data['Author Name'] = await author_elem.inner_text()
    rating_elem = await page.query_selector('div.RatingStatistics__rating')
    if rating_elem: data['Rating (out of 5) of Primary Book 1'] = await rating_elem.inner_text()
    ratings_count_elem = await page.query_selector('span[data-testid="ratingsCount"]')
    if ratings_count_elem:
        count_text = await ratings_count_elem.inner_text()
        data['Ratings (#) of Primary Book 1'] = count_text.split()[0].replace(',', '')
    synopsis_elem = await page.query_selector('div[data-testid="description"]')
    if synopsis_elem: data['Synopsis (if available)'] = await synopsis_elem.inner_text()
    series_elem = await page.query_selector('h3.Text__title3 a[href*="/series/"]')
    if series_elem:
        s_title = await series_elem.inner_text()
        s_href = await series_elem.get_attribute('href')
        data['Name of Series'] = s_title
        data['GoodReads series link'] = BASE_URL + s_href if s_href.startswith('/') else s_href
    else: data['GoodReads series link'] = url
    next_data_elem = await page.query_selector('script#__NEXT_DATA__')
    if next_data_elem:
        try:
            next_json = json.loads(await next_data_elem.inner_text())
            apollo_state = next_json.get('props', {}).get('pageProps', {}).get('apolloState', {})
            for key, val in apollo_state.items():
                if key.startswith('Book:'):
                    details = val.get('details')
                    if isinstance(details, dict):
                        pub_ref = details.get('publisher', {})
                        if isinstance(pub_ref, dict) and '__ref' in pub_ref:
                            pub_obj = apollo_state.get(pub_ref['__ref'], {})
                            if pub_obj: data['Publisher'] = pub_obj.get('name', '')
                    break
        except: pass
    if '/series/' in data['GoodReads series link']:
        try:
            await page.goto(data['GoodReads series link'], wait_until="domcontentloaded")
            desc_text = await page.inner_text('body')
            match = re.search(r'(\d+)\s+primary\s+work', desc_text, re.IGNORECASE)
            if match: data['Number of PRIMARY books in the series'] = match.group(1)
            else: data['Number of PRIMARY books in the series'] = '1'
        except: data['Number of PRIMARY books in the series'] = '1'
    else: data['Number of PRIMARY books in the series'] = '1'
    return data

async def worker(queue, context, results):
    page = await context.new_page()
    while True:
        url = await queue.get()
        if url is None: break
        logging.info(f"Processing book: {url}")
        try:
            book_data = await parse_book_page(page, url)
            if book_data: results.append(book_data)
        except Exception as e: logging.error(f"Error processing {url}: {e}")
        queue.task_done()
    await page.close()

async def main():
    if os.path.exists(EXCEL_FILE):
        existing_df = pd.read_excel(EXCEL_FILE)
        existing_urls = set(existing_df['GoodReads series link'].tolist())
    else:
        existing_df = pd.DataFrame(columns=COLUMNS)
        existing_urls = set()

    scraper = GoodreadsScraper(headless=False)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        
        BASE_SHELF_URL = 'https://www.goodreads.com/shelf/show/berkley-romance'
        
        page_num = 4
        while page_num <= 10:
            current_url = f"{BASE_SHELF_URL}?page={page_num}"
            logging.info(f"Navigating directly to URL: {current_url}")
            await login_page.goto(current_url, wait_until="domcontentloaded")
            await asyncio.sleep(5) # Add a 5 second delay to avoid rate limits
            
            logging.info(f"Extracting books from page {page_num}...")
            await login_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)
            
            books = await login_page.query_selector_all('.elementList .left a.bookTitle')
            if not books:
                logging.info(f"No books found on page {page_num}. Goodreads might be blocking us.")
                break
            
            page_new_urls = []
            for b in books:
                href = await b.get_attribute('href')
                if href:
                    full_url = BASE_URL + href if href.startswith('/') else href
                    if full_url not in existing_urls:
                        page_new_urls.append(full_url)
                        existing_urls.add(full_url)
            
            logging.info(f"Page {page_num} yielded {len(page_new_urls)} new unique books to scrape.")
            
            if page_new_urls:
                queue = asyncio.Queue()
                for u in page_new_urls: queue.put_nowait(u)
                results = []
                workers = []
                logging.info(f"Starting 10 concurrent tabs for page {page_num}...")
                for _ in range(10): workers.append(asyncio.create_task(worker(queue, context, results)))
                await queue.join()
                for _ in range(10): queue.put_nowait(None)
                await asyncio.gather(*workers)
                
                if results:
                    new_df = pd.DataFrame(results, columns=COLUMNS)
                    existing_df = pd.concat([existing_df, new_df], ignore_index=True)
                    existing_df.to_excel(EXCEL_FILE, index=False)
                    logging.info(f"Saved {len(results)} new records. Total is now {len(existing_df)}.")
            
            page_num += 1
            
        logging.info("Finished scraping all requested pages!")
        await login_page.close()
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
