import pandas as pd
import os
import sys

# Append backend directory to path to import styling
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)
from apply_premium_style_crime import apply_premium_fixed_style

def main():
    workspace_dir = os.path.dirname(backend_dir)
    output_file = os.path.join(workspace_dir, 'Blank_11_Column_Template.xlsx')
    
    # The standard 11 columns
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
    
    # Create an empty dataframe with these columns
    df = pd.DataFrame(columns=standard_cols)
    
    # Save the new empty excel file
    print(f"Creating empty template at {output_file}...")
    df.to_excel(output_file, index=False)
    
    # Apply premium styling
    print("Applying premium styling...")
    apply_premium_fixed_style(output_file)
    print("Done!")

if __name__ == "__main__":
    main()
