import pandas as pd
import subprocess
import json
import re

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

print("Fetching file list from Google Drive folder...")
folder_id = "1al9K4bsc9qvAZywp2Y0-cKzdKDLl9LV-"
res = subprocess.run(["rclone", "lsjson", "gdrive:", "--drive-root-folder-id", folder_id], capture_output=True, text=True)

if res.returncode != 0:
    print("Failed to fetch folder contents. Error:")
    print(res.stderr)
    exit(1)

files = json.loads(res.stdout)
print(f"Found {len(files)} files in the folder.")

folder_titles = set()
for f in files:
    if not f['IsDir']:
        folder_titles.add(clean_title(f['Name']))

print("Loading existing Metrics Sheet to check what we've already done...")
metrics_df = pd.read_excel('e:/Internship/PocketFM/GenAI_Metrics.xlsx')
existing_names = set(metrics_df['Show / Title'].dropna().tolist())

# Filter out what we've already done
new_titles = folder_titles - existing_names
print(f"Out of those, {len(new_titles)} are entirely NEW and haven't been added yet.")

print("Loading Vikrant Sheet to check for CPI data...")
vikrant_df = pd.read_excel('e:/Internship/PocketFM/Vikrant Sheet.xlsx', sheet_name='LC data - 7.10.26')
vikrant_df['Cleaned Show'] = vikrant_df['Show / Title'].apply(clean_title)

# Only keep rows with CPI
vikrant_with_cpi = vikrant_df.dropna(subset=['CPI (GenAI)'])
cpi_titles = set(vikrant_with_cpi['Cleaned Show'].tolist())

# Find the intersection
ready_to_download = new_titles.intersection(cpi_titles)

print("\n" + "="*50)
print(f"Found {len(ready_to_download)} shows that are NEW and have valid CPI data!")
print("="*50)
for t in sorted(ready_to_download):
    # Find original name for better context
    original = [f['Name'] for f in files if not f['IsDir'] and clean_title(f['Name']) == t][0]
    print(f"- {t}  (Original File: {original})")
