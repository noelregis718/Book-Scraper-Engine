import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Next_Agency.xlsx')

def run():
    columns = [
        'Name of Series', 
        'Author Name', 
        'Publisher', 
        'GoodReads series link', 
        'Number of PRIMARY books in the series', 
        'Rating (out of 5) of Primary Book 1', 
        'Ratings (#) of Primary Book 1', 
        'Synopsis (if available)', 
        'Romantasy = Yes or No?', 
        'Romantasy Sub-Genre of series', 
        'Name of agent in the main folder'
    ]
    
    df = pd.DataFrame(columns=columns)
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        apply_styling(EXCEL_FILE)
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    print(f"Successfully created a blank Excel sheet with standard 11 columns at: {EXCEL_FILE}")

if __name__ == '__main__':
    run()
