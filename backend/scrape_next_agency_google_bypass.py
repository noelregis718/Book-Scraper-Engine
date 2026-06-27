import os
import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from googlesearch import search
from apply_jra_style import apply_styling

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Next_Agency.xlsx')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

def clean_text(text):
    if not text: return ""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def scrape_goodreads_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Rating & Count
        avg_rating = "N/A"
        rating_count = "N/A"
        ld_el = soup.find('script', type="application/ld+json")
        if ld_el:
            try:
                ld_data = json.loads(ld_el.string)
                if isinstance(ld_data, list): ld_data = ld_data[0]
                avg_rating = str(ld_data.get('aggregateRating', {}).get('ratingValue', 'N/A'))
                rating_count = str(ld_data.get('aggregateRating', {}).get('ratingCount', 'N/A'))
            except: pass
            
        # Description
        description = "N/A"
        desc_el = soup.select_one('[data-testid="description"] .Formatted, .readable')
        if desc_el:
            description = clean_text(desc_el.get_text(separator=' '))
            
        # Genres
        genres = []
        for g in soup.select('[data-testid="genresList"] .Button__labelItem, .BookPageMetadataSection__genre a'):
            txt = clean_text(g.text)
            if txt and txt not in genres: genres.append(txt)
            
        is_romantasy = "Yes" if any("romantasy" in g.lower() for g in genres) else "No"
        genre_sub = genres[1] if len(genres) > 1 else (genres[0] if genres else "N/A")
        
        # Series
        series_url = "N/A"
        series_link = soup.select_one('h3.Text__title3 a[href*="/series/"]')
        if series_link:
            series_url = series_link['href']
            
        return {
            "GoodReads_Series_URL": series_url if series_url != "N/A" else url,
            "GoodReads_Rating": avg_rating,
            "GoodReads_Rating_Count": rating_count,
            "Description": description,
            "Romantasy_Subgenre": is_romantasy,
            "Sub_Genre": genre_sub
        }
    except Exception as e:
        print(f"Error scraping page {url}: {e}")
        return None

def fetch_series_info(series_url):
    if series_url == "N/A" or not series_url.startswith("http"): return "1"
    try:
        res = requests.get(series_url, headers=HEADERS, timeout=10)
        m = re.search(r'(\d+)\s+primary\s+works', res.text, re.IGNORECASE)
        if m: return m.group(1)
    except: pass
    return "1"

def run():
    print("Loading Excel file...", flush=True)
    df = pd.read_excel(EXCEL_FILE)
    
    # Fill NaN
    for col in ["GoodReads series link", "Number of PRIMARY books in the series", 
                "Rating (out of 5) of Primary Book 1", "Ratings (#) of Primary Book 1", 
                "Synopsis (if available)", "Romantasy = Yes or No?", "Romantasy Sub-Genre of series"]:
        if col not in df.columns:
            df[col] = ""
            
    print("\nStarting Google-Bypass Scraper...", flush=True)
    
    count = 0
    for index, row in df.iterrows():
        title = str(row.get("Name of Series", "")).strip()
        author = str(row.get("Author Name", "")).strip()
        current_link = str(row.get("GoodReads series link", ""))
        
        if current_link and current_link not in ["nan", "None", "", "N/A"]:
            continue
            
        if not title or title in ["nan", "None", ""]:
            continue
            
        print(f"[{index}] Google Searching: '{title}'", flush=True)
        query = f'"{title}" site:goodreads.com/book'
        
        book_url = None
        try:
            for url in search(query, num_results=2):
                if "/book/show/" in url:
                    book_url = url
                    break
        except Exception as e:
            print(f"[{index}] Google search error: {e}", flush=True)
            time.sleep(2)
            continue
            
        if not book_url:
            print(f"[{index}] No Goodreads link found for '{title}'", flush=True)
            continue
            
        print(f"[{index}] Found link: {book_url}. Fetching details...", flush=True)
        data = scrape_goodreads_page(book_url)
        
        if data:
            df.at[index, "GoodReads series link"] = data["GoodReads_Series_URL"]
            df.at[index, "Rating (out of 5) of Primary Book 1"] = data["GoodReads_Rating"]
            df.at[index, "Ratings (#) of Primary Book 1"] = data["GoodReads_Rating_Count"]
            df.at[index, "Synopsis (if available)"] = data["Description"]
            
            romantasy = str(df.at[index, "Romantasy = Yes or No?"])
            if romantasy in ["nan", "", "None"]:
                df.at[index, "Romantasy = Yes or No?"] = data["Romantasy_Subgenre"]
                df.at[index, "Romantasy Sub-Genre of series"] = data["Sub_Genre"]
                
            num_primary = fetch_series_info(data["GoodReads_Series_URL"])
            df.at[index, "Number of PRIMARY books in the series"] = num_primary
            
            print(f"[{index}] Success! '{title}'", flush=True)
            df.to_excel(EXCEL_FILE, index=False)
            count += 1
        else:
            print(f"[{index}] Failed to extract data from page.", flush=True)
            
        time.sleep(1.5) # Be polite to Google/Goodreads
        
    print(f"\nScraping complete. Processed {count} new books.", flush=True)
    try:
        apply_styling(EXCEL_FILE)
        print("Styling applied.", flush=True)
    except: pass

if __name__ == '__main__':
    run()
