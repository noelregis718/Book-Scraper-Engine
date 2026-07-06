from bs4 import BeautifulSoup

with open('e:/Internship/PocketFM/backend/harlequin_dump.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

hits = soup.find_all(class_=lambda x: x and 'ais-hits-item' in x.lower())
print(f'Found {len(hits)} Algolia hits.')

if hits:
    print(hits[0].prettify()[:1000])
    
    # Let's extract the title and author for the first 5 hits to build the parser
    for h in hits[:5]:
        title = h.find('p', class_='snize-title')
        title_text = title.text.strip() if title else 'No Title'
        
        # Algolia instantsearch often stores data in data attributes, or we can just find it in the HTML
        print(f"Book HTML sample for {title_text}:")
        print(h.prettify()[:300])
        print("-------------")
