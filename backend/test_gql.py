import urllib.request
import json

q = """
query {
  products(filter: {category_uid: {eq: "NjU1"}}, pageSize: 100, currentPage: 11) {
    items {
      name
      url_key
      url_path
    }
  }
}
"""

req = urllib.request.Request(
    'https://www.sourcebooks.com/graphql',
    data=json.dumps({'query': q}).encode('utf-8'),
    headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
)
try:
    with urllib.request.urlopen(req) as response:
        print(response.status)
        print(response.read().decode('utf-8')[:500])
except Exception as e:
    print("Error:", e)
