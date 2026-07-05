import re
html = open('e:/Internship/PocketFM/backend/panmac_dump.html', encoding='utf-8').read()
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print('Found', len(scripts), 'scripts')
match = [s for s in scripts if 'Good Intentions' in s or 'books' in s]
print('Found matches:', len(match))
if match:
    print(match[0][:1000])
