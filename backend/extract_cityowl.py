from bs4 import BeautifulSoup
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('cityowl_rendered.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("--- H2 Tags ---")
h2s = set()
for h2 in soup.find_all('h2'):
    text = h2.text.strip()
    if text:
        h2s.add(text)
for t in list(h2s)[:20]: print(t)

print("\n--- H3 Tags ---")
h3s = set()
for h3 in soup.find_all('h3'):
    text = h3.text.strip()
    if text:
        h3s.add(text)
for t in list(h3s)[:20]: print(t)

print("\n--- H4 Tags ---")
h4s = set()
for h4 in soup.find_all('h4'):
    text = h4.text.strip()
    if text:
        h4s.add(text)
for t in list(h4s)[:20]: print(t)

print("\n--- Product/Title Classes ---")
# Check common Shopify classes
for c in ['grid-view-item__title', 'product-card__title', 'product-item__title', 'title', 'card__heading']:
    items = soup.find_all(class_=c)
    if items:
        print(f"Class: {c}")
        for i in items[:5]:
            print(i.text.strip())
