from bs4 import BeautifulSoup

with open('jill_html.txt', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

links = soup.find_all('a')
for a in links:
    text = a.text.strip()
    if text and len(text.split()) >= 2:
        print(f"Text: {text} | Class: {a.get('class')} | Href: {a.get('href')}")
