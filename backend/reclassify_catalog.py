import pandas as pd
import os
from ai_classifier import identify_subgenre

MASTER_FILE = "Deep_Catalog_Enrichment.xlsx"

def reclassify():
    if not os.path.exists(MASTER_FILE):
        print(f"Error: {MASTER_FILE} not found.")
        return

    print(f"Loading {MASTER_FILE}...")
    df = pd.read_excel(MASTER_FILE)

    print("Re-classifying Romantasy sub-genres...")
    
    total_rows = len(df)
    for idx, row in df.iterrows():
        synopsis = str(row.get('Synopsis (if available)', ''))
        genre = str(row.get('Genre', '')) # We'll check the Genre column if it exists or just use empty list
        # In our master file, we might have a Genre column from the scraper
        
        # Call classifier
        subgenre = identify_subgenre(synopsis, [genre])
        
        if subgenre != "N/A":
            if "Melissa Foster" in str(row.get('Author Name', '')):
                print(f"    [Match] {row.get('Name of Series')} matched {subgenre}", flush=True)
            df.at[idx, 'Romantasy = Yes or No?'] = "Yes"
            df.at[idx, 'Romantasy Sub-Genre of series'] = subgenre
        else:
            df.at[idx, 'Romantasy = Yes or No?'] = "No"
            df.at[idx, 'Romantasy Sub-Genre of series'] = "N/A"
            
        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{total_rows} rows...")

    print(f"Saving changes to {MASTER_FILE}...")
    df.to_excel(MASTER_FILE, index=False)
    print("Done! Re-classification complete.")

if __name__ == "__main__":
    reclassify()
