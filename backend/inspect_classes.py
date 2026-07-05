from bs4 import BeautifulSoup
from collections import Counter

with open('e:/Internship/PocketFM/backend/panmac_dump.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("Most common classes on elements with text > 10 chars:")
text_elements = [t for t in soup.find_all(True) if len(t.text.strip()) > 10 and not t.find(True)] # leaves only innermost elements

classes = []
for el in text_elements:
    cls = el.get('class')
    if cls:
        classes.append(' '.join(cls))

for cls, count in Counter(classes).most_common(20):
    print(f"{count}: {cls}")
    # print an example
    example = soup.find(class_=cls.split()[0]).text.strip()
    print(f"  Example: {example[:50]}")
