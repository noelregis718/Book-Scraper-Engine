import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_classifier import identify_subgenre

def classify_romantasy():
    file_path = r'E:\Internship\PocketFM\books_authors.xlsx'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
        
    print(f"Loading {file_path}...")
    df = pd.read_excel(file_path)
    
    count_yes = 0
    count_no = 0
    
    for idx, row in df.iterrows():
        synopsis = str(row.get('Synopsis (if available)', 'N/A'))
        
        # If there's no synopsis, we can't classify it properly
        if synopsis == 'N/A' or synopsis.lower() == 'nan' or not synopsis.strip():
            # If it already has a Yes/No, don't override unless forced, but we'll override to be safe
            df.at[idx, 'Romantasy Sub-Genre of series'] = 'N/A'
            # If it's empty, leave as N/A or No
            df.at[idx, 'Romantasy = Yes or No?'] = 'No'
            continue
            
        sub_genre = identify_subgenre(synopsis, [])
        
        if sub_genre != "N/A":
            df.at[idx, 'Romantasy Sub-Genre of series'] = sub_genre
            df.at[idx, 'Romantasy = Yes or No?'] = 'Yes'
            count_yes += 1
        else:
            # Maybe it is romantasy but not a specific sub-genre? 
            # We will map it to No per the instruction "map it accordingly to the sub-genre"
            df.at[idx, 'Romantasy Sub-Genre of series'] = 'N/A'
            df.at[idx, 'Romantasy = Yes or No?'] = 'No'
            count_no += 1
            
    print(f"Classification complete! Found {count_yes} Romantasy books and {count_no} Non-Romantasy/Unknown.")
    print("Saving Excel file...")
    
    df.to_excel(file_path, index=False)
    
    # Re-apply styling just in case
    try:
        from style_books_authors import apply_styling
        apply_styling(file_path)
    except Exception as e:
        print(f"Could not apply styling automatically: {e}")
        
    print("ALL DONE!")

if __name__ == "__main__":
    classify_romantasy()
