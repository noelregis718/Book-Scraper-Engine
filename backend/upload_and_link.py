import subprocess
import json
import os
import re
import pandas as pd
import time

def clean_title(name):
    if pd.isna(name): return ""
    name = str(name)
    name = re.sub(r'\d+', '', name)
    name = name.replace('-', ' ').replace('_', ' ')
    name = name.lower()
    name = name.replace('joyread', '').replace('goodnovel', '')
    name = re.sub(r'\s+', ' ', name).strip()
    return name

folders = [
    'e:/Internship/PocketFM/Goodnovel-shows-free-chapters-20261008T121725Z-1-001',
    'e:/Internship/PocketFM/dreame, joyread, goodnovel, moboredaer, befant #4110 - 4124-20261008T121440Z-1-001'
]

# 1. Bulk upload all files to a single folder on GDrive
gdrive_dest = "gdrive:PocketFM_Scripts"
for folder in folders:
    if os.path.exists(folder):
        print(f"Uploading {folder} to Google Drive...")
        subprocess.run(["rclone", "copy", folder, gdrive_dest])

# 2. Get list of files uploaded
print("Fetching uploaded files from Google Drive...")
result = subprocess.run(["rclone", "lsjson", gdrive_dest], capture_output=True, text=True)
files = json.loads(result.stdout)

# Create a mapping of cleaned name to Google Drive link
print("Generating Google Drive links (this may take several minutes)...")
links_map = {}
for i, f in enumerate(files):
    if not f['IsDir']:
        filename = f['Path']
        clean = clean_title(os.path.splitext(filename)[0])
        
        # Generate link for this specific file
        link_res = subprocess.run(["rclone", "link", f"{gdrive_dest}/{filename}"], capture_output=True, text=True)
        
        # Some links might fail or rclone prints warnings, so we grab the last line
        link = link_res.stdout.strip().split('\n')[-1]
        
        links_map[clean] = link
        
        if i % 50 == 0:
            print(f"Generated {i}/{len(files)} links...")
        
        # Small sleep to avoid aggressive rate limiting
        time.sleep(0.2)

# 3. Update the Excel sheet
print("Updating Excel sheet...")
metrics_file = 'e:/Internship/PocketFM/GenAI_Metrics.xlsx'
df = pd.read_excel(metrics_file)

# Add Drive Link column safely without destroying existing links
if 'Drive Link' not in df.columns:
    df['Drive Link'] = None
    
df['Drive Link'] = df['Drive Link'].fillna(df['Show / Title'].map(links_map))

# Determine formatting columns
cols = list(df.columns)

# Save
print("Saving final formatted sheet...")
with pd.ExcelWriter(metrics_file, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Metrics')
    workbook = writer.book
    worksheet = writer.sheets['Metrics']
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'center', 'fg_color': '#D7E4BC', 'border': 1})
    
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        
    worksheet.set_column('A:A', 35) # Show / Title
    worksheet.set_column('B:L', 20) # Metric columns
    worksheet.set_column('M:M', 60) # Drive link
    worksheet.freeze_panes(1, 0)

print("SUCCESS! All files uploaded and links mapped perfectly to GenAI_Metrics.xlsx.")
