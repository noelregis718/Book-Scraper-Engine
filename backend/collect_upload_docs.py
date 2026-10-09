import pandas as pd
import os
import re
import shutil

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

# 1. Map all local files
local_files_map = {}
for root, dirs, files in os.walk(base_dir):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for file in files:
        if file.endswith('.docx') or file.endswith('.doc'):
            if 'SOP' in file or 'Lifecycle' in file: continue
            cleaned = clean_title(file)
            if cleaned: 
                # Keep the first matched path
                if cleaned not in local_files_map:
                    local_files_map[cleaned] = os.path.join(root, file)

# 2. Get the 142 shows from Metrics
df = pd.read_excel('e:/Internship/PocketFM/GenAI_Metrics.xlsx')

target_folder = 'e:/Internship/PocketFM/Final_Upload_Docs'
if not os.path.exists(target_folder):
    os.makedirs(target_folder)

copied_count = 0
for title in df['Show / Title'].dropna():
    cleaned_title = clean_title(title)
    if cleaned_title in local_files_map:
        source_path = local_files_map[cleaned_title]
        dest_path = os.path.join(target_folder, os.path.basename(source_path))
        
        # In case of duplicate filenames across different folders, handle it
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(dest_path)
            dest_path = f"{base}_{copied_count}{ext}"
            
        shutil.copy2(source_path, dest_path)
        copied_count += 1

print(f"Successfully copied {copied_count} physical documents into {target_folder}!")
