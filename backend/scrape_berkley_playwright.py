import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import logging
import json
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = 'https://www.goodreads.com'
SHELF_URL = 'https://www.goodreads.com/shelf/show/berkley-romance'

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

async def parse_book_page(page, url):
    await page.goto(url, wait_until="domcontentloaded")
    
    # Defaults
    data = {col: '' for col in COLUMNS}
    
    # Try to close any modal if it appears
    try:
        modal_close = await page.query_selector('.modal__close')
        if modal_close:
            await modal_close.click()
    except:
        pass
        
    title_elem = await page.query_selector('h1[data-testid="bookTitle"]')
    if title_elem:
        data['Name of Series'] = await title_elem.inner_text()
        
    author_elem = await page.query_selector('span[data-testid="name"]')
    if author_elem:
        data['Author Name'] = await author_elem.inner_text()
        
    rating_elem = await page.query_selector('div.RatingStatistics__rating')
    if rating_elem:
        data['Rating (out of 5) of Primary Book 1'] = await rating_elem.inner_text()
        
    ratings_count_elem = await page.query_selector('span[data-testid="ratingsCount"]')
    if ratings_count_elem:
        count_text = await ratings_count_elem.inner_text()
        data['Ratings (#) of Primary Book 1'] = count_text.split()[0].replace(',', '')
        
    synopsis_elem = await page.query_selector('div[data-testid="description"]')
    if synopsis_elem:
        data['Synopsis (if available)'] = await synopsis_elem.inner_text()
        
    series_elem = await page.query_selector('h3.Text__title3 a[href*="/series/"]')
    if series_elem:
        s_title = await series_elem.inner_text()
        s_href = await series_elem.get_attribute('href')
        data['Name of Series'] = s_title
        data['GoodReads series link'] = BASE_URL + s_href if s_href.startswith('/') else s_href
    else:
        data['GoodReads series link'] = url

    # Extract publisher from __NEXT_DATA__
    next_data_elem = await page.query_selector('script#__NEXT_DATA__')
    if next_data_elem:
        try:
            next_data_text = await next_data_elem.inner_text()
            next_json = json.loads(next_data_text)
            apollo_state = next_json.get('props', {}).get('pageProps', {}).get('apolloState', {})
            
            for key, val in apollo_state.items():
                if key.startswith('Book:'):
                    details = val.get('details')
                    if isinstance(details, dict):
                        pub_ref = details.get('publisher', {})
                        if isinstance(pub_ref, dict) and '__ref' in pub_ref:
                            pub_obj = apollo_state.get(pub_ref['__ref'], {})
                            if pub_obj:
                                data['Publisher'] = pub_obj.get('name', '')
                    break
        except:
            pass

    # Number of primary books
    if '/series/' in data['GoodReads series link']:
        try:
            await page.goto(data['GoodReads series link'], wait_until="domcontentloaded")
            desc_text = await page.inner_text('body')
            match = re.search(r'(\d+)\s+primary\s+work', desc_text, re.IGNORECASE)
            if match:
                data['Number of PRIMARY books in the series'] = match.group(1)
            else:
                data['Number of PRIMARY books in the series'] = '1'
        except:
            data['Number of PRIMARY books in the series'] = '1'
    else:
        data['Number of PRIMARY books in the series'] = '1'
        
    return data

async def worker(queue, context, results):
    page = await context.new_page()
    while True:
        url = await queue.get()
        if url is None:
            break
        logging.info(f"Processing book: {url}")
        try:
            book_data = await parse_book_page(page, url)
            if book_data:
                results.append(book_data)
        except Exception as e:
            logging.error(f"Error processing {url}: {e}")
        queue.task_done()
    await page.close()

async def main():
    async with async_playwright() as p:
        # headless=False to open visibly before the user
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        logging.info("Opening Goodreads visibly...")
        await page.goto("https://www.goodreads.com")
        
        # Give user 10 seconds to manually login if they want to
        logging.info("Waiting 10 seconds before starting to scrape shelves... (Login if needed!)")
        await asyncio.sleep(10)
        
        book_urls = []
        page_num = 1
        last_page_books = set()
        
        while True:
            logging.info(f"Fetching shelf page {page_num}")
            url = f"{SHELF_URL}?page={page_num}"
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(3) # Ensure content loads
            
            books = await page.query_selector_all('.elementList .left a.bookTitle')
            if not books:
                logging.info(f"No books found on page {page_num}.")
                break
                
            current_page_books = set()
            for b in books:
                href = await b.get_attribute('href')
                if href:
                    full_url = BASE_URL + href if href.startswith('/') else href
                    current_page_books.add(full_url)
                    if full_url not in book_urls:
                        book_urls.append(full_url)
            
            # If the current page contains exactly the same set of books as the previous page, we've hit the limit.
            if current_page_books == last_page_books:
                logging.info("Reached end of pagination or Goodreads returned duplicate page.")
                break
                
            last_page_books = current_page_books
            page_num += 1
            
        logging.info(f"Total unique books found: {len(book_urls)}")
        await page.close()
        
        queue = asyncio.Queue()
        for url in book_urls:
            queue.put_nowait(url)
            
        results = []
        # Create 10 workers for 10 concurrent tabs
        workers = []
        logging.info("Starting 10 concurrent tabs to process the books...")
        for _ in range(10):
            workers.append(asyncio.create_task(worker(queue, context, results)))
            
        await queue.join()
        
        # Stop workers
        for _ in range(10):
            queue.put_nowait(None)
        await asyncio.gather(*workers)
        
        await browser.close()
        
        # Save results
        df = pd.DataFrame(results, columns=COLUMNS)
        output_file = 'e:/Internship/PocketFM/berkley_romance_books_playwright.xlsx'
        df.to_excel(output_file, index=False)
        logging.info(f"Saved {len(results)} records to {output_file}")

if __name__ == '__main__':
    asyncio.run(main())
