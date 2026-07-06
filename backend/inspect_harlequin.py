import requests
from bs4 import BeautifulSoup

url = 'https://harlequin.com/pages/romance-bestsellers'
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(response.text, 'html.parser')

print("Looking for typical Shopify product classes...")
products = soup.find_all(class_=lambda x: x and any(c in x.lower() for c in ['card__information', 'product-card', 'grid-item', 'product-item']))

print(f'Found {len(products)} products')
if products:
    for p in products[:3]:
        print(p.text.strip().replace('\n', ' '))
        print("-------------")
else:
    print("Trying to find h3 or h2 titles...")
    for h in soup.find_all(['h2', 'h3'])[:10]:
        print(f"{h.name}: {h.text.strip()}")
