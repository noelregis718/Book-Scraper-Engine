import pandas as pd
import os
import re

target_file = 'e:/Internship/PocketFM/Episode Metrics - Noel New.xlsx'
upload_folder = 'e:/Internship/PocketFM/Final_Upload_Docs'

df = pd.read_excel(target_file, sheet_name='Metrics (1)')

title_col = None
for col in df.columns:
    if 'show' in str(col).lower() or 'title' in str(col).lower():
        title_col = col
        break

def clean_title(name):
    if pd.isna(name): return ''
    name = str(name).replace('.docx', '').replace('.doc', '').replace('.pdf', '')
    name = re.sub(r'\d+', '', name)
    name = name.replace('-', ' ').replace('_', ' ')
    name = name.lower()
    for p in ['joyread', 'goodnovel', 'dreame', 'moboreader', 'moboredaer', 'befant', 'shows', 'free', 'chapters', 'chapter']:
        name = name.replace(p, '')
    return re.sub(r'\s+', ' ', name).strip()

sheet_titles = set()
for t in df[title_col].dropna():
    cleaned = clean_title(t)
    if cleaned:
        sheet_titles.add(cleaned)

local_names = set()
for item in os.listdir(upload_folder):
    local_names.add(clean_title(item))

sheet_only = sheet_titles - local_names
local_only = local_names - sheet_titles

fuzzy_matches = []
still_missing = list(sheet_only)
still_extra = list(local_only)

# Check for starts_with or substring matching
for s_title in list(still_missing):
    for l_title in list(still_extra):
        if len(s_title) > 5 and len(l_title) > 5:
            # If the base sheet name is inside the local file name (which has garbage characters appended)
            if s_title in l_title or l_title in s_title:
                fuzzy_matches.append((s_title, l_title))
                still_missing.remove(s_title)
                still_extra.remove(l_title)
                break

perfect_matches = len(sheet_titles.intersection(local_names))
total_matches = perfect_matches + len(fuzzy_matches)

print(f'\n--- NEW MATCHING RESULTS (WITH FUZZY MATCH) ---')
print(f'Perfectly Matched: {perfect_matches}')
print(f'Fuzzy Matched (Corrected Names): {len(fuzzy_matches)}')
print(f'TOTAL OVERALL MATCHES: {total_matches}')

print(f'\nHere are a few examples of the Fuzzy Matches we found:')
for match in fuzzy_matches[:5]:
    print(f'Sheet Name: "{match[0]}"  -->  Folder File: "{match[1]}"')

print(f'\n[STILL MISSING] Shows in Episode Metrics not found anywhere: {len(still_missing)}')
for s in still_missing[:5]:
    print(f'- {s}')
if len(still_missing) > 5: print('...')

print(f'\n[STILL EXTRA] Unused Files/Folders in Final_Upload_Docs: {len(still_extra)}')
for e in still_extra[:5]:
    print(f'- {e}')
if len(still_extra) > 5: print('...')
