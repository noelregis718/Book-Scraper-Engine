import pandas as pd
import requests
import json
import re
import os
import subprocess
import time
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

token = get_access_token()
headers = {'Authorization': f'Bearer {token}'}

missing_shows = df[~df['Show / Title'].apply(clean_title).isin(local_files)]
print(f"Attempting to download {len(missing_shows)} missing documents from Google Drive...", flush=True)

def download_show(row_tuple):
    idx, row = row_tuple
    title = row['Show / Title']
    link = row.get('Drive Link', '')
    if pd.isna(link): link = title
    
    file_id = None
    if 'drive.google.com' in str(link) or 'docs.google.com' in str(link):
        match = re.search(r'/(?:folders|d)/([a-zA-Z0-9_-]+)', str(link))
        if match: file_id = match.group(1)
    
    if not file_id:
        search_name = str(link).replace("'", "\\'")
        q = f"name contains '{search_name}' and trashed = false"
        try:
            res = requests.get(f'https://www.googleapis.com/drive/v3/files?q={q}&fields=files(id,name,mimeType)', headers=headers, timeout=10)
            if res.status_code == 200 and res.json().get('files'):
                file_id = res.json()['files'][0]['id']
                if res.json()['files'][0]['mimeType'] == 'application/vnd.google-apps.folder':
                    q2 = f"'{file_id}' in parents and trashed = false"
                    res2 = requests.get(f'https://www.googleapis.com/drive/v3/files?q={q2}&fields=files(id,name,mimeType)', headers=headers, timeout=10)
                    if res2.status_code == 200 and res2.json().get('files'):
                        doc_files = [f for f in res2.json()['files'] if 'folder' not in f['mimeType']]
                        if doc_files: file_id = doc_files[0]['id']
        except: pass

    if file_id:
        try:
            res = requests.get(f'https://www.googleapis.com/drive/v3/files/{file_id}?fields=name,mimeType', headers=headers, timeout=10)
            if res.status_code == 200:
                meta = res.json()
                mime = meta.get('mimeType')
                save_path = os.path.join(target_folder, f"{clean_title(title)}.docx")
                
                if mime == 'application/vnd.google-apps.document':
                    export_url = f'https://www.googleapis.com/drive/v3/files/{file_id}/export?mimeType=application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    doc_res = requests.get(export_url, headers=headers, timeout=15)
                    if doc_res.status_code == 200:
                        with open(save_path, 'wb') as f: f.write(doc_res.content)
                        return f"Downloaded Google Doc: {title}"
                else:
                    dl_url = f'https://www.googleapis.com/drive/v3/files/{file_id}?alt=media'
                    dl_res = requests.get(dl_url, headers=headers, timeout=15)
                    if dl_res.status_code == 200:
                        with open(save_path, 'wb') as f: f.write(dl_res.content)
                        return f"Downloaded File: {title}"
        except: pass
    return f"Failed: {title}"

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(download_show, missing_shows.iterrows()))

downloaded = sum(1 for r in results if 'Downloaded' in r)
for r in results: print(r, flush=True)

print(f"\nSuccessfully downloaded {downloaded} documents into Final_Upload_Docs!", flush=True)
