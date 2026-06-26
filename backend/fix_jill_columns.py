import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'New_Agency.xlsx')

def run():
    df = pd.read_excel(EXCEL_FILE)
    
    changed = 0
    
    # We want to fill 'Publisher' and 'Name of agent in the main folder'
    # for all the Jill Grinberg rows (where we incorrectly added 'Agency' or where it's known to be Jill)
    
    for idx in range(len(df)):
        author = str(df.at[idx, 'Author Name']).strip()
        
        # In the previous script, we filled 'Agency' == 'Jill Grinberg Literary'
        # So we can use that to identify the rows, or just check the last 426 rows.
        # Let's check if 'Agency' exists and equals 'Jill Grinberg Literary'
        if 'Agency' in df.columns:
            agency_val = str(df.at[idx, 'Agency']).strip()
            if agency_val == 'Jill Grinberg Literary':
                df.at[idx, 'Publisher'] = 'Jill Grinberg Literary'
                df.at[idx, 'Name of agent in the main folder'] = 'Katelyn Detweiler'
                changed += 1
    
    # Drop the mistakenly created extra columns
    if 'Agency' in df.columns:
        df = df.drop(columns=['Agency'])
    if 'Agent' in df.columns:
        df = df.drop(columns=['Agent'])
        
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        apply_styling(EXCEL_FILE)
    except:
        pass
        
    print(f"Fixed {changed} rows: Removed extra columns and correctly updated 'Publisher' and 'Name of agent in the main folder'.")

if __name__ == '__main__':
    run()
