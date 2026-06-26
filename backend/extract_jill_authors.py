import sys
from bs4 import BeautifulSoup
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('jill_rendered.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("--- H2 Tags ---")
authors = set()
for h2 in soup.find_all('h2'):
    text = h2.text.strip()
    if text and len(text.split()) >= 2:
        authors.add(text)

for a in sorted(list(authors)):
    print(a)

print("\n--- H3 Tags ---")
authors3 = set()
for h3 in soup.find_all('h3'):
    text = h3.text.strip()
    if text and len(text.split()) >= 2:
        authors3.add(text)
        
for a in sorted(list(authors3)):
    print(a)
    
print("\n--- H4 Tags ---")
authors4 = set()
for h4 in soup.find_all('h4'):
    text = h4.text.strip()
    if text and len(text.split()) >= 2:
        authors4.add(text)
        
for a in sorted(list(authors4)):
    print(a)
