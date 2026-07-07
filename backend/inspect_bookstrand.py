import requests
from bs4 import BeautifulSoup

url = 'https://www.bookstrand.com/books/erotic-romance'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}

print(f"Fetching {url}...")
try:
    response = requests.get(url, headers=headers, timeout=15)
    print(f"Status Code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try to find typical product/book containers
    containers = soup.find_all(class_=lambda x: x and any(c in x.lower() for c in ['product', 'book', 'item', 'entry']))
    print(f"Found {len(containers)} potential book containers.")
    
    if containers:
        for c in containers[:3]:
            print("-------------")
            print(c.prettify()[:500])
    else:
        print("No typical book containers found. Extracting visible text...")
        for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
            tag.decompose()
        print("\n".join([line.strip() for line in soup.get_text(separator='\n').split('\n') if line.strip()][:30]))

except Exception as e:
    print(f"Error: {e}")
