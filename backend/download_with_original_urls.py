import pandas as pd
import requests
import json
import re
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

def get_access_token():
    res = subprocess.run(['rclone', 'config', 'dump'], capture_output=True, text=True)
    try:
        config = json.loads(res.stdout)
        return json.loads(config.get('gdrive', {}).get('token', '{}')).get('access_token')
    except: return None

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

base_dir = 'e:/Internship/PocketFM'
exclude_dirs = {'.git', 'node_modules', '.vscode', '.kilo', 'backend', 'frontend', 'webapp', 'scratch', 'Drive_Folder_Zips', 'New Revenue Statement Calculation', 'docs'}

local_files = set()
for root, dirs, files in os.walk(base_dir):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for file in files:
        if file.endswith('.docx') or file.endswith('.doc'):
            if 'SOP' in file or 'Lifecycle' in file: continue
            cleaned = clean_title(file)
            if cleaned: local_files.add(cleaned)

df = pd.read_excel('e:/Internship/PocketFM/GenAI_Metrics.xlsx')
target_folder = 'e:/Internship/PocketFM/Final_Upload_Docs'

missing_titles = set(df[~df['Show / Title'].apply(clean_title).isin(local_files)]['Show / Title'].apply(clean_title).tolist())

token = get_access_token()
headers = {'Authorization': f'Bearer {token}'}

# Collect ALL raw URLs from the new sheet and the CSV
all_urls = set()
new_df = pd.read_excel('e:/Internship/PocketFM/Matched Series - New.xlsx')
for col in ['Source link', 'Crawled Script', 'Original URL', 'Alternate Links', 'Output Drive link']:
    if col in new_df.columns:
        for val in new_df[col].dropna():
            if isinstance(val, str) and ('drive.google.com' in val or 'docs.google.com' in val):
                # Clean off query params if any
                clean_url = val.split('?')[0] if '?' in val else val
                for part in clean_url.split(','):
                    if 'drive.google.com' in part or 'docs.google.com' in part:
                        all_urls.add(part.strip())

try:
    acc_df = pd.read_csv('e:/Internship/PocketFM/accessible_drive_links.csv')
    for val in acc_df['Link'].dropna():
        clean_url = val.split('?')[0] if '?' in val else val
        all_urls.add(clean_url.strip())
except: pass

print(f"Collected {len(all_urls)} raw URLs to process. Looking for {len(missing_titles)} missing titles.", flush=True)

def process_url(link):
    match = re.search(r'/(?:folders|d)/([a-zA-Z0-9_-]+)', link)
    if not match: return "No ID in URL"
    file_id = match.group(1)
    
    try:
        res = requests.get(f'https://www.googleapis.com/drive/v3/files/{file_id}?fields=name,mimeType', headers=headers, timeout=10)
        if res.status_code == 200:
            meta = res.json()
            name = clean_title(meta.get('name', ''))
            
            # Is this one of the missing titles? Or wait, if it's a folder, its contents might be the missing title!
            if meta.get('mimeType') == 'application/vnd.google-apps.folder':
                q2 = f"'{file_id}' in parents and trashed = false"
                res2 = requests.get(f'https://www.googleapis.com/drive/v3/files?q={q2}&fields=files(id,name,mimeType)', headers=headers, timeout=10)
                if res2.status_code == 200 and res2.json().get('files'):
                    for f in res2.json().get('files'):
                        if 'folder' not in f['mimeType']:
                            f_name = clean_title(f.get('name', ''))
                            if f_name in missing_titles or name in missing_titles:
                                # We found a match! Download this file!
                                doc_id = f['id']
                                doc_mime = f['mimeType']
                                
                                title_to_use = f_name if f_name in missing_titles else name
                                save_path = os.path.join(target_folder, f"{title_to_use}.docx")
                                
                                if doc_mime == 'application/vnd.google-apps.document':
                                    export_url = f'https://www.googleapis.com/drive/v3/files/{doc_id}/export?mimeType=application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                                    doc_res = requests.get(export_url, headers=headers, timeout=20)
                                    if doc_res.status_code == 200:
                                        with open(save_path, 'wb') as file_obj: file_obj.write(doc_res.content)
                                        return f"Downloaded Google Doc: {title_to_use}"
                                else:
                                    dl_url = f'https://www.googleapis.com/drive/v3/files/{doc_id}?alt=media'
                                    dl_res = requests.get(dl_url, headers=headers, timeout=20)
                                    if dl_res.status_code == 200:
                                        with open(save_path, 'wb') as file_obj: file_obj.write(dl_res.content)
                                        return f"Downloaded File: {title_to_use}"
                                        
            else:
                # It's a file
                if name in missing_titles:
                    save_path = os.path.join(target_folder, f"{name}.docx")
                    doc_mime = meta.get('mimeType')
                    if doc_mime == 'application/vnd.google-apps.document':
                        export_url = f'https://www.googleapis.com/drive/v3/files/{file_id}/export?mimeType=application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                        doc_res = requests.get(export_url, headers=headers, timeout=20)
                        if doc_res.status_code == 200:
                            with open(save_path, 'wb') as file_obj: file_obj.write(doc_res.content)
                            return f"Downloaded Google Doc: {name}"
                    else:
                        dl_url = f'https://www.googleapis.com/drive/v3/files/{file_id}?alt=media'
                        dl_res = requests.get(dl_url, headers=headers, timeout=20)
                        if dl_res.status_code == 200:
                            with open(save_path, 'wb') as file_obj: file_obj.write(dl_res.content)
                            return f"Downloaded File: {name}"
    except Exception as e:
        return f"Error on {link}: {str(e)}"
    
    return None # Didn't match any missing titles

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(process_url, all_urls))

downloaded = sum(1 for r in results if r and 'Downloaded' in r)
for r in results: 
    if r: print(r.encode('ascii', 'replace').decode('ascii'), flush=True)

print(f"\nSuccessfully downloaded {downloaded} documents into Final_Upload_Docs!", flush=True)
