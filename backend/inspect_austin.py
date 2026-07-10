import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.austinmacauley.com/genre/erotica-romance-fiction'
headers = {'User-Agent': 'Mozilla/5.0'}
r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')

with open('austin_dump.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())

# Let's find some common container names
articles = soup.find_all('article')
if not articles:
    articles = soup.find_all(class_=re.compile(r'book|product|item', re.I))

print(f"Found {len(articles)} potential book containers.")

for i, a in enumerate(articles[:5]):
    title = a.find(re.compile(r'h[1-6]'))
    title_text = title.text.strip() if title else "No Title Found"
    
    # Try to find author
    author_el = a.find(class_=re.compile(r'author', re.I))
    author_text = author_el.text.strip() if author_el else "No Author Found"
    
    print(f"[{i}] Title: {title_text} | Author: {author_text}")

# Check pagination
pag = soup.find(class_=re.compile(r'pager|pagination|next', re.I))
if pag:
    print("Pagination found:")
    print(pag.prettify()[:300])
else:
    print("No obvious pagination found.")
