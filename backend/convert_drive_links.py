import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time

def get_drive_title(url):
    if not isinstance(url, str): return url
    if not url.startswith('http'): return url
    if 'drive.google.com' not in url and 'docs.google.com' not in url:
        return url
        
    try:
        # Some links might be comma separated if they have multiple
        first_url = url.split(',')[0].strip()
        if not first_url.startswith('http'):
            first_url = url.split()[0].strip()
            
        res = requests.get(first_url, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            if soup.title and soup.title.string:
                title = soup.title.string
                # Clean up the Google suffix
                title = title.replace(' - Google Drive', '').replace(' - Google Docs', '')
                # Fix the weird unicode dash that sometimes appears
                title = title.replace('', '-').strip()
                
                # If it's a generic sign-in page, return the original URL
                if "meet google drive" not in title.lower() and "sign in" not in title.lower() and title != "Google Docs":
                    return title
    except Exception:
        pass
    return url

print("Loading Matched_Series.xlsx...")
file_path = 'e:/Internship/PocketFM/Matched_Series.xlsx'
df = pd.read_excel(file_path)

link_cols = ['Source link', 'Crawled Script', 'Original URL', 'Alternate Links', 'Output Drive link']

print("Converting Google Drive URLs to Folder/Document Names (this is multithreaded and may take a minute)...")

for col in link_cols:
    if col in df.columns:
        print(f"Processing '{col}'...")
        with ThreadPoolExecutor(max_workers=20) as executor:
            df[col] = list(executor.map(get_drive_title, df[col]))

print("Saving updated Matched_Series.xlsx...")
with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Matched Data')
    workbook = writer.book
    worksheet = writer.sheets['Matched Data']
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'center', 'fg_color': '#D7E4BC', 'border': 1})
    
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        
    worksheet.set_column('A:A', 35) # Show / Title
    worksheet.set_column('B:F', 50) # The converted link columns
    worksheet.freeze_panes(1, 0)

print("SUCCESS! All Drive links have been permanently replaced with their actual folder/document names.")
