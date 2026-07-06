import requests
from bs4 import BeautifulSoup

url = 'https://harlequin.com/pages/romance-bestsellers'
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(response.text, 'html.parser')

products = soup.find_all('div', class_='card-product')
print(f'Found {len(products)} products.')

for i, p in enumerate(products[:10]):
    title_el = p.find('h3', class_='card-product__title')
    title = title_el.text.strip() if title_el else "No Title"
    
    author_el = p.find('p', class_='card-product__detail')
    author = "No Author"
    if author_el and author_el.find('a'):
        author = author_el.find('a').text.strip()
        
    print(f"{i+1}. {title} by {author}")
