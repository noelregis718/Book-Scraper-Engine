import pandas as pd
import re

df = pd.read_excel(r'E:\Internship\PocketFM\Amazon Keyword - Romantasy.xlsx')
urls = df['Amazon URL'].dropna().tail(20)
for u in urls:
    m = re.search(r'sr_1_(\d+)', str(u))
    print(f"Rank: {m.group(1) if m else 'N/A'} | URL: {str(u)[:50]}...")
