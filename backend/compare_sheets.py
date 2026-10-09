import pandas as pd
import openpyxl

def clean_name(name):
    if pd.isna(name): return ""
    return str(name).lower().strip()

def get_real_links(file_path, sheet_name, title_col, link_cols):
    print(f"Extracting real hyperlinks from {file_path}...")
    # First, get column indices using pandas
    df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=0)
    col_map = {col: idx for idx, col in enumerate(df.columns)}
    
    title_idx = col_map.get(title_col)
    link_indices = {col: col_map.get(col) for col in link_cols if col_map.get(col) is not None}
    
    # Now load with openpyxl to get hyperlinks
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb[sheet_name] if sheet_name else wb.active
    
    extracted_data = []
    
    # Iterate through rows (skip header)
    for row in ws.iter_rows(min_row=2):
        title_cell = row[title_idx] if title_idx is not None else None
        title = title_cell.value if title_cell else None
        
        if not title: continue
        
        row_data = {title_col: title}
        
        for col_name, idx in link_indices.items():
            cell = row[idx]
            # If the cell has an embedded hyperlink, grab it! Otherwise fallback to text value
            if cell.hyperlink and cell.hyperlink.target:
                row_data[col_name] = cell.hyperlink.target
            else:
                row_data[col_name] = str(cell.value).strip() if cell.value else ""
                
        extracted_data.append(row_data)
        
    return pd.DataFrame(extracted_data)

# Extract real links from Vikrant sheet
vikrant_links = ['Source link', 'Crawled Script']
vikrant_df = get_real_links('e:/Internship/PocketFM/Vikrant Sheet.xlsx', 'LC data - 7.10.26', 'Show / Title', vikrant_links)

# Extract real links from Crawling sheet
crawling_links = ['Original URL', 'Alternate Links', 'Output Drive link']
crawling_df = get_real_links('e:/Internship/PocketFM/Copy of crawling sheet.xlsx', 0, 'Title Name', crawling_links)

# Create normalized names
crawling_df['Normalized Name'] = crawling_df['Title Name'].apply(clean_name)
vikrant_df['Normalized Name'] = vikrant_df['Show / Title'].apply(clean_name)

# Find common names
common_names = set(crawling_df['Normalized Name']).intersection(set(vikrant_df['Normalized Name']))
common_names.discard("")

print(f"Found {len(common_names)} common series names!")

# Subset and drop duplicates
vikrant_subset = vikrant_df[vikrant_df['Normalized Name'].isin(common_names)][['Normalized Name', 'Show / Title'] + vikrant_links].drop_duplicates(subset=['Normalized Name'])
crawling_subset = crawling_df[crawling_df['Normalized Name'].isin(common_names)][['Normalized Name'] + crawling_links].drop_duplicates(subset=['Normalized Name'])

# Merge
matched_shows = pd.merge(vikrant_subset, crawling_subset, on='Normalized Name', how='inner')
matched_shows = matched_shows.drop(columns=['Normalized Name'])

# Save
output_file = 'e:/Internship/PocketFM/Matched_Series.xlsx'
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    matched_shows.to_excel(writer, index=False, sheet_name='Matched Data')
    workbook = writer.book
    worksheet = writer.sheets['Matched Data']
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'center', 'fg_color': '#D7E4BC', 'border': 1})
    for col_num, value in enumerate(matched_shows.columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('A:A', 35)
    worksheet.set_column('B:F', 50)
    worksheet.freeze_panes(1, 0)

print(f"Saved matched series with TRUE embedded hyperlinks to {output_file}")
