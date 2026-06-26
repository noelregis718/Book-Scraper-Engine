import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'New_Agency.xlsx')

def run():
    df = pd.read_excel(EXCEL_FILE)
    print("Columns:", list(df.columns))
    
    # We want to fill Agency and Agent for the newly added Jill Grinberg authors.
    # The new authors might have empty Agency and Agent.
    # We just need to find the rows we just scraped and fill them.
    # If the user says "in all rows now", I should just fill it where it is empty, or for the ones from Jill Grinberg.
    # Wait, earlier I extracted 204 authors. They were appended.
    # Let's fill 'Agency' and 'Agent' for all rows where 'Agency' is empty or NaN, 
    # OR where we know it's Jill Grinberg. Since these were the only recently added ones.
    
    changed = 0
    
    # Check if 'Agency' and 'Agent' columns exist
    if 'Agency' not in df.columns:
        df['Agency'] = ''
    if 'Agent' not in df.columns:
        df['Agent'] = ''
        
    for idx in range(len(df)):
        # If the row has data from our recent scrape (e.g. Author Name is filled)
        # and Agency is empty or contains Jill Grinberg Literary Management
        author = str(df.at[idx, 'Author Name']).strip()
        agency = str(df.at[idx, 'Agency']).strip()
        
        # We know we just appended 204 authors. Let's just update all rows 
        # where Agency is empty, or Agency is 'Jill Grinberg Literary Management'
        if author and author.lower() != 'nan':
            if agency == '' or agency.lower() == 'nan' or 'jill grinberg' in agency.lower():
                df.at[idx, 'Agency'] = 'Jill Grinberg Literary'
                df.at[idx, 'Agent'] = 'Katelyn Detweiler'
                changed += 1
                
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        apply_styling(EXCEL_FILE)
    except:
        pass
        
    print(f"Updated {changed} rows with Agency 'Jill Grinberg Literary' and Agent 'Katelyn Detweiler'.")

if __name__ == '__main__':
    run()
