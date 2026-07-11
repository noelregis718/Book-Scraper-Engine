import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

def merge_sheets():
    print("Starting merge of the two attached Excel sheets...")
    
    file1 = 'e:/Internship/PocketFM/Books_and_Authors_Updated.xlsx'
    file2 = 'e:/Internship/PocketFM/Books_From_Screenshots_Updated.xlsx'
    target = 'e:/Internship/PocketFM/Next_Agency.xlsx'
    
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)
    
    # Standard 11 columns
    cols = [
        'Name of Series', 'Author Name', 'Publisher', 'GoodReads series link',
        'Number of PRIMARY books in the series', 'Rating (out of 5) of Primary Book 1',
        'Ratings (#) of Primary Book 1', 'Synopsis (if available)',
        'Romantasy = Yes or No?', 'Romantasy Sub-Genre of series',
        'Name of agent in the main folder'
    ]
    
    # Map File 1
    new_df1 = pd.DataFrame(columns=cols)
    new_df1['Name of Series'] = df1['Book Name']
    new_df1['Author Name'] = df1['Author Name']
    
    # Map File 2
    new_df2 = pd.DataFrame(columns=cols)
    new_df2['Name of Series'] = df2['Title']
    new_df2['Author Name'] = df2['Author']
    
    # Combine without deleting anything
    final_df = pd.concat([new_df1, new_df2], ignore_index=True)
    
    # Fill NaN with blanks
    final_df = final_df.fillna('')
    
    print(f"Merged successfully. Total rows: {len(final_df)}")
    
    # Save and style
    final_df.to_excel(target, index=False)
    apply_styling(target)
    print("Saved to Next_Agency.xlsx and styled perfectly.")

if __name__ == '__main__':
    merge_sheets()
