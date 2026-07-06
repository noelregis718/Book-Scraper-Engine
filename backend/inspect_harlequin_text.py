from bs4 import BeautifulSoup

with open('e:/Internship/PocketFM/backend/harlequin_dump.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "template"]):
    tag.decompose()

text = soup.get_text(separator='\n')
lines = [line.strip() for line in text.split('\n') if line.strip()]

# Let's see if we find any book authors by looking for "by " or just printing the first 100 lines
print("\n".join(lines[:100]))
