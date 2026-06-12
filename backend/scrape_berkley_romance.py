import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import json
import logging
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = 'https://www.goodreads.com'
SHELF_URL = 'https://www.goodreads.com/shelf/show/berkley-romance'

# Columns as requested
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

async def fetch_html(session, url, retries=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    for attempt in range(retries):
        try:
            async with session.get(url, headers=headers, timeout=20) as response:
                if response.status == 200:
                    return await response.text()
                elif response.status == 429:
                    logging.warning(f"Rate limited on {url}, retrying in 5 seconds...")
                    await asyncio.sleep(5)
                else:
                    logging.error(f"Failed to fetch {url} with status {response.status}")
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
        await asyncio.sleep(2)
    return None

async def parse_book_page(session, url):
    html = await fetch_html(session, url)
    if not html:
        return None
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # Defaults
    data = {col: '' for col in COLUMNS}
    
    # Parse basic fields from HTML
    title_elem = soup.select_one('h1[data-testid="bookTitle"]')
    author_elem = soup.select_one('span[data-testid="name"]')
    rating_elem = soup.select_one('div.RatingStatistics__rating')
    ratings_count_elem = soup.select_one('span[data-testid="ratingsCount"]')
    synopsis_elem = soup.select_one('div[data-testid="description"]')
    
    # Try to find series link from HTML. Series links look like /series/
    series_elem = soup.select_one('h3.Text__title3 a[href*="/series/"]')
    if series_elem:
        data['Name of Series'] = series_elem.text.strip()
        data['GoodReads series link'] = urljoin(BASE_URL, series_elem['href'])
    else:
        # If no series, we use the book's title
        data['Name of Series'] = title_elem.text.strip() if title_elem else ''
        data['GoodReads series link'] = url

    data['Author Name'] = author_elem.text.strip() if author_elem else ''
    data['Rating (out of 5) of Primary Book 1'] = rating_elem.text.strip() if rating_elem else ''
    
    if ratings_count_elem:
        count_text = ratings_count_elem.text.strip().replace(',', '').split()[0]
        data['Ratings (#) of Primary Book 1'] = count_text
        
    data['Synopsis (if available)'] = synopsis_elem.text.strip() if synopsis_elem else ''
    
    # Extract publisher from __NEXT_DATA__
    next_data = soup.find('script', id='__NEXT_DATA__')
    if next_data:
        try:
            next_json = json.loads(next_data.string)
            apollo_state = next_json.get('props', {}).get('pageProps', {}).get('apolloState', {})
            
            # Find publisher
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
        except Exception as e:
            logging.error(f"Error parsing apollo state for {url}: {e}")

    # Fetch series page if applicable to get number of primary books
    if '/series/' in data['GoodReads series link']:
        series_html = await fetch_html(session, data['GoodReads series link'])
        if series_html:
            series_soup = BeautifulSoup(series_html, 'html.parser')
            # E.g., "10 primary works \u2022 15 total works"
            desc_text = series_soup.get_text()
            import re
            match = re.search(r'(\d+)\s+primary\s+work', desc_text, re.IGNORECASE)
            if match:
                data['Number of PRIMARY books in the series'] = match.group(1)
            else:
                data['Number of PRIMARY books in the series'] = '1'
    else:
        data['Number of PRIMARY books in the series'] = '1'

    return data

async def process_book(session, url, semaphore, results):
    async with semaphore:
        logging.info(f"Processing book: {url}")
        book_data = await parse_book_page(session, url)
        if book_data:
            results.append(book_data)

async def main():
    semaphore = asyncio.Semaphore(10) # 10 at a time
    results = []
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Collect book URLs from the shelf pages
        book_urls = set()
        page = 1
        
        while True:
            logging.info(f"Fetching shelf page {page}")
            url = f"{SHELF_URL}?page={page}"
            html = await fetch_html(session, url)
            if not html:
                break
                
            soup = BeautifulSoup(html, 'html.parser')
            books = soup.select('.elementList .left a.bookTitle')
            
            if not books:
                logging.info(f"No books found on page {page}. Ending pagination.")
                break
                
            for b in books:
                href = b.get('href')
                if href:
                    book_urls.add(urljoin(BASE_URL, href))
                    
            page += 1
            if page > 9: # 441 books, 50 per page -> max 9 pages.
                break
                
        logging.info(f"Total unique books found: {len(book_urls)}")
        
        # Step 2: Process each book with concurrency of 10
        tasks = [process_book(session, url, semaphore, results) for url in book_urls]
        await asyncio.gather(*tasks)
        
    # Step 3: Save to Excel
    df = pd.DataFrame(results, columns=COLUMNS)
    output_file = 'berkley_romance_books.xlsx'
    df.to_excel(output_file, index=False)
    logging.info(f"Saved {len(results)} records to {output_file}")

if __name__ == '__main__':
    asyncio.run(main())
