import requests
from bs4 import BeautifulSoup

url = 'https://harlequin.com/pages/romance-bestsellers?page=2'
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(response.text, 'html.parser')

products = soup.find_all('div', class_='card-product')
print(f'Found {len(products)} products on page 2.')
if products:
    print("First book on page 2:", products[0].find('h3').text.strip())

# Also check for a next button to see how pagination is handled
next_btn = soup.find('a', class_='next') or soup.find(string='Next')
if next_btn:
    print("Next button found!")
else:
    print("No next button found in HTML.")
