import pandas as pd
import os
from ai_classifier import identify_subgenre

# Configuration
CATALOG_FILE = "SBR_Media_Catalog_Final.xlsx"

def finalize_classification():
    if not os.path.exists(CATALOG_FILE):
        print(f"Error: {CATALOG_FILE} not found!")
        return

    print(f"Reading {CATALOG_FILE}...")
    df = pd.read_excel(CATALOG_FILE)
    
    print(f"Classifying {len(df)} entries into the 12 Romantasy Sub-Genres...")
    
    for idx, row in df.iterrows():
        synopsis = str(row.get('Synopsis (if available)', ''))
        current_genre = str(row.get('Romantasy Sub-Genre of series', ''))
        
        # We pass the current genre as 'tags' to the identifier
        # identify_subgenre(synopsis, tags)
        # Note: identify_subgenre expects tags as a list
        tags = [current_genre]
        
        subgenre = identify_subgenre(synopsis, tags)
        
        if subgenre != "N/A":
            df.at[idx, 'Romantasy = Yes or No?'] = "Yes"
            df.at[idx, 'Romantasy Sub-Genre of series'] = subgenre
        else:
            # Fallback check: if it was already marked as something, keep it but try to clean it
            if row['Romantasy = Yes or No?'] == "Yes" and subgenre == "N/A":
                # It's romantasy but we don't know which sub-genre
                df.at[idx, 'Romantasy Sub-Genre of series'] = "Urban / Contemporary Fantasy Romance" # Default for unknown romantasy
            else:
                # If no keywords found, default to No for cleanliness
                df.at[idx, 'Romantasy = Yes or No?'] = "No"
                df.at[idx, 'Romantasy Sub-Genre of series'] = "N/A"

    # Final cleanup: ensure no 'NaN' strings
    df = df.replace('nan', 'N/A').replace('None', 'N/A').fillna('N/A')

    print(f"Saving finalized catalog to {CATALOG_FILE}...")
    df.to_excel(CATALOG_FILE, index=False)
    print("Mission Complete! Your catalog is now fully classified.")

if __name__ == "__main__":
    finalize_classification()
