import pandas as pd
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
from apply_jra_style import apply_styling

def run():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    exclusion_path = os.path.join(base_dir, 'Licensing Outreach Exclusion List.xlsx')
    tracker_path = os.path.join(base_dir, 'Publishers_Tracker_updated.xlsx')
    
    print("Loading Sheet25 from Exclusion List...")
    df_excl = pd.read_excel(exclusion_path, sheet_name='Sheet25')
    
    # Assuming publishers are in 'Unnamed: 1' based on inspection
    col = 'Unnamed: 1'
    if col not in df_excl.columns:
        print(f"Error: {col} not found in Sheet25.")
        return
        
    # Extract unique publishers, drop NA
    new_pubs = df_excl[col].dropna().astype(str).str.strip().unique()
    new_pubs = [p for p in new_pubs if p.lower() not in ['nan', 'none', 'self published']]
    
    print("Loading Publishers_Tracker...")
    df_tracker = pd.read_excel(tracker_path)
    to_append = new_pubs
            
    print(f"{len(to_append)} publishers will be appended as requested.")
    
    if len(to_append) > 0:
        # Create a dataframe for the new rows
        new_rows = []
        for p in to_append:
            row = {col: '' for col in df_tracker.columns}
            row['Publisher Name'] = p
            new_rows.append(row)
            
        df_new = pd.DataFrame(new_rows)
        
        # Append to the bottom
        df_final = pd.concat([df_tracker, df_new], ignore_index=True)
        
        print("Saving updated tracker...")
        df_final.to_excel(tracker_path, index=False)
        
        try:
            apply_styling(tracker_path)
            print("Styling applied.")
        except Exception as e:
            print("Error applying style:", e)
            
        print(f"Successfully appended {len(to_append)} new publishers after row {len(df_tracker)}!")
    else:
        print("No new publishers to append (they were all already in the tracker).")

if __name__ == '__main__':
    run()
