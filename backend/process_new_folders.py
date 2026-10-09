import os
import re
import pandas as pd

def clean_title(name):
    if pd.isna(name): return ""
    name = str(name)
    name = re.sub(r'\d+', '', name)
    name = name.replace('-', ' ').replace('_', ' ')
    name = name.lower()
    
    # Remove all known platforms
    platforms = ['joyread', 'goodnovel', 'dreame', 'moboreader', 'moboredaer', 'befant', 'shows', 'free', 'chapters']
    for p in platforms:
        name = name.replace(p, '')
        
    name = re.sub(r'\s+', ' ', name).strip()
    return name

new_folders = [
    'e:/Internship/PocketFM/Goodnovel-shows-free-chapters-20261008T121725Z-1-001',
    'e:/Internship/PocketFM/dreame, joyread, goodnovel, moboredaer, befant #4110 - 4124-20261008T121440Z-1-001'
]

script_names = set()

print("Extracting names from new folders...")
for folder in new_folders:
    if os.path.exists(folder):
        for root, dirs, files in os.walk(folder):
            for file in files:
                name = os.path.splitext(file)[0]
                cleaned = clean_title(name)
                if cleaned:
                    script_names.add(cleaned)

print(f"Found {len(script_names)} unique cleaned scripts.")

print("Loading Vikrant Sheet...")
vikrant_df = pd.read_excel('e:/Internship/PocketFM/Vikrant Sheet.xlsx', sheet_name='LC data - 7.10.26')
vikrant_df['Cleaned Show'] = vikrant_df['Show / Title'].apply(clean_title)

# Grab the metric columns (index 17 to 27)
metric_cols = list(vikrant_df.columns[17:28])

# Subset and drop duplicates to ensure clean mapping
vikrant_subset = vikrant_df[['Cleaned Show'] + metric_cols].dropna(subset=['Cleaned Show'])
vikrant_subset = vikrant_subset.drop_duplicates(subset=['Cleaned Show'])

# Create a dataframe for the new scripts
new_df = pd.DataFrame({'Show / Title': list(script_names)})

print("Merging new data...")
# Match and get CPI data
merged_new = pd.merge(new_df, vikrant_subset, left_on='Show / Title', right_on='Cleaned Show', how='left')
merged_new = merged_new.drop(columns=['Cleaned Show'])

# Drop rows missing CPI data as the user requested
merged_new = merged_new.dropna(subset=['CPI (GenAI)'])
print(f"After dropping missing CPI data, kept {len(merged_new)} scripts from the new batch.")

print("Appending to GenAI_Metrics.xlsx...")
metrics_file = 'e:/Internship/PocketFM/GenAI_Metrics.xlsx'
existing_df = pd.read_excel(metrics_file)

# Append the new ones
final_df = pd.concat([existing_df, merged_new], ignore_index=True)

print("Saving final sheet...")
with pd.ExcelWriter(metrics_file, engine='xlsxwriter') as writer:
    final_df.to_excel(writer, index=False, sheet_name='Metrics')
    workbook = writer.book
    worksheet = writer.sheets['Metrics']
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'center', 'fg_color': '#D7E4BC', 'border': 1})
    
    for col_num, value in enumerate(final_df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        
    worksheet.set_column('A:A', 35) # Show / Title
    worksheet.set_column('B:L', 20) # Metric columns
    if 'Drive Link' in final_df.columns:
        worksheet.set_column('M:M', 60) # Drive link
    worksheet.freeze_panes(1, 0)

print("SUCCESS! Processed new folders and appended to Metrics sheet.")
