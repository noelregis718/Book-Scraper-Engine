import requests
from bs4 import BeautifulSoup

url = 'https://redadeptpublishing.com/romance/'
try:
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}, timeout=15)
    print(f"Status Code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try to find typical product/book containers
    containers = soup.find_all(class_=lambda x: x and any(c in x.lower() for c in ['product', 'book', 'item', 'entry']))
    print(f"Found {len(containers)} potential book containers.")
    
    if containers:
        for c in containers[:3]:
            print(c.prettify()[:500])
            print("-------------")
    else:
        print("No typical book containers found. Looking for headers (h2/h3)...")
        for h in soup.find_all(['h2', 'h3'])[:15]:
            print(f"{h.name}: {h.text.strip()}")

except Exception as e:
    print(f"Error fetching page: {e}")
