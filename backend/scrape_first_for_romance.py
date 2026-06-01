import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

base_url = 'https://www.firstforromance.com/index.php?route=product/all&page={}'
page = 1
books_data = []

print("Starting to scrape First For Romance...")
while True:
    url = base_url.format(page)
    try:
        res = requests.get(url, timeout=15)
    except Exception as e:
        print(f"Error fetching page {page}: {e}")
        break
        
    soup = BeautifulSoup(res.text, 'html.parser')
    boxes = soup.select('div.product-list-box')
    
    if not boxes:
        print(f"No more books found on page {page}. Stopping pagination.")
        break
        
    print(f"Scraping Page {page}: Found {len(boxes)} books...")
    
    for box in boxes:
        title_el = box.select_one('.title-link')
        author_el = box.select_one('.author_link_book_listing')
        
        title = title_el.text.strip() if title_el else "Unknown Title"
        author = author_el.text.strip() if author_el else "Unknown Author"
        
        books_data.append({
            "Book Name": title,
            "Author Name": author
        })
        
    page += 1
    time.sleep(1) # Be polite to the server

df = pd.DataFrame(books_data)
out_path = r"E:\Internship\PocketFM\first_for_romance_books.xlsx"
df.to_excel(out_path, index=False)
print(f"Successfully scraped {len(books_data)} books and saved to {out_path}!")
