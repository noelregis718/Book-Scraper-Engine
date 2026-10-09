import pandas as pd
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

print("Scanning Matched_Series.xlsx for potential titles...")
df = pd.read_excel('e:/Internship/PocketFM/Matched_Series.xlsx')

potential_titles = {}
for col in df.columns:
    for val in df[col].dropna():
        if isinstance(val, str):
            for part in val.split(','):
                cleaned = clean_title(part.strip())
                if cleaned and "http" not in cleaned and len(cleaned) > 2:
                    # We store the raw value as the 'location' or 'folder' reference
                    potential_titles[cleaned] = val.strip()

print(f"Extracted {len(potential_titles)} unique cleaned text values from Matched_Series.")

print("Loading GenAI_Metrics.xlsx to filter out already added shows...")
metrics_file = 'e:/Internship/PocketFM/GenAI_Metrics.xlsx'
metrics_df = pd.read_excel(metrics_file)
existing_names = set(metrics_df['Show / Title'].dropna().tolist())

new_titles = {k: v for k, v in potential_titles.items() if k not in existing_names}
print(f"Out of those, {len(new_titles)} are entirely NEW and not in the Metrics sheet.")

print("Loading Vikrant Sheet to check for CPI data...")
vikrant_df = pd.read_excel('e:/Internship/PocketFM/Vikrant Sheet.xlsx', sheet_name='LC data - 7.10.26')
vikrant_df['Cleaned Show'] = vikrant_df['Show / Title'].apply(clean_title)

# Only keep rows with CPI
metric_cols = list(vikrant_df.columns[17:28])
vikrant_cpi = vikrant_df[['Cleaned Show'] + metric_cols].dropna(subset=['CPI (GenAI)']).drop_duplicates(subset=['Cleaned Show'])

cpi_titles = set(vikrant_cpi['Cleaned Show'].tolist())

# Find intersection
valid_actionable = {k: v for k, v in new_titles.items() if k in cpi_titles}

print(f"\nFound {len(valid_actionable)} highly actionable shows from Matched_Series!")
print("Appending them to GenAI_Metrics.xlsx...")

if len(valid_actionable) > 0:
    new_df = pd.DataFrame({'Show / Title': list(valid_actionable.keys())})
    merged_new = pd.merge(new_df, vikrant_cpi, left_on='Show / Title', right_on='Cleaned Show', how='inner')
    merged_new = merged_new.drop(columns=['Cleaned Show'])
    
    # Map the folder names into the Drive Link column
    merged_new['Drive Link'] = merged_new['Show / Title'].map(valid_actionable)
    
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

    print("SUCCESS! All valid missing shows from Matched_Series have been successfully appended to the Metrics sheet!")
else:
    print("No valid shows to append.")
