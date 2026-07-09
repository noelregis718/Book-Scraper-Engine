import requests
from bs4 import BeautifulSoup
import json

url = 'https://turnerpublishing.com/collections/romance-books'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

print(f"Fetching {url}...")
try:
    response = requests.get(url, headers=headers, timeout=15)
    print(f"Status Code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    with open('turner_dump.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("Dumped to turner_dump.html")
    
    # Try to find products (common Shopify/e-comm classes)
    products = soup.find_all(class_=lambda x: x and ('product' in x.lower() or 'grid' in x.lower() or 'item' in x.lower()))
    print(f"Found {len(products)} potential product containers.")
    
    titles = soup.find_all(['h2', 'h3', 'a'], class_=lambda x: x and 'title' in x.lower())
    print(f"Found {len(titles)} potential titles.")
    if titles:
        for t in titles[:5]:
            print(f"Title: {t.text.strip()}")
        
    pagination = soup.find_all(class_=lambda x: x and ('page' in x.lower() or 'pagination' in x.lower() or 'next' in x.lower()))
    print(f"\nFound {len(pagination)} potential pagination containers.")
    if pagination:
        for p in pagination[:2]:
            print(p.prettify()[:200])

except Exception as e:
    print(f"Error: {e}")
