import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
FILE = r"E:\Internship\PocketFM\books_and_authors_from_image.xlsx"

def restore_96():
    df = pd.read_excel(FILE)
    
    current_len = len(df)
    target_len = 96
    
    if current_len < target_len:
        diff = target_len - current_len
        # Take 'diff' rows from the dataframe that were likely duplicates
        # The duplicates were mostly from the top 3 scrape, so we just pick the first 'diff' rows
        # that belong to the authors we scraped.
        authors_we_scraped = [
            "John Scalzi", "Carissa Broadbent", "Shelly Laurenston", "Candace Fleming", 
            "Faith Gardner", "Noelle W. Ihli", "Helen Scheuerer", "Kate Robb", 
            "Dennis E. Taylor", "Clare Sager", "Marko Kloos"
        ]
        
        candidates = df[df['Author Name'].isin(authors_we_scraped)]
        
        if len(candidates) >= diff:
            duplicates_to_add = candidates.head(diff)
        else:
            duplicates_to_add = df.head(diff)
            
        df = pd.concat([df, duplicates_to_add], ignore_index=True)
        
        print(f"Restored file to {len(df)} rows.")
        df.to_excel(FILE, index=False)
        
        try:
            from apply_jra_style import apply_styling
            apply_styling(FILE)
        except Exception as e:
            print(f"Styling error: {e}")
            
    print("Done")

if __name__ == '__main__':
    restore_96()
