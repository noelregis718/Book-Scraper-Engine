from bs4 import BeautifulSoup

with open('e:/Internship/PocketFM/backend/harlequin_dump.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

products = soup.find_all('div', class_='card-product')
print(f"Found {len(products)} products.")
for p in products[:3]:
    title = p.find('h3', class_='card-product__title')
    title_text = title.text.strip() if title else 'No Title'
    author = p.find('p', class_='card-product__detail')
    author_text = author.find('a').text.strip() if (author and author.find('a')) else 'No Author'
    print(f" - {title_text} by {author_text}")

if not products:
    print("Checking other typical elements:")
    for a in soup.find_all('a')[:20]:
        print(a.get('class'), a.text.strip()[:30])

pagination = soup.find(class_=lambda x: x and 'pagination' in x.lower())
if pagination:
    print("\nPagination HTML:")
    print(pagination.prettify()[:500])
else:
    print("\nNo element with class containing 'pagination' found.")
    
# Check for 'Next' button specifically
next_btn = soup.find('a', string=lambda s: s and 'next' in s.lower())
if next_btn:
    print("\nFound next button:", next_btn)
else:
    print("\nNo 'Next' button found.")
