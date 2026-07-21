import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

all_authors = []
base_url = 'https://sbrmedia.com/authors/'
headers = {'User-Agent': 'Mozilla/5.0'}

for page in range(1, 5):
    if page == 1:
        url = base_url
    else:
        url = f"{base_url}page/{page}/"
        
    print(f"Scraping {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for a in soup.find_all('a'):
            href = a.get('href', '')
            if href.startswith('https://sbrmedia.com/authors/') and 'page/' not in href and '?ui_tax' not in href:
                name = a.text.strip()
                # filter out empty names or generic names like 'All' or 'Our Authors'
                if name and name.lower() not in ['all', 'our authors']:
                    if name not in all_authors:
                        all_authors.append(name)
    except Exception as e:
        print(f"Failed on page {page}: {e}")
        
    time.sleep(1)

print(f"Found {len(all_authors)} unique authors.")

df = pd.DataFrame({'Author Name': all_authors})
output_file = 'SBR_Media_Scraped_Authors.xlsx'
df.to_excel(output_file, index=False)
print(f"Saved to {output_file}")
