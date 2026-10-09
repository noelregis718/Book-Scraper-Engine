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

potential_titles = set()
for col in df.columns:
    for val in df[col].dropna():
        if isinstance(val, str):
            # Split by comma just in case some cells have multiple values
            for part in val.split(','):
                cleaned = clean_title(part.strip())
                if cleaned and "http" not in cleaned and len(cleaned) > 2:
                    potential_titles.add(cleaned)

print(f"Extracted {len(potential_titles)} unique cleaned text values from Matched_Series.")

print("Loading GenAI_Metrics.xlsx to filter out already added shows...")
metrics_file = 'e:/Internship/PocketFM/GenAI_Metrics.xlsx'
metrics_df = pd.read_excel(metrics_file)
existing_names = set(metrics_df['Show / Title'].dropna().tolist())

new_titles = potential_titles - existing_names
print(f"Out of those, {len(new_titles)} are entirely NEW and not in the Metrics sheet.")

print("Loading Vikrant Sheet to check for CPI data...")
vikrant_df = pd.read_excel('e:/Internship/PocketFM/Vikrant Sheet.xlsx', sheet_name='LC data - 7.10.26')
vikrant_df['Cleaned Show'] = vikrant_df['Show / Title'].apply(clean_title)

# Only keep rows with CPI
vikrant_cpi = vikrant_df.dropna(subset=['CPI (GenAI)'])
cpi_titles = set(vikrant_cpi['Cleaned Show'].tolist())

# Find intersection
valid_actionable = new_titles.intersection(cpi_titles)

print("\n" + "="*70)
print(f"Found {len(valid_actionable)} highly actionable shows from Matched_Series!")
print("(They are NEW to our tracker AND have valid CPI data in Vikrant)")
print("="*70)

for c_name in sorted(valid_actionable):
    print(f"- {c_name}")
