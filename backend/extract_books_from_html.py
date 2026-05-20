from bs4 import BeautifulSoup

with open("full_dom.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

count = 0
for link in soup.find_all(class_="textlink"):
    title = link.get_text(strip=True)
    author_p = link.find_next_sibling("p")
    author = author_p.get_text(separator=" ", strip=True) if author_p else "Unknown"
    print(f"Title: {title} | Author: {author}")
    count += 1
    if count >= 10:
        break
