import requests
from bs4 import BeautifulSoup

url = 'https://awfulagent.com/jabclients/'
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')

# Find the author list
authors = []
# On Jabberwocky, authors are usually in a grid or list
# Let's try common selectors
for a in soup.find_all('a', href=True):
    href = a['href']
    if '/author/' in href or 'awfulagent.com/' in href:
        if a.text.strip() and len(a.text.strip().split()) >= 2:
            authors.append((a.text.strip(), href))

for name, link in authors[:30]:
    print(f"{name} | {link}")
