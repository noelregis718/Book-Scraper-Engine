from bs4 import BeautifulSoup
import json

with open('e:/Internship/PocketFM/backend/panmac_dump.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print('Parsing dumped HTML...')
all_titles = soup.find_all(['h4', 'h3', 'h2'])
results = []
for h in all_titles:
    if h.get('class') and 'book-title' in h.get('class'):
        # Check parents for sections that might distinguish new releases vs actual books
        parents = [p.name + ('.' + '.'.join(p.get('class', []))) for p in h.parents if p.name in ['div', 'section', 'ul', 'li']]
        
        # also get author
        author_el = h.find_parent('div', class_='books')
        author_text = ""
        if author_el:
            a_tag = author_el.find(class_='author-name')
            if a_tag:
                author_text = a_tag.text.strip()
                
        results.append({
            'text': h.text.strip(),
            'author': author_text,
            'parents': parents[:3] # just top 3 immediate parents
        })

print(json.dumps(results[:10], indent=2))
print("...")
print(json.dumps(results[10:20], indent=2))
