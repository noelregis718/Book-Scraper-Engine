import pandas as pd

def main():
    file_path = 'e:/Internship/PocketFM/Podium CT Wishlist (Tier 1).xlsx'
    
    print("Loading Sheet3...")
    df_sheet3 = pd.read_excel(file_path, sheet_name='Sheet3', engine='openpyxl')
    
    print("Loading Base List for page counts...")
    df_base = pd.read_excel(file_path, sheet_name='Shortlisted for Tier 1 Selectio', engine='openpyxl')
    
    # Create a lookup dictionary mapping Series Name to Number of Pages in Book 1
    # We strip and lowercase strings to ensure matches aren't missed due to case/spaces
    df_base_unique = df_base.dropna(subset=['Series Name']).drop_duplicates(subset=['Series Name'])
    page_lookup = dict(zip(
        df_base_unique['Series Name'].astype(str).str.strip().str.lower(), 
        df_base_unique['Number of Pages in Book 1']
    ))
    
    # Function to get page count from lookup
    def get_pages(series_name):
        if pd.isna(series_name):
            return 0
        return page_lookup.get(str(series_name).strip().lower(), 0)
        
    print("Applying formula...")
    # Map the pages to Sheet3
    df_sheet3['Mapped Pages in Book 1'] = df_sheet3['Series Name'].apply(get_pages)
    
    # Convert to numeric to ensure math works safely
    df_sheet3['Mapped Pages in Book 1'] = pd.to_numeric(df_sheet3['Mapped Pages in Book 1'], errors='coerce').fillna(0)
    df_sheet3['No. of Primary Books Numeric'] = pd.to_numeric(df_sheet3['No. of Primary Books'], errors='coerce').fillna(0)
    
    # Apply Boss's Formula: (Pages * Books * 250) / 10000
    df_sheet3['Calculated Hours (Formula)'] = (df_sheet3['Mapped Pages in Book 1'] * df_sheet3['No. of Primary Books Numeric'] * 250) / 10000
    
    # Fill any completely missing 'No. of Hours' with our calculated formula hours!
    df_sheet3['No. of Hours'] = pd.to_numeric(df_sheet3['No. of Hours'], errors='coerce')
    df_sheet3['No. of Hours'] = df_sheet3['No. of Hours'].fillna(df_sheet3['Calculated Hours (Formula)'])
    
    # Clean up temporary column used for math
    df_sheet3 = df_sheet3.drop(columns=['No. of Primary Books Numeric'])
    
    out_path = 'e:/Internship/PocketFM/Sheet3_With_Calculated_Hours.xlsx'
    df_sheet3.to_excel(out_path, index=False)
    
    print(f"Successfully grabbed page counts, applied the formula, and saved to {out_path}")

if __name__ == '__main__':
    main()
