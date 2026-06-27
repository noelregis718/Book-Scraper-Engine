import pandas as pd
import os
import sys
import glob

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
from apply_jra_style import apply_styling

def run():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tracker_path = os.path.join(base_dir, 'Publishers_Tracker.xlsx')
    
    # Load existing tracker
    print("Loading Publishers_Tracker.xlsx...")
    df_tracker = pd.read_excel(tracker_path)
    existing_publishers = set(df_tracker['Publisher Name'].dropna().astype(str).str.strip())
    
    # Find all Amazon Keyword files
    keyword_files = glob.glob(os.path.join(base_dir, 'Amazon Keyword - *.xlsx'))
    
    new_publishers = set()
    
    print(f"Found {len(keyword_files)} Amazon Keyword files. Extracting publishers...")
    for fpath in keyword_files:
        try:
            df = pd.read_excel(fpath)
            # Find publisher column (could be 'Publisher', 'publisher', etc.)
            pub_col = None
            for col in df.columns:
                if str(col).lower() == 'publisher':
                    pub_col = col
                    break
            
            if pub_col:
                pubs = df[pub_col].dropna().unique()
                for pub in pubs:
                    pub_str = str(pub).strip()
                    if pub_str and pub_str.lower() not in ['nan', 'none']:
                        new_publishers.add(pub_str)
        except Exception as e:
            print(f"Error reading {fpath}: {e}")
            
    # Find publishers that are not in the tracker
    publishers_to_add = new_publishers - existing_publishers
    publishers_to_add = sorted(list(publishers_to_add))
    
    print(f"Found {len(publishers_to_add)} NEW unique publishers across the keyword files.")
    
    if len(publishers_to_add) > 0:
        # Create a dataframe for the new rows
        new_rows = pd.DataFrame({'Publisher Name': publishers_to_add})
        # Make sure it has all the columns of the tracker
        for col in df_tracker.columns:
            if col != 'Publisher Name':
                new_rows[col] = ""
                
        # Append to the bottom
        df_tracker = pd.concat([df_tracker, new_rows], ignore_index=True)
        
        # Save
        print("Saving updated Publishers_Tracker.xlsx...")
        df_tracker.to_excel(tracker_path, index=False)
        
        # Style
        try:
            apply_styling(tracker_path)
            print("Styling applied.")
        except Exception as e:
            print(f"Error styling: {e}")
    else:
        print("No new publishers to add!")

if __name__ == '__main__':
    run()
