import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_classifier import identify_subgenre

EXCEL_FILE = r"E:\Internship\PocketFM\corvisiero_merged.xlsx"

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
            
    romantasy_col = "Romantasy = Yes or No?"
    subgenre_col = "Romantasy Sub-Genre of series"
    
    yes_count = 0
    
    for idx, row in df.iterrows():
        title = str(row.get('Name of Series', '')).strip()
        synopsis = str(row.get('Synopsis (if available)', '')).strip()
        
        if title.lower() == 'nan' or not title:
            continue
            
        current_yes_no = str(row.get(romantasy_col, '')).strip()
        current_sub = str(row.get(subgenre_col, '')).strip()
        
        # We pass synopsis and tags (which can just be the title and any existing genre notes)
        tags_list = [title]
        if current_sub and current_sub != 'nan':
            tags_list.append(current_sub)
            
        # Classify using the AI-Enhanced script logic
        subgenre_result = identify_subgenre(synopsis, tags_list)
        
        # Decide Yes/No
        if current_yes_no.lower() == 'yes' or subgenre_result != "N/A":
            df.at[idx, romantasy_col] = "Yes"
            df.at[idx, subgenre_col] = subgenre_result if subgenre_result != "N/A" else "High Fantasy Court Adventure"
            yes_count += 1
        else:
            df.at[idx, romantasy_col] = "No"
            df.at[idx, subgenre_col] = ""

    print(f"Saving {EXCEL_FILE} with {yes_count} AI-Enhanced Romantasy matches...")
    df.to_excel(EXCEL_FILE, index=False)
    
    print("ALL DONE!")

if __name__ == '__main__':
    main()
