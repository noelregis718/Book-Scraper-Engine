import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import json

base_url = "https://podiumentertainment.com"
excel_path = r"e:\Internship\PocketFM\podium_data.xlsx"
links_file = "podium_dynamic_links.json"

def scrape_book_details(book_url):
    print(f"Scraping: {book_url}")
    try:
        response = requests.get(book_url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Title
        title_tag = soup.find('h1', {'data-testid': 'title-header'})
        title = title_tag.text.strip() if title_tag else ""
        
        # Series Name
        series_tag = soup.find('a', {'data-testid': 'title-series'})
        series = series_tag.text.strip() if series_tag else ""
        
        # Author
        author_tags = soup.find_all('a', {'data-testid': 'link-authors'})
        author = ", ".join([a.text.strip() for a in author_tags]) if author_tags else ""
        
        # Genre and Subgenre
        genre_tags = soup.find_all('a', {'data-testid': 'link-genre'})
        genres_list = [a.text.strip().replace(',', '') for a in genre_tags]
        genre = genres_list[0] if len(genres_list) > 0 else ""
        subgenre = ", ".join(genres_list[1:]) if len(genres_list) > 1 else ""
        
        # Podium Summary / Description
        desc_tag = soup.find('div', {'data-testid': 'story-description'})
        description = desc_tag.text.strip() if desc_tag else ""
        
        # Release Date
        release_date = ""
        rd_div = soup.find('div', {'data-testid': 'label-release-date'})
        if rd_div:
            spans = rd_div.find_all('span')
            if len(spans) > 1:
                release_date = spans[1].text.strip()
                
        # Language
        language = ""
        lang_div = soup.find('div', {'data-testid': 'label-language'})
        if lang_div:
            spans = lang_div.find_all('span')
            if len(spans) > 1:
                language = spans[1].text.strip()
                
        # Format
        fmt = ""
        fmt_div = soup.find('div', {'data-testid': 'label-format'})
        if fmt_div:
            spans = fmt_div.find_all('span')
            if len(spans) > 1:
                fmt = spans[1].text.strip()
                
        # Duration
        duration = ""
        dur_div = soup.find('div', {'data-testid': 'label-duration'})
        if dur_div:
            spans = dur_div.find_all('span')
            if len(spans) > 1:
                duration = spans[1].text.strip()
                
        # Narrator
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
    if not os.path.exists(links_file):
        print(f"Links file {links_file} not found.")
        return
        
    with open(links_file, "r") as f:
        book_links = json.load(f)
        
    print(f"Loaded {len(book_links)} links from {links_file}")
    
    # Read existing excel
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
    else:
        df = pd.DataFrame()
        
    existing_urls = set()
    if not df.empty and 'Podium URL' in df.columns:
        existing_urls = set(df['Podium URL'].dropna().tolist())
        
    links_to_scrape = [link for link in book_links if link not in existing_urls]
    
    print(f"Skipping {len(book_links) - len(links_to_scrape)} already scraped books.")
    print(f"Will scrape {len(links_to_scrape)} new books.")
    
    scraped_data = []
    for link in links_to_scrape:
        data = scrape_book_details(link)
        if data:
            scraped_data.append(data)
        time.sleep(1) # Polite scraping
        
    if not scraped_data:
        print("No new data scraped.")
        return
        
    new_df = pd.DataFrame(scraped_data)
    
    if not df.empty:
        # Get existing columns to preserve them
        existing_cols = df.columns.tolist()
        df = pd.concat([df, new_df], ignore_index=True)
        # reorder columns to match original
        missing_cols = [c for c in existing_cols if c not in df.columns]
        for c in missing_cols:
            df[c] = ""
        df = df[existing_cols]
    else:
        df = new_df
        
    # Drop duplicates by Podium URL if any
    if 'Podium URL' in df.columns:
        df = df.drop_duplicates(subset=['Podium URL'], keep='last')
        
    df.to_excel(excel_path, index=False)
    print(f"Saved {len(scraped_data)} new records to {excel_path}")

if __name__ == "__main__":
    main()
