import pandas as pd
import difflib
import re

target_file = 'e:/Internship/PocketFM/Episode Metrics - Noel New.xlsx'
vikrant_file = 'e:/Internship/PocketFM/Vikrant Sheet.xlsx'

df_target = pd.read_excel(target_file, sheet_name='Metrics (1)')
df_vikrant = pd.read_excel(vikrant_file)

vikrant_title_col = [col for col in df_vikrant.columns if 'show' in str(col).lower() or 'title' in str(col).lower() or 'name' in str(col).lower()][0]

valid_vikrant_rows = df_vikrant.dropna(subset=[vikrant_title_col])
valid_vikrant_titles = valid_vikrant_rows[vikrant_title_col].astype(str).tolist()

def clean_for_diff(name):
    name = str(name).replace('.docx', '').replace('.doc', '').replace('.pdf', '')
    name = re.sub(r'[\W_]+', '', name.lower())
    name = re.sub(r'\d+', '', name)
    for p in ['joyread', 'goodnovel', 'dreame', 'moboreader', 'moboredaer', 'befant', 'shows', 'free', 'chapters', 'chapter', 'v', 'p']:
        name = name.replace(p, '')
    return name

clean_to_orig_vikrant = {}
for t in valid_vikrant_titles:
    clean_to_orig_vikrant[clean_for_diff(t)] = t

rescued = 0

for idx, row in df_target.iterrows():
    if pd.isna(row.get('CPI (GenAI)')) or str(row.get('CPI (GenAI)')).strip() == '':
        t_title = clean_for_diff(row['Show / Title'])
        
        matches = difflib.get_close_matches(t_title, clean_to_orig_vikrant.keys(), n=1, cutoff=0.4)
        
        if matches:
            best_clean_match = matches[0]
            best_orig_match = clean_to_orig_vikrant[best_clean_match]
            
            matched_row = valid_vikrant_rows[valid_vikrant_rows[vikrant_title_col] == best_orig_match].iloc[0]
            
            # Extract data even if it's NaNs, we'll just force whatever is there
            cpi = matched_row.get('CPI (GenAI)')
            if not pd.isna(cpi) and str(cpi).strip() != '':
                for col in ['CPI (GenAI)', 'CTR x CTI (Gen AI)', '95% plays/3-sec plays (GenAI)', 'Thruplays/3sec plays']:
                    if col in matched_row:
                        df_target.at[idx, col] = matched_row[col]
                rescued += 1
                t_val = str(row['Show / Title'])[:25]
                m_val = str(best_orig_match)[:25]
                print(f'MAPPED: {t_val} -> {m_val} | CPI: {cpi}')
            else:
                t_val = str(row['Show / Title'])[:25]
                m_val = str(best_orig_match)[:25]
                print(f'MAPPED (BUT NO CPI IN VIKRANT): {t_val} -> {m_val}')
        else:
            t_val = str(row['Show / Title'])[:25]
            print(f'NO MATCH AT ALL IN VIKRANT: {t_val}')

with pd.ExcelWriter(target_file, engine='xlsxwriter') as writer:
    df_target.to_excel(writer, index=False, sheet_name='Metrics (1)')
    workbook = writer.book
    worksheet = writer.sheets['Metrics (1)']
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'center', 'fg_color': '#D7E4BC', 'border': 1})
    for col_num, value in enumerate(df_target.columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('A:Z', 20)
    worksheet.freeze_panes(1, 0)

print(f'\nTotal successfully rescued with CPI: {rescued}')
