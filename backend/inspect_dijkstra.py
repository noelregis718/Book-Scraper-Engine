import requests
from bs4 import BeautifulSoup

url = "https://dijkstraagency.com/books-by-subject.php?subject1=Romance"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Look for book entries
# Based on the markdown, they look like links followed by "By author"
books = []
for a in soup.find_all('a', href=True):
    if 'book-page.php' in a['href']:
        title = a.get_text(strip=True)
        # The author usually follows
        next_sib = a.find_next_sibling(string=True)
        author = "Unknown"
        if next_sib and 'By' in next_sib:
            # Check next link
            author_link = a.find_next_sibling('a', href=True)
            if author_link and 'author-page.php' in author_link['href']:
                author = author_link.get_text(strip=True)
        
        books.append({'title': title, 'author': author})

print(f"Found {len(books)} books.")
for b in books[:10]:
    print(b)
