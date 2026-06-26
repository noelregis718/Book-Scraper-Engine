import pandas as pd
from bs4 import BeautifulSoup
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'New_Agency.xlsx')

def run():
    print(f"Reading HTML...")
    with open('jill_rendered.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    authors = set()
    for h4 in soup.find_all('h4'):
        text = h4.text.strip()
        if text and len(text.split()) >= 2:
            authors.add(text)
            
    sorted_authors = sorted(list(authors))
    print(f"Extracted {len(sorted_authors)} authors from the website.")
    
    df = pd.read_excel(EXCEL_FILE)
    
    new_rows = []
    for author in sorted_authors:
        # Create an empty row with the same columns
        row = {col: '' for col in df.columns}
        row['Author Name'] = author
        # Optional: if Agency exists, fill it in
        if 'Agency' in df.columns:
            row['Agency'] = 'Jill Grinberg Literary Management'
        new_rows.append(row)
        
    new_df = pd.DataFrame(new_rows)
    df = pd.concat([df, new_df], ignore_index=True)
    
    df.to_excel(EXCEL_FILE, index=False)
    try:
        apply_styling(EXCEL_FILE)
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    print(f"Successfully appended {len(sorted_authors)} authors to {EXCEL_FILE}.")

if __name__ == '__main__':
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)
    run()
