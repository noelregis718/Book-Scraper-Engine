import pandas as pd

source_file = 'Narrative Podcasts Shortlists.xlsx'
target_file = 'Narrative_Podcasts_Blank.xlsx'

# The actual headers are on the second row (index 1) for both sheets
tc_df = pd.read_excel(source_file, sheet_name='True Crime', header=1)
hm_df = pd.read_excel(source_file, sheet_name='Horror & Mystery Audio Drama', header=1)

tc_df.dropna(how='all', inplace=True)
hm_df.dropna(how='all', inplace=True)

# Correctly rename Horror columns to match True Crime template so they align perfectly
rename_map = {
    'Type / Premise': 'Premise',
    'Amber shortlists': "Amber's notes",
    'Status': 'Outreach status'
}
hm_df = hm_df.rename(columns=rename_map)

def filter_contact_forms(df):
    if 'Contact point' in df.columns:
        mask = df['Contact point'].astype(str).str.lower().str.contains('contact form', na=False)
        return df[mask]
    return pd.DataFrame()

tc_filtered = filter_contact_forms(tc_df)
hm_filtered = filter_contact_forms(hm_df)

# Combine both filtered dataframes
combined_filtered = pd.concat([tc_filtered, hm_filtered], ignore_index=True)

# Keep only the columns present in the True Crime template
template_columns = [
    "Title", "Premise", "Validation: Listens / Charts / Awards", 
    "Current Audio Rights Holder", "Episode Count", "Format Type", 
    "Sub-genre", "Length (hrs)", "Series / Anthology", "Show structure", 
    "Licensing Confidence", "Final Priority", "Shicong's Notes", 
    "Rights required", "Amber's notes", "Rightsholder contact", 
    "Contact point", "Email (creator)", "Outreach status"
]
combined_filtered = combined_filtered.reindex(columns=template_columns)

# Save back to target file
combined_filtered.to_excel(target_file, index=False)

print(f"Successfully fixed columns and extracted {len(combined_filtered)} rows.")
