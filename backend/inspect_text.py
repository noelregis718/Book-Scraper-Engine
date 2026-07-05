from bs4 import BeautifulSoup
import re

with open('e:/Internship/PocketFM/backend/panmac_dump.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

# Remove scripts, styles
for tag in soup(["script", "style", "noscript", "svg", "header", "footer"]):
    tag.decompose()

text = soup.get_text(separator='\n')
# clean up empty lines
lines = [line.strip() for line in text.split('\n') if line.strip()]

print("\n".join(lines[:200])) # print first 200 lines of visible text
