import sys
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from playwright.sync_api import sync_playwright

excel_path = r"e:\Internship\PocketFM\podium_data.xlsx"

def scrape_book_details(book_url):
    print(f"Scraping: {book_url}")
    try:
        response = requests.get(book_url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_tag = soup.find('h1', {'data-testid': 'title-header'})
        title = title_tag.text.strip() if title_tag else ""
        
        series_tag = soup.find('a', {'data-testid': 'title-series'})
        series = series_tag.text.strip() if series_tag else ""
        
        author_tags = soup.find_all('a', {'data-testid': 'link-authors'})
        author = ", ".join([a.text.strip() for a in author_tags]) if author_tags else ""
        
        genre_tags = soup.find_all('a', {'data-testid': 'link-genre'})
        genres_list = [a.text.strip().replace(',', '') for a in genre_tags]
        genre = genres_list[0] if len(genres_list) > 0 else ""
        subgenre = ", ".join(genres_list[1:]) if len(genres_list) > 1 else ""
        
        desc_tag = soup.find('div', {'data-testid': 'story-description'})
        description = desc_tag.text.strip() if desc_tag else ""
        
        release_date = ""
        rd_div = soup.find('div', {'data-testid': 'label-release-date'})
        if rd_div:
            spans = rd_div.find_all('span')
            if len(spans) > 1: release_date = spans[1].text.strip()
                
        language = ""
        lang_div = soup.find('div', {'data-testid': 'label-language'})
        if lang_div:
            spans = lang_div.find_all('span')
            if len(spans) > 1: language = spans[1].text.strip()
                
        fmt = ""
        fmt_div = soup.find('div', {'data-testid': 'label-format'})
        if fmt_div:
            spans = fmt_div.find_all('span')
            if len(spans) > 1: fmt = spans[1].text.strip()
                
        duration = ""
        dur_div = soup.find('div', {'data-testid': 'label-duration'})
        if dur_div:
            spans = dur_div.find_all('span')
            if len(spans) > 1: duration = spans[1].text.strip()
                
        narrators = ""
        narrator_tags = soup.find_all('a', {'data-testid': 'link-performers'})
        if narrator_tags:
            narrators = ", ".join([a.text.strip().replace(',', '').strip() for a in narrator_tags])
            
        return {
            "Book Title": title,
            "Series Name": series,
            "Author": author,
            "Genre": genre,
            "Subgenre": subgenre,
            "Podium Summary / Description": description,
            "Podium URL": book_url,
            "Release Date": release_date,
            "Language": language,
            "Format": fmt,
            "Duration": duration,
            "Narrator": narrators
        }
    except Exception as e:
        print(f"Error scraping {book_url}: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python scrape_podium_genre.py <genre_url>")
        return
        
    url = sys.argv[1]
    
    # Load existing data to avoid duplicates
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
    else:
        df = pd.DataFrame()
        
    existing_urls = set()
    if not df.empty and 'Podium URL' in df.columns:
        existing_urls = set(df['Podium URL'].dropna().tolist())

    processed_in_session = set()
    total_scraped = 0
    batch_size = 10

    print(f"Starting synchronized scraping on {url} ...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5)
        
        last_height = page.evaluate("document.body.scrollHeight")
        attempts = 0
        
        while attempts < 100:
            # 1. Grab all visible links on the screen right now
            elements = page.query_selector_all("a[href^='/titles/']")
            visible_links = set()
            for el in elements:
                href = el.get_attribute("href")
                if href and href.startswith('/titles/'):
                    full_link = "https://podiumentertainment.com" + href
                    visible_links.add(full_link)
            
            # 2. Filter down to links we haven't processed yet and aren't in Excel
            new_links = [l for l in visible_links if l not in existing_urls and l not in processed_in_session]
            
            # 3. If we have at least 10 new links (or if we hit the end of the page), process a batch
            while len(new_links) >= batch_size:
                batch_links = new_links[:batch_size]
                new_links = new_links[batch_size:] # Remove them from the queue
                
                print(f"\n--- Processing batch of {len(batch_links)} books ---")
                batch_data = []
                for link in batch_links:
                    data = scrape_book_details(link)
                    processed_in_session.add(link)
                    if data:
                        batch_data.append(data)
                    time.sleep(1) # Polite scraping
                
                # Save batch to Excel
                if batch_data:
                    new_df = pd.DataFrame(batch_data)
                    if os.path.exists(excel_path):
                        current_df = pd.read_excel(excel_path)
                    else:
                        current_df = pd.DataFrame()
                        
                    if not current_df.empty:
                        existing_cols = current_df.columns.tolist()
                        current_df = pd.concat([current_df, new_df], ignore_index=True)
                        missing_cols = [c for c in existing_cols if c not in current_df.columns]
                        for c in missing_cols: current_df[c] = ""
                        current_df = current_df[existing_cols]
                    else:
                        current_df = new_df
                        
                    if 'Podium URL' in current_df.columns:
                        current_df = current_df.drop_duplicates(subset=['Podium URL'], keep='last')
                        
                    current_df.to_excel(excel_path, index=False)
                    total_scraped += len(batch_data)
                    print(f"Saved batch! Total books successfully scraped so far: {total_scraped}")

            # 4. We ran out of new links, so we must scroll / click "Load More" to reveal more
            print(f"Scrolling to find more books...")
            try:
                load_more = page.query_selector("button:has-text('Load More Titles')")
                if load_more and load_more.is_visible():
                    load_more.click()
                    time.sleep(3)
            except:
                pass
                
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)
            
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                time.sleep(3)
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    # We have reached the very bottom of the entire page
                    break
            last_height = new_height
            attempts += 1
            
        browser.close()
        
    if total_scraped > 0:
        print("\nApplying styling...")
        os.system(f"python {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'style_excel.py')}")
        print("Done!")
    else:
        print("\nNo new data scraped.")

if __name__ == "__main__":
    main()
