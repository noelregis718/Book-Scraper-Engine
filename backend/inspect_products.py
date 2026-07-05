from bs4 import BeautifulSoup
import json

with open('e:/Internship/PocketFM/backend/panmac_dump.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

products = soup.find_all('li', class_='product')
print(f'Found {len(products)} products')
if products:
    print(products[0].prettify()[:1000])
