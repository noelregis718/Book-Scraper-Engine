import pandas as pd
import requests
import json
import re
import subprocess

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

token = get_access_token()
headers = {'Authorization': f'Bearer {token}'}

# 1. Fetch the 142 files from the user's Google Drive folder
folder_id = '10AXu1LMa7dNj8EnYyAosBVFjLxURCOGL'
print("Fetching individual links from the uploaded folder...")

local_links = {}
page_token = None
while True:
    url = f"https://www.googleapis.com/drive/v3/files?q='{folder_id}'+in+parents+and+trashed=false&fields=nextPageToken,files(name,webViewLink)&pageSize=1000"
    if page_token: url += f"&pageToken={page_token}"
    
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        for f in data.get('files', []):
            local_links[clean_title(f['name'])] = f['webViewLink']
        page_token = data.get('nextPageToken')
        if not page_token: break
    else:
        print("Failed to fetch folder contents", res.text)
        break

print(f"Extracted {len(local_links)} shareable links from the uploaded folder!")

# 2. Extract URLs from Matched Series - New.xlsx
print("Extracting URLs from Matched Series - New.xlsx...")
remote_links = {}
new_df = pd.read_excel('e:/Internship/PocketFM/Matched Series - New.xlsx')

for idx, row in new_df.iterrows():
    title = row.get('Show / Title', '')
    if pd.isna(title): continue
    cleaned = clean_title(title)
    for col in ['Source link', 'Crawled Script', 'Original URL', 'Alternate Links', 'Output Drive link']:
        if col in row and isinstance(row[col], str) and ('drive.google.com' in row[col] or 'docs.google.com' in row[col]):
            remote_links[cleaned] = row[col]
            break

try:
    acc_df = pd.read_csv('e:/Internship/PocketFM/accessible_drive_links.csv')
    for val in acc_df['Link'].dropna():
        if isinstance(val, str):
            remote_links[val] = val 
except: pass

# 3. Apply ALL links to GenAI_Metrics.xlsx
metrics_file = 'e:/Internship/PocketFM/GenAI_Metrics.xlsx'
df = pd.read_excel(metrics_file)

updated_count = 0
for idx, row in df.iterrows():
    title = clean_title(row['Show / Title'])
    
    # Priority 1: User's newly uploaded folder links
    if title in local_links:
        df.at[idx, 'Drive Link'] = local_links[title]
        updated_count += 1
    # Priority 2: Original Google Drive URLs
    elif title in remote_links:
        df.at[idx, 'Drive Link'] = remote_links[title]
        updated_count += 1

with pd.ExcelWriter(metrics_file, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Metrics')
    workbook = writer.book
    worksheet = writer.sheets['Metrics']
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'center', 'fg_color': '#D7E4BC', 'border': 1})
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('A:A', 35)
    worksheet.set_column('B:L', 20)
    worksheet.set_column('M:M', 60)
    worksheet.freeze_panes(1, 0)

print(f"Successfully populated exactly {updated_count} individual Drive Links into the Metrics sheet!")
