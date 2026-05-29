import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from classify_perez import KEYWORD_MAP, classify_subgenre

EXCEL_FILE = r"E:\Internship\PocketFM\MarsalLyon_Merged_Formatted.xlsx"

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
        
        # Combine all text to classify subgenre
        combined_text = synopsis + " " + title
        
        # Classify
        subgenre_result = classify_subgenre(combined_text)
        
        # Decide Yes/No based purely on if a subgenre was found
        # (This forces proper re-evaluation of ALL rows based on the requested list)
        if subgenre_result is not None:
            df.at[idx, romantasy_col] = "Yes"
            df.at[idx, subgenre_col] = subgenre_result
            yes_count += 1
        else:
            # Check if there is already a 'Yes' from goodreads genres list containing 'romantasy'
            if current_yes_no == 'Yes':
                df.at[idx, romantasy_col] = "Yes"
                df.at[idx, subgenre_col] = "High Fantasy Court Adventure" # Default fallback
                yes_count += 1
            else:
                df.at[idx, romantasy_col] = "No"
                df.at[idx, subgenre_col] = ""

    print(f"Saving {EXCEL_FILE} with {yes_count} Romantasy matches...")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    print("ALL DONE!")

if __name__ == '__main__':
    main()
