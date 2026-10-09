import pandas as pd
import os
import re
import subprocess
import time

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

folder = 'e:/Internship/PocketFM/content'

print(f"Scanning the {folder} folder for Word documents...")
local_files = {}
if os.path.exists(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.docx') or file.endswith('.doc'):
                cleaned = clean_title(file)
                if cleaned:
                    local_files[cleaned] = os.path.join(root, file)
else:
    print("Content folder not found!")
    exit(1)

print(f"Found {len(local_files)} valid documents in the content folder.")

print("Loading GenAI_Metrics.xlsx to check existing records...")
metrics_file = 'e:/Internship/PocketFM/GenAI_Metrics.xlsx'
metrics_df = pd.read_excel(metrics_file)
existing_names = set(metrics_df['Show / Title'].dropna().tolist())

new_titles = {k: v for k, v in local_files.items() if k not in existing_names}
print(f"Out of those, {len(new_titles)} are entirely new to the Metrics sheet.")

if not new_titles:
    print("No new files to process!")
    exit(0)

print("Loading Vikrant Sheet to check for CPI data...")
vikrant_df = pd.read_excel('e:/Internship/PocketFM/Vikrant Sheet.xlsx', sheet_name='LC data - 7.10.26')
vikrant_df['Cleaned Show'] = vikrant_df['Show / Title'].apply(clean_title)

# Only keep rows with CPI
vikrant_subset = vikrant_df.dropna(subset=['CPI (GenAI)']).drop_duplicates(subset=['Cleaned Show'])
metric_cols = list(vikrant_df.columns[17:28])
vikrant_subset = vikrant_subset[['Cleaned Show'] + metric_cols]

new_df = pd.DataFrame({'Show / Title': list(new_titles.keys())})
merged_new = pd.merge(new_df, vikrant_subset, left_on='Show / Title', right_on='Cleaned Show', how='inner') # inner join drops those without CPI
merged_new = merged_new.drop(columns=['Cleaned Show'])

print(f"After checking CPI data, we have exactly {len(merged_new)} files that are new AND have valid CPI data!")

if len(merged_new) > 0:
    gdrive_dest = "gdrive:PocketFM_Scripts"
    links_map = {}
    
    print("Uploading these specific files to Google Drive and generating links...")
    valid_titles = merged_new['Show / Title'].tolist()
    
    for i, title in enumerate(valid_titles):
        filepath = new_titles[title]
        filename = os.path.basename(filepath)
        
        print(f"[{i+1}/{len(valid_titles)}] Uploading: {filename}")
        subprocess.run(["rclone", "copyto", filepath, f"{gdrive_dest}/{filename}"])
        
        link_res = subprocess.run(["rclone", "link", f"{gdrive_dest}/{filename}"], capture_output=True, text=True)
        link = link_res.stdout.strip().split('\\n')[-1] # handle any rclone warnings
        links_map[title] = link
        time.sleep(0.2)
        
    merged_new['Drive Link'] = merged_new['Show / Title'].map(links_map)
    
    final_df = pd.concat([metrics_df, merged_new], ignore_index=True)

    print("Saving updated Metrics Sheet...")
    with pd.ExcelWriter(metrics_file, engine='xlsxwriter') as writer:
        final_df.to_excel(writer, index=False, sheet_name='Metrics')
        workbook = writer.book
        worksheet = writer.sheets['Metrics']
        header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'center', 'fg_color': '#D7E4BC', 'border': 1})
        for col_num, value in enumerate(final_df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        worksheet.set_column('A:A', 35)
        worksheet.set_column('B:L', 20)
        worksheet.set_column('M:M', 60)
        worksheet.freeze_panes(1, 0)

    print("SUCCESS! Processed content folder, uploaded files, and updated the metrics sheet.")
