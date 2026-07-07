import requests
from bs4 import BeautifulSoup

url = 'https://redadeptpublishing.com/romance/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Remove nav, script, style
for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "template", "aside"]):
    tag.decompose()

text = soup.get_text(separator='\n')
lines = [line.strip() for line in text.split('\n') if line.strip()]

print("\n".join(lines[:100]))
