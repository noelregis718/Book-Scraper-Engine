import bs4
import pandas as pd
import sys
import os
import subprocess
import time

def scrape_page(base_url, page_num, excel_file):
    # Determine the correct URL
    if '?' in base_url:
        url = f"{base_url}&page_current={page_num}"
    else:
        # Avoid double slashes if user included a trailing slash
        base_url = base_url.rstrip('/')
        url = f"{base_url}/?page_current={page_num}"
        
    html_file = f"temp_page_{page_num}.html"
    print(f"Fetching page {page_num}: {url}")
    
    # Use curl to bypass simple blocks
    cmd = [
        "curl.exe", 
        "-s",
        "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36", 
        "-o", html_file, 
        url
    ]
    subprocess.run(cmd)
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Failed to read {html_file}")
        return 0
        
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    cards = soup.find_all('div', class_='card-post-content')
    
    books = []
    for card in cards:
        title_tag = card.find('h3')
        author_tag = card.find('span', class_='author-item')
        
        if title_tag and author_tag:
            title = title_tag.text.strip()
            author = author_tag.text.strip()
            books.append({'Name of Series': title, 'Author Name': author})
            
    num_books = len(books)
    print(f"Found {num_books} books on page {page_num}.")
    
    if num_books > 0:
        try:
            df = pd.read_excel(excel_file)
        except FileNotFoundError:
            df = pd.DataFrame()
            
        new_df = pd.DataFrame(books)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_excel(excel_file, index=False)
        print("Saved to excel.")
        
    # Clean up
    if os.path.exists(html_file):
        os.remove(html_file)
        
    return num_books

if __name__ == '__main__':
    excel_file = 'agency_template.xlsx'
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'https://torpublishinggroup.com/genre/young-adult/new-releases'
    start_page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    page = start_page
    
    while True:
        num = scrape_page(base_url, page, excel_file)
        if num == 0:
            print("No more books found. Stopping.")
            break
        page += 1
        time.sleep(1) # Be polite
