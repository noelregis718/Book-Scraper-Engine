import requests
from bs4 import BeautifulSoup

url = "https://www.rebelangel.co.uk/category/book-reviews/romantasy-fantasy/"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

posts = soup.find_all('article')
if not posts:
    # Try different standard selectors
    posts = soup.select('.post, .type-post, article')

print(f"Found {len(posts)} posts on the first page.")

for i, post in enumerate(posts[:5]):
    title_tag = post.find(['h1', 'h2', 'h3'])
    title = title_tag.text.strip() if title_tag else "No Title"
    print(f"{i+1}. Title: {title}")

# Check pagination
next_link = soup.select_one('a.next, a.next-page, .pagination a.next, .nav-previous a')
if next_link:
    print(f"\nNext Page URL: {next_link.get('href')}")
else:
    print("\nNo next page link found using standard selectors.")
