import pandas as pd
import os
import subprocess
import time
import re
from concurrent.futures import ThreadPoolExecutor

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

metrics_file = 'e:/Internship/PocketFM/GenAI_Metrics.xlsx'
df = pd.read_excel(metrics_file)

# 1. Upload local 142 files and get their links
upload_folder = 'e:/Internship/PocketFM/Final_Upload_Docs'
gdrive_dest = 'gdrive:PocketFM_Scripts'

print("Uploading 142 local files to Google Drive and generating links...", flush=True)
subprocess.run(['rclone', 'copy', upload_folder, gdrive_dest])

local_links = {}
files = [f for f in os.listdir(upload_folder) if f.endswith('.docx')]

def get_link(file):
    res = subprocess.run(['rclone', 'link', f"{gdrive_dest}/{file}"], capture_output=True, text=True)
    return clean_title(file), res.stdout.strip().split('\n')[-1]

with ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(get_link, files))
    for title, link in results:
        if link: local_links[title] = link

print(f"Generated {len(local_links)} links for local files.", flush=True)

# 2. Extract URLs from Matched Series - New.xlsx
print("Extracting URLs from Matched Series - New.xlsx...", flush=True)
remote_links = {}
new_df = pd.read_excel('e:/Internship/PocketFM/Matched Series - New.xlsx')

for idx, row in new_df.iterrows():
    title = row.get('Show / Title', '')
    if pd.isna(title): continue
    cleaned = clean_title(title)
    
    # Check all link columns
    for col in ['Source link', 'Crawled Script', 'Original URL', 'Alternate Links', 'Output Drive link']:
        if col in row and isinstance(row[col], str) and ('drive.google.com' in row[col] or 'docs.google.com' in row[col]):
            remote_links[cleaned] = row[col]
            break

# 3. Extract URLs from accessible_drive_links.csv
try:
    acc_df = pd.read_csv('e:/Internship/PocketFM/accessible_drive_links.csv')
    for val in acc_df['Link'].dropna():
        if isinstance(val, str):
            remote_links[val] = val # We'll try to map it later
except: pass

# 4. Apply links to GenAI_Metrics.xlsx
updated_count = 0
for idx, row in df.iterrows():
    title = clean_title(row['Show / Title'])
    
    # 1. Check local links (the 142 we just uploaded)
    if title in local_links:
        df.at[idx, 'Drive Link'] = local_links[title]
        updated_count += 1
    # 2. Check remote links from Matched Series
    elif title in remote_links:
        df.at[idx, 'Drive Link'] = remote_links[title]
        updated_count += 1
    # 3. If missing, just leave it with whatever it had (the folder name/text name)

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

print(f"Successfully populated EXACT Drive Links for {updated_count} out of 399 rows!")
