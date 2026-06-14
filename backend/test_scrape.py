import requests

headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get('https://www.sourcebooks.com/fiction/romance', headers=headers)
with open('page.html', 'w', encoding='utf-8') as f:
    f.write(res.text)
