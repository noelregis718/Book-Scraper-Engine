from bs4 import BeautifulSoup

with open('bn_dump.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

products = soup.find_all('div', class_='product-shelf-info')
print(f"Found {len(products)} products with 'product-shelf-info'")

if len(products) == 0:
    products = soup.find_all('div', class_='product-info')
    print(f"Found {len(products)} products with 'product-info'")

for i, product in enumerate(products[:5]):
    title_element = product.find('a', title=True)
    if not title_element:
        title_element = product.find('a')
    title = title_element.text.strip() if title_element else 'No Title'
    
    author_element = product.find('div', class_='product-shelf-author')
    if not author_element:
        author_element = product.find(class_=lambda c: c and 'author' in c.lower())
    author = author_element.text.strip() if author_element else 'No Author'
    
    print(f"{i+1}. {title} by {author}")
