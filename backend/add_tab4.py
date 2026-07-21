import pandas as pd
import warnings

# Suppress openpyxl warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

def main():
    cat_path = 'e:/Internship/PocketFM/Podium Entertainment Complete Catalogue.xlsx'
    master_path = 'e:/Internship/PocketFM/PocketFM_CT_Analysis_Master.xlsx'
    
    print("Loading Complete Catalogue...")
    df_cat = pd.read_excel(cat_path, engine='openpyxl')
    
    # Check for anything containing Romance OR Fantasy
    # (Since we defined Romantasy this way in our previous filters)
    def is_romantasy(genre):
        if pd.isna(genre): return False
        g = str(genre).lower()
        return ('romance' in g and 'fantasy' in g) or 'romantasy' in g
        
    df_romantasy = df_cat[df_cat['Genre'].apply(is_romantasy)]
    count = len(df_romantasy)
    print(f"Found {count} Romance/Fantasy series in the Catalogue.")
    
    print("Adding Tab 4 ('Catalogue Romantasy') to the master workbook...")
    
    # Append the new sheet to the existing workbook
    with pd.ExcelWriter(master_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_romantasy.to_excel(writer, sheet_name='Catalogue Romantasy', index=False)
        
    print("Successfully added Tab 4!")

if __name__ == '__main__':
    main()
