from curl_cffi import requests
from bs4 import BeautifulSoup

def test_url(url):
    print(f"Testing URL: {url}")
    try:
        response = requests.get(url, impersonate="chrome120")
        print(f"Status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        books = soup.select('a[href^="/w/"]')
        titles = []
        for b in books:
            title = b.text.strip() or b.get('title')
            if title and len(title) > 2 and title not in titles:
                titles.append(title)
                
        print(f"Found {len(titles)} books. First 5: {titles[:5]}")
    except Exception as e:
        print(f"Error: {e}")

# Page 1
test_url("https://www.barnesandnoble.com/pages/bestsellers?orderBy=attributes.mfield_bnb__salesRank&attributes.subjectCategoryDisplayName=Fantasy+Romance")
# Page 2
test_url("https://www.barnesandnoble.com/pages/bestsellers?orderBy=attributes.mfield_bnb__salesRank&attributes.subjectCategoryDisplayName=Fantasy+Romance&page=2")
