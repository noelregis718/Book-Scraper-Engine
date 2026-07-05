from bs4 import BeautifulSoup
import re

with open('e:/Internship/PocketFM/backend/panmac_dump.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
    tag.decompose()

text = soup.get_text(separator='\n')
lines = [line.strip() for line in text.split('\n') if line.strip()]

books = []
for i, line in enumerate(lines):
    if line == "BUY":
        if i >= 2:
            author = lines[i-1]
            title = lines[i-2]
            # Extra filter: avoid accidentally grabbing "Show 50" as a title
            if title.startswith("Show "):
                continue
            books.append((title, author))

for b in books:
    print(f"Title: {b[0]} | Author: {b[1]}")
print(f"Total found: {len(books)}")
