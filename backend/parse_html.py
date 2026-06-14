import re

html = open('e:/Internship/PocketFM/backend/book_page.html', encoding='utf-8').read()

# Look for series links
series_links = re.findall(r'href="([^"]*series[^"]*)"', html)
print("Series Links:")
for link in set(series_links):
    print(link)

# Look for primary works
match = re.search(r'(\d+)\s+primary\s+works', html, re.IGNORECASE)
if match:
    print(f"\nFound primary works directly in HTML: {match.group(1)}")
else:
    print("\nDid not find 'primary works' text in HTML.")
    
# Check for "book 1 of" or something similar
book_of = re.findall(r'Book (\d+) of.*?([^<]+)', html)
print(f"\nBook of matches: {book_of}")
