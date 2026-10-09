import pandas as pd
import subprocess
import json
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

folder_id = '1al9K4bsc9qvAZywp2Y0-cKzdKDLl9LV-'
res = subprocess.run(['rclone', 'lsjson', 'gdrive:', '--drive-root-folder-id', folder_id], capture_output=True, text=True)
files = json.loads(res.stdout)

target = 'the billionaire triplets take new york'
file_obj = next((f for f in files if not f['IsDir'] and clean_title(f['Name']) == target), None)

link = f"https://docs.google.com/document/d/{file_obj['ID']}/edit" if file_obj else ''

metrics_file = 'e:/Internship/PocketFM/GenAI_Metrics.xlsx'
metrics_df = pd.read_excel(metrics_file)

vikrant_df = pd.read_excel('e:/Internship/PocketFM/Vikrant Sheet.xlsx', sheet_name='LC data - 7.10.26')
vikrant_df['Cleaned Show'] = vikrant_df['Show / Title'].apply(clean_title)

metric_cols = list(vikrant_df.columns[17:28])
vikrant_subset = vikrant_df[['Cleaned Show'] + metric_cols].dropna(subset=['Cleaned Show']).drop_duplicates(subset=['Cleaned Show'])

new_df = pd.DataFrame({'Show / Title': [target], 'Drive Link': [link]})
merged_new = pd.merge(new_df, vikrant_subset, left_on='Show / Title', right_on='Cleaned Show', how='left')
merged_new = merged_new.drop(columns=['Cleaned Show'])

final_df = pd.concat([metrics_df, merged_new], ignore_index=True)

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

print(f'Successfully appended {target} with link {link}!')
