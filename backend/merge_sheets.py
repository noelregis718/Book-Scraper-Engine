import pandas as pd

def main():
    # The three individual files we generated
    file1 = 'e:/Internship/PocketFM/Missing_CT_From_Base_List.xlsx'
    file2 = 'e:/Internship/PocketFM/Sheet3_With_Calculated_Hours.xlsx'
    file3 = 'e:/Internship/PocketFM/Final_CT_Wishlist_Filtered.xlsx'
    
    out_path = 'e:/Internship/PocketFM/PocketFM_CT_Analysis_Master.xlsx'
    
    print("Loading all three sheets into memory...")
    try:
        df1 = pd.read_excel(file1, engine='openpyxl')
        df2 = pd.read_excel(file2, engine='openpyxl')
        df3 = pd.read_excel(file3, engine='openpyxl')
    except Exception as e:
        print(f"Error loading files: {e}")
        return
        
    print(f"Writing master workbook to {out_path}...")
    with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
        # Saving each dataframe to its own labeled tab
        df1.to_excel(writer, sheet_name='Missing CT Titles', index=False)
        df2.to_excel(writer, sheet_name='Sheet3 (Calculated Hours)', index=False)
        df3.to_excel(writer, sheet_name='Final Vetted CT Shortlist', index=False)
        
    print("Success! The files have been merged into a single workbook.")

if __name__ == '__main__':
    main()
