import pandas as pd
import os
import re

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

print("Sweeping the entire workspace for Word documents...")
local_files = {}

for root, dirs, files in os.walk(base_dir):
    # Modify dirs in-place to skip excluded directories
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    
    for file in files:
        if file.endswith('.docx') or file.endswith('.doc'):
            # Skip the SOP doc and other non-script docs
            if 'SOP' in file or 'Lifecycle' in file:
                continue
                
            cleaned = clean_title(file)
            if cleaned:
                local_files[cleaned] = os.path.join(root, file)

print(f"Found {len(local_files)} unique Word documents stored locally.")

print("Loading GenAI_Metrics.xlsx to filter out already added shows...")
metrics_file = 'e:/Internship/PocketFM/GenAI_Metrics.xlsx'
metrics_df = pd.read_excel(metrics_file)
existing_names = set(metrics_df['Show / Title'].dropna().tolist())

new_titles = {k: v for k, v in local_files.items() if k not in existing_names}
print(f"Out of those, {len(new_titles)} are entirely NEW and not in the Metrics sheet.")

print("Loading Vikrant Sheet to check for CPI data...")
vikrant_df = pd.read_excel('e:/Internship/PocketFM/Vikrant Sheet.xlsx', sheet_name='LC data - 7.10.26')
vikrant_df['Cleaned Show'] = vikrant_df['Show / Title'].apply(clean_title)

# Only keep rows with CPI
cpi_titles = set(vikrant_df.dropna(subset=['CPI (GenAI)'])['Cleaned Show'].tolist())

# Intersection
valid_actionable = {k: v for k, v in new_titles.items() if k in cpi_titles}

print("\n" + "="*70)
print(f"Found {len(valid_actionable)} documents that are NEW and have valid CPI data!")
print("="*70)

for c_name, filepath in valid_actionable.items():
    print(f"- {c_name} (File: {os.path.basename(filepath)})")

if len(valid_actionable) == 0:
    print("\nWe have officially processed every single valid document in the workspace!")
