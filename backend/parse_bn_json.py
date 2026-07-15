import json
import re
from bs4 import BeautifulSoup

with open('bn_dump.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

scripts = soup.find_all('script')
for i, s in enumerate(scripts):
    if s.string and '{"' in s.string:
        print(f"Script {i} contains JSON, length: {len(s.string)}")
        if '"name":' in s.string or '"title":' in s.string or '"book"' in s.string.lower():
            print("  Looks like it might contain book data!")
            # Try to find a book title snippet
            match = re.search(r'"name":"([^"]+)"', s.string)
            if match:
                print("  Example name:", match.group(1))
            
            # also look for window.__INITIAL_STATE__ or similar
            if '__INITIAL_STATE__' in s.string or '__remixContext' in s.string:
                print("  Found Remix/React initial state!")
