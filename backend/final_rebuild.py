import pandas as pd

def main():
    master_path = 'e:/Internship/PocketFM/PocketFM_CT_Analysis_Master.xlsx'
    
    print("Loading the preserved Missing CT Titles...")
    df_missing = pd.read_excel(master_path, sheet_name='Missing CT Titles', engine='openpyxl')
    
    raw_path = 'e:/Internship/PocketFM/Sheet3_With_Calculated_Hours.xlsx'
    print("Loading the raw calculated dataset...")
    df_raw = pd.read_excel(raw_path, engine='openpyxl')
    
    def is_romantasy(genre):
        if pd.isna(genre): return False
        g = str(genre).lower()
        return 'romance' in g or 'fantasy' in g
        
    mask_romantasy = df_raw['Genre'].apply(is_romantasy)
    
    books_numeric = pd.to_numeric(df_raw['No. of Primary Books'], errors='coerce').fillna(0)
    mask_books = books_numeric <= 4
    
    hours_numeric = pd.to_numeric(df_raw['No. of Hours'], errors='coerce').fillna(0)
    mask_hours = hours_numeric <= 40
    
    # Combined mask for everything that gets cut from the Vetted list
    mask_removed = mask_romantasy | mask_books | mask_hours
    
    def get_reason(row):
        reasons = []
        if is_romantasy(row['Genre']):
            reasons.append("Romantasy Overlap")
        
        books = pd.to_numeric(row['No. of Primary Books'], errors='coerce')
        if pd.isna(books) or books <= 4:
            reasons.append("Books <= 4")
            
        hours = pd.to_numeric(row['No. of Hours'], errors='coerce')
        if pd.isna(hours) or hours <= 40:
            reasons.append("Hours <= 40")
            
        return " | ".join(reasons)
        
    df_raw['Reason for Removal'] = df_raw.apply(get_reason, axis=1)
    
    # 1. The Vetted list stays the same (everything failing ANY rule is removed)
    df_kept = df_raw[~mask_removed].drop(columns=['Reason for Removal'])
    
    # 2. Tab 3 should ONLY contain Romantasy rejects now
    df_romantasy_rejects = df_raw[mask_romantasy]
    
    # Rebuild the master workbook
    print("Rebuilding the master workbook...")
    with pd.ExcelWriter(master_path, engine='openpyxl') as writer:
        df_missing.to_excel(writer, sheet_name='Missing CT Titles', index=False)
        df_kept.to_excel(writer, sheet_name='Final Vetted CT Shortlist', index=False)
        df_romantasy_rejects.to_excel(writer, sheet_name='Removed Romantasy', index=False)
        
    print(f"Success! Vetted List Size: {len(df_kept)}, Romantasy Rejects Size: {len(df_romantasy_rejects)}")

if __name__ == '__main__':
    main()
