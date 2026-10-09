import pandas as pd
import requests
import json
import re
import os
import subprocess

def clean_title(name):
    if pd.isna(name): return ""
    name = str(name)
    name = name.replace('.docx', '').replace('.pdf', '')
    name = re.sub(r'\d+', '', name)
    name = name.replace('-', ' ').replace('_', ' ')
    name = name.lower()
    
    platforms = ['joyread', 'goodnovel', 'dreame', 'moboreader', 'moboredaer', 'befant', 'shows', 'free', 'chapters', 'chapter']
    for p in platforms:
        name = name.replace(p, '')
        
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def get_access_token():
    res = subprocess.run(["rclone", "config", "dump"], capture_output=True, text=True)
    try:
        config = json.loads(res.stdout)
        token_str = config.get("gdrive", {}).get("token", "{}")
        token_data = json.loads(token_str)
        return token_data.get("access_token")
    except:
        return None

def get_drive_name(url, token):
    match = re.search(r'/(?:folders|d)/([a-zA-Z0-9_-]+)', url)
    if not match:
        return None
    file_id = match.group(1)
    
    api_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=name"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(api_url, headers=headers)
    if res.status_code == 200:
        return res.json().get('name')
    return None

print("Loading accessible links CSV...")
links_df = pd.read_csv('e:/Internship/PocketFM/accessible_drive_links.csv')
links = links_df['Link'].dropna().tolist()

print("Authenticating with Google Drive API...")
token = get_access_token()
if not token:
    print("Failed to get Google Drive API token from rclone.")
    exit(1)

extracted_scripts = {}

print("Fetching ACTUAL titles using Google Drive API (bypassing sign-in blocks)...")
for url in links:
    raw_name = get_drive_name(url, token)
    if raw_name:
        cleaned = clean_title(raw_name)
        if cleaned:
            extracted_scripts[cleaned] = url
            print(f"Successfully extracted private file: '{cleaned}' from URL")
    else:
        print(f"Could not extract name for: {url}")

print(f"Successfully extracted {len(extracted_scripts)} unique valid script names from URLs.")

print("Loading existing Metrics Sheet...")
metrics_file = 'e:/Internship/PocketFM/GenAI_Metrics.xlsx'
metrics_df = pd.read_excel(metrics_file)
existing_names = set(metrics_df['Show / Title'].dropna().tolist())

new_scripts = {name: url for name, url in extracted_scripts.items() if name not in existing_names}
print(f"Found {len(new_scripts)} completely new scripts that were previously blocked by sign-in.")

if not new_scripts:
    print("No new scripts to add!")
else:
    print("Loading Vikrant Sheet to find CPI data...")
    vikrant_df = pd.read_excel('e:/Internship/PocketFM/Vikrant Sheet.xlsx', sheet_name='LC data - 7.10.26')
    vikrant_df['Cleaned Show'] = vikrant_df['Show / Title'].apply(clean_title)
    
    metric_cols = list(vikrant_df.columns[17:28])
    vikrant_subset = vikrant_df[['Cleaned Show'] + metric_cols].dropna(subset=['Cleaned Show']).drop_duplicates(subset=['Cleaned Show'])
    
    new_df = pd.DataFrame({'Show / Title': list(new_scripts.keys())})
    merged_new = pd.merge(new_df, vikrant_subset, left_on='Show / Title', right_on='Cleaned Show', how='left')
    merged_new = merged_new.drop(columns=['Cleaned Show'])
    
    # Drop missing CPI data
    merged_new = merged_new.dropna(subset=['CPI (GenAI)'])
    print(f"After matching CPI data, we have {len(merged_new)} new valid rows to add.")
    
    if len(merged_new) > 0:
        merged_new['Drive Link'] = merged_new['Show / Title'].map(new_scripts)
        final_df = pd.concat([metrics_df, merged_new], ignore_index=True)
        
        print("Saving updated Metrics Sheet...")
        with pd.ExcelWriter(metrics_file, engine='xlsxwriter') as writer:
            final_df.to_excel(writer, index=False, sheet_name='Metrics')
            workbook = writer.book
            worksheet = writer.sheets['Metrics']
            header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'center', 'fg_color': '#D7E4BC', 'border': 1})
            
            for col_num, value in enumerate(final_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            worksheet.set_column('A:A', 35) # Show / Title
            worksheet.set_column('B:L', 20) # Metric columns
            worksheet.set_column('M:M', 60) # Drive link
            worksheet.freeze_panes(1, 0)
        print("SUCCESS! Metrics sheet updated with the previously inaccessible links.")
