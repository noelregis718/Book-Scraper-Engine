import pandas as pd
import requests
import json
import re
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

def get_access_token():
    res = subprocess.run(["rclone", "config", "dump"], capture_output=True, text=True)
    try:
        config = json.loads(res.stdout)
        token_str = config.get("gdrive", {}).get("token", "{}")
        token_data = json.loads(token_str)
        return token_data.get("access_token")
    except:
        return None

def clean_title(name):
    if pd.isna(name): return ''
    name = str(name)
    name = name.replace('.docx', '').replace('.pdf', '')
    name = re.sub(r'\d+', '', name)
    name = name.replace('-', ' ').replace('_', ' ')
    name = name.lower()
    for p in ['joyread', 'goodnovel', 'dreame', 'moboreader', 'moboredaer', 'befant', 'shows', 'free', 'chapters', 'chapter']:
        name = name.replace(p, '')
    return re.sub(r'\s+', ' ', name).strip()

token = get_access_token()
headers = {"Authorization": f"Bearer {token}"}

discovered_docs = []

def process_url(url):
    if not isinstance(url, str): return url
    match = re.search(r'/(?:folders|d)/([a-zA-Z0-9_-]+)', url)
    if not match: return url
    file_id = match.group(1)
    
    name = url
    try:
        res = requests.get(f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=name,mimeType", headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            name = data.get('name', url)
            
            if data.get('mimeType') == 'application/vnd.google-apps.folder':
                query = f"'{file_id}' in parents and trashed = false"
                res_list = requests.get(f"https://www.googleapis.com/drive/v3/files?q={query}&fields=files(id,name,mimeType)", headers=headers, timeout=10)
                if res_list.status_code == 200:
                    for f in res_list.json().get('files', []):
                        if f.get('mimeType') != 'application/vnd.google-apps.folder':
                            discovered_docs.append({'folder_url': url, 'file_name': f.get('name'), 'file_id': f.get('id')})
    except Exception:
        pass
    return name

file_path = 'e:/Internship/PocketFM/Matched_Series.xlsx'
df = pd.read_excel(file_path)
link_cols = ['Source link', 'Crawled Script', 'Original URL', 'Alternate Links', 'Output Drive link']

unique_urls = set()
for col in link_cols:
    if col in df.columns:
        for val in df[col]:
            if isinstance(val, str) and ('drive.google.com' in val or 'docs.google.com' in val):
                # Clean off query params if any
                clean_url = val.split('?')[0] if '?' in val else val
                unique_urls.add(val)

print(f"Found {len(unique_urls)} remaining private Drive URLs to process.")

url_to_name = {}
print("Fetching folder names and scanning their contents using Google Drive API (multithreaded)...")
with ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(process_url, unique_urls))
    for url, name in zip(unique_urls, results):
        url_to_name[url] = name

for col in link_cols:
    if col in df.columns:
        df[col] = df[col].apply(lambda x: url_to_name.get(x, x) if isinstance(x, str) else x)

print("Saving updated Matched_Series.xlsx...")
with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Matched Data')
    workbook = writer.book
    worksheet = writer.sheets['Matched Data']
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'center', 'fg_color': '#D7E4BC', 'border': 1})
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('A:A', 35)
    worksheet.set_column('B:F', 50)
    worksheet.freeze_panes(1, 0)

print(f"\nScanned inside those folders and discovered {len(discovered_docs)} files.")

print("Checking against GenAI_Metrics.xlsx...")
metrics_df = pd.read_excel('e:/Internship/PocketFM/GenAI_Metrics.xlsx')
existing_names = set(metrics_df['Show / Title'].dropna().tolist())

print("Checking against Vikrant Sheet for CPI data...")
vikrant_df = pd.read_excel('e:/Internship/PocketFM/Vikrant Sheet.xlsx', sheet_name='LC data - 7.10.26')
vikrant_df['Cleaned Show'] = vikrant_df['Show / Title'].apply(clean_title)
cpi_titles = set(vikrant_df.dropna(subset=['CPI (GenAI)'])['Cleaned Show'].tolist())

valid_actionable_files = []
for doc in discovered_docs:
    c_name = clean_title(doc['file_name'])
    if c_name and c_name not in existing_names and c_name in cpi_titles:
        valid_actionable_files.append((c_name, doc['file_name']))

print("\n" + "="*70)
print(f"Found {len(valid_actionable_files)} highly actionable documents hidden in those folders!")
print(f"(They are NEW to our tracker AND have valid CPI data)")
print("="*70)

# Deduplicate
unique_valid = {}
for c_name, orig_name in valid_actionable_files:
    unique_valid[c_name] = orig_name

for i, (c_name, orig_name) in enumerate(unique_valid.items()):
    print(f"{i+1}. {c_name}  (Original: {orig_name})")

print(f"\nTotal Unique Actionable: {len(unique_valid)}")
