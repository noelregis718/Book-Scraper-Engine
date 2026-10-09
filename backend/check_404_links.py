import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor

df = pd.read_excel('e:/Internship/PocketFM/GenAI_Metrics.xlsx')

error_404_data = []

def check_link(row_tuple):
    idx, row = row_tuple
    link = row.get('Drive Link')
    title = row.get('Show / Title')
    
    if pd.isna(link) or 'http' not in str(link):
        return None
        
    try:
        # Check the link without downloading the whole file
        res = requests.get(str(link), allow_redirects=True, timeout=10)
        # 404 indicates the file is completely missing/malformed
        if res.status_code == 404:
            return {'Row Number': idx + 2, 'Show / Title': title, 'Drive Link': link}
    except Exception as e:
        return {'Row Number': idx + 2, 'Show / Title': title, 'Drive Link': link, 'Error': str(e)}
    
    return None

print(f"Checking {len(df)} rows for broken 404 links...")

with ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(check_link, df.iterrows()))

for r in results:
    if r:
        error_404_data.append(r)

if error_404_data:
    error_df = pd.DataFrame(error_404_data)
    error_df.to_excel('e:/Internship/PocketFM/404_Error_Links.xlsx', index=False)
    print(f"Found {len(error_404_data)} broken links returning a 404 error.")
    print("They have been saved to '404_Error_Links.xlsx'.")
else:
    print("No 404 broken links found!")
