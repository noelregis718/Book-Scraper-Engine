import pandas as pd
import os
import sys

# Append backend directory to path to import styling
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)
from apply_premium_style_crime import apply_premium_fixed_style

def main():
    workspace_dir = os.path.dirname(backend_dir)
    input_file = os.path.join(workspace_dir, '39 Selected titles.xlsx')
    output_file = os.path.join(workspace_dir, '39_Selected_Titles_Standard_Format.xlsx')
    
    # Read the data
    print(f"Reading {input_file}...")
    df = pd.read_excel(input_file)
    
    # The standard 11 columns based on previous work
    standard_cols = [
        'Publisher Name', 
        'Series Name', 
        'Goodreads Series URL', 
        'Author Name', 
        'Book 1 Title', 
        'Book 1 Goodreads Rating', 
        'Number of Book 1 Ratings', 
        'Number of Primary Books', 
        'Number of Pages in Book 1', 
        'Primary Genre(s)', 
        'Verification Source'
    ]
    
    # Filter to just these columns (ignoring any extra ones like 'Tier Mapping', 'No. of Hours')
    print("Filtering to the standard 11 columns...")
    df_new = df[standard_cols]
    
    # Save the new excel file
    print(f"Saving to {output_file}...")
    df_new.to_excel(output_file, index=False)
    
    # Apply premium styling
    print("Applying premium styling...")
    apply_premium_fixed_style(output_file)
    print("Done!")

if __name__ == "__main__":
    main()
