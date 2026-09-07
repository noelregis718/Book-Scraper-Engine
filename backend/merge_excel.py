import pandas as pd

def merge_data():
    csv_file = '../RB Media _ Pocket FM List - 2 (Testing Final) _ Internal Copy - Noel.csv'
    excel_file = '../RB Media _ Pocket FM List - 2 (Testing Final) _ Internal Copy.xlsx'
    
    print("Loading CSV...")
    df_csv = pd.read_csv(csv_file)
    
    print("Loading Excel...")
    # Load all sheets to preserve them
    xls_dict = pd.read_excel(excel_file, sheet_name=None)
    
    sheet_name = 'Testing List metrics'
    if sheet_name not in xls_dict:
        print(f"Error: Sheet '{sheet_name}' not found.")
        return
        
    df_target = xls_dict[sheet_name]
    
    cols_to_update = [
        'GR series link',
        'Total page count',
        '*Total No. of Books',
        'GR Book 1 rating',
        'GR Book 1 #ratings'
    ]
    
    update_count = 0
    
    for idx, row in df_csv.iterrows():
        s_no = row.get('S No.')
        if pd.isna(s_no):
            continue
            
        gr_link = str(row.get('GR series link', '')).strip()
        if not gr_link.startswith('http'):
            continue # Skip if not a valid scraped link
            
        target_idx = df_target[df_target['S No.'] == s_no].index
        
        if len(target_idx) > 0:
            t_idx = target_idx[0]
            for col in cols_to_update:
                if col in row and not pd.isna(row[col]):
                    df_target.at[t_idx, col] = row[col]
            update_count += 1
            
    print(f"Updated {update_count} rows in '{sheet_name}'.")
    
    print("Saving back to Excel...")
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        for s_name, df_sheet in xls_dict.items():
            df_sheet.to_excel(writer, sheet_name=s_name, index=False)
            
    print("Done! Data successfully merged.")

if __name__ == '__main__':
    merge_data()
