import pandas as pd
import os
import sys

# Append backend directory to path to import styling
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)
from apply_premium_style_crime import apply_premium_fixed_style

def main():
    workspace_dir = os.path.dirname(backend_dir)
    output_file = os.path.join(workspace_dir, 'Selected_Titles_Blank_Template.xlsx')
    
    # The custom columns requested by the user
    custom_cols = [
        'Name of Series',
        'Author Name',
        'Publisher',
        'GoodReads series link',
        'Number of PRIMARY books in the series',
        'Rating (out of 5) of Primary Book 1',
        'Ratings (#) of Primary Book 1',
        'Synopsis (if available)',
        'Name of agent'
    ]
    
    # Create an empty dataframe with these exact columns
    df = pd.DataFrame(columns=custom_cols)
    
    # Save the new empty excel file
    print(f"Creating empty template at {output_file}...")
    df.to_excel(output_file, index=False)
    
    # Apply premium styling
    print("Applying premium styling...")
    apply_premium_fixed_style(output_file)
    print("Done!")

if __name__ == "__main__":
    main()
