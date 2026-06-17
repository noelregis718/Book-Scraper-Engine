import requests
from bs4 import BeautifulSoup

def scrape_blackrose_romance():
    url = "https://www.blackrosewriting.com/romance"
    print(f"Fetching {url} ...")
    
    # We use an aggressive loop by checking for offset pagination (Squarespace standard)
    # even though it appears all 63 books load on the first request.
    all_books = set()
    
    # First page
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    items = soup.find_all(class_='product-list-item-title')
    
    for item in items:
        title = item.text.strip().replace('\n', ' ')
        all_books.add(title)
        
    print(f"Found {len(all_books)} books on the main page.")
    
    # Let's try to forcefully offset to see if there are more
    offset = len(all_books)
    while True:
        offset_url = f"{url}?offset={offset}"
        print(f"Checking for more books aggressively at offset {offset}...")
        r = requests.get(offset_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.find_all(class_='product-list-item-title')
        
        added = 0
        for item in items:
            title = item.text.strip().replace('\n', ' ')
            if title not in all_books:
                all_books.add(title)
                added += 1
                
        if added == 0:
            print("No more new books found.")
            break
        else:
            print(f"Found {added} new books.")
            offset += added

    print(f"\nTotal unique books found: {len(all_books)}")
    
    with open('blackrose_romance_books.txt', 'w', encoding='utf-8') as f:
        for title in sorted(list(all_books)):
            f.write(title + '\n')
            
    print("Successfully saved all names to blackrose_romance_books.txt")

if __name__ == '__main__':
    scrape_blackrose_romance()
