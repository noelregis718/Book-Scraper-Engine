from bs4 import BeautifulSoup
import os

html_path = r'e:\Internship\PocketFM\backend\scratch\dijkstra_romance.html'
if not os.path.exists(html_path):
    print("HTML not found")
    exit()

soup = BeautifulSoup(open(html_path, encoding='utf-8').read(), 'html.parser')
wraps = soup.find_all('div', class_='books-by-subject-wrap')
if not wraps:
    print("Wraps not found")
    exit()

results = []
for wrap in wraps:
    title_a = wrap.find('a', href=lambda h: h and 'book-page.php' in h)
    title_span = wrap.find('span', class_='book_title_list')
    if title_span:
        title = title_span.get_text(strip=True)
    elif title_a:
        title = title_a.get_text(strip=True)
    else:
        continue
    
    if not title: continue

    author = "Unknown"
    author_a = wrap.find('a', href=lambda h: h and 'author-page.php' in h)
    if author_a:
        author = author_a.get_text(strip=True)
    else:
        # Fallback search for "By" text
        for p in wrap.find_all('p'):
            text = p.get_text()
            if 'By' in text:
                author = text.replace('By', '').strip()
                break
    
    results.append((title, author))

print(f"Found {len(results)} books.")
for title, author in results[:20]:
    print(f"{title} | {author}")

print("...")
for title, author in results[-5:]:
    print(f"{title} | {author}")
