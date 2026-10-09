import pandas as pd
import re

def clean_title(name):
    if pd.isna(name): return ""
    name = str(name)
    name = re.sub(r'\d+', '', name)
    name = name.replace('-', ' ').replace('_', ' ')
    name = name.lower()
    name = name.replace('joyread', '').replace('goodnovel', '')
    name = re.sub(r'\s+', ' ', name).strip()
    return name

print("Loading Vikrant Sheet...")
vikrant_df = pd.read_excel('e:/Internship/PocketFM/Vikrant Sheet.xlsx', sheet_name='LC data - 7.10.26')

print("Cleaning Vikrant titles to match...")
vikrant_df['Cleaned Show'] = vikrant_df['Show / Title'].apply(clean_title)

# Grab the metric columns (index 17 to 27)
metric_cols = list(vikrant_df.columns[17:28])

# Subset and drop duplicates to ensure clean mapping
vikrant_subset = vikrant_df[['Cleaned Show'] + metric_cols].dropna(subset=['Cleaned Show'])
vikrant_subset = vikrant_subset.drop_duplicates(subset=['Cleaned Show'])

print("Loading GenAI_Metrics.xlsx...")
metrics_file = 'e:/Internship/PocketFM/GenAI_Metrics.xlsx'
metrics_df = pd.read_excel(metrics_file)

# Keep only the Show / Title column since the rest are empty
metrics_df = metrics_df[['Show / Title']]

print("Merging matching data...")
# Left join on the cleaned names
merged_df = pd.merge(metrics_df, vikrant_subset, left_on='Show / Title', right_on='Cleaned Show', how='left')
merged_df = merged_df.drop(columns=['Cleaned Show'])

# Ensure the column order is perfect
final_cols = ['Show / Title'] + metric_cols
merged_df = merged_df[final_cols]

print("Saving filled metrics sheet...")
with pd.ExcelWriter(metrics_file, engine='xlsxwriter') as writer:
    merged_df.to_excel(writer, index=False, sheet_name='Metrics')
    workbook = writer.book
    worksheet = writer.sheets['Metrics']
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'center', 'fg_color': '#D7E4BC', 'border': 1})
    for col_num, value in enumerate(merged_df.columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('A:A', 35)
    worksheet.set_column('B:L', 20)
    worksheet.freeze_panes(1, 0)

print(f"Successfully filled missing columns in {metrics_file}!")
