import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

start_url = "https://www.rebelangel.co.uk/category/book-reviews/romance/"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

books = []

current_url = start_url
page = 1

while current_url:
    print(f"Scraping Page {page}: {current_url}")
    response = requests.get(current_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch {current_url}. Status code: {response.status_code}")
        break
        
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all('article')
    
    for post in posts:
        title_tag = post.find(['h1', 'h2', 'h3'])
        if not title_tag:
            continue
            
        full_title = title_tag.text.strip()
        
        # Parse "Book Title by Author Name - Review Type"
        # We handle various dash characters including Unicode replacement char \ufffd
        match = re.search(r"^(.*?)\s+by\s+(.*?)\s+(?:-|–|—|\u2013|\u2014|\ufffd|–)\s+.*?(?:Review|Romantasy|Fantasy|Blog)", full_title, re.IGNORECASE)
        
        if match:
            book_name = match.group(1).strip()
            author_name = match.group(2).strip()
        else:
            # Fallback parsing
            parts = full_title.split(" by ")
            if len(parts) > 1:
                book_name = parts[0].strip()
                author_part = parts[1]
                # Try to split by dash
                author_split = re.split(r'\s+[-–—\ufffd]\s+', author_part)
                author_name = author_split[0].strip()
            else:
                book_name = full_title
                author_name = "Unknown"
                
        # Clean up any residual quotes or strange characters
        book_name = book_name.replace("Review:", "").strip()
        
        books.append({
            'Name of Series': book_name,
            'Author Name': author_name,
            'Publisher': "",
            'GoodReads series link': "",
            'Number of PRIMARY books in the series': 1,
            'Rating (out of 5) of Primary Book 1': "",
            'Ratings (#) of Primary Book 1': "",
            'Synopsis (if available)': "",
            'Romantasy = Yes or No?': "Yes",
            'Romantasy Sub-Genre of series': "",
            'Name of agent in the main folder': ""
        })
        
    # Find next page
    next_link = soup.select_one('a.next, a.next-page, .pagination a.next, .nav-previous a')
    if next_link:
        current_url = next_link.get('href')
        page += 1
    else:
        current_url = None

print(f"\nFinished scraping. Extracted {len(books)} books.")

# Load existing excel or create new
file_path = r"E:\Internship\PocketFM\New_Romantasy_Books.xlsx"
df_new = pd.DataFrame(books)

try:
    df_existing = pd.read_excel(file_path)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
except Exception as e:
    print(f"Could not read existing file, saving as new: {e}")
    df_combined = df_new

df_combined.to_excel(file_path, index=False)

import os
os.system("python format_new_romantasy.py")
print("Saved books to New_Romantasy_Books.xlsx and applied premium formatting.")
