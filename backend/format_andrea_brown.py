import pandas as pd
import os
import sys

def apply_11_column_format(input_file, output_file):
    print(f"Reading {input_file}...")
    df = pd.read_excel(input_file)
    
    # Standard 11 columns
    columns = [
        "Name of Series",
        "Author Name",
        "Publisher",
        "GoodReads series link",
        "Number of PRIMARY books in the series",
        "Rating (out of 5) of Primary Book 1",
        "Ratings (#) of Primary Book 1",
        "Synopsis (if available)",
        "Romantasy = Yes or No?",
        "Romantasy Sub-Genre of series",
        "Name of agent"
    ]
    
    # Create a new DataFrame with the 11 columns
    new_df = pd.DataFrame(columns=columns)
    
    # Map the existing data
    if 'Title' in df.columns:
        new_df['Name of Series'] = df['Title']
        
    if 'Subtitle / Series' in df.columns:
        # Append subtitle to Name of Series if it exists
        mask = df['Subtitle / Series'].notna() & (df['Subtitle / Series'] != '')
        new_df.loc[mask, 'Name of Series'] = new_df.loc[mask, 'Name of Series'].astype(str) + " - " + df.loc[mask, 'Subtitle / Series'].astype(str)
        
    if 'Author' in df.columns:
        new_df['Author Name'] = df['Author']
        
    if 'Notes' in df.columns:
        new_df['Synopsis (if available)'] = df['Notes']

    print(f"Saving formatted data to {output_file}...")
    new_df.to_excel(output_file, index=False)
    
    # Apply styling if apply_jra_style.py is available
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from apply_jra_style import apply_styling
        apply_styling(output_file)
        print("Styling applied successfully.")
    except Exception as e:
        print(f"Could not apply styling: {e}")

if __name__ == '__main__':
    input_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "final_master_books_list_complete.xlsx")
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "andrea_brown_books_formatted.xlsx")
    apply_11_column_format(input_path, output_path)
    print("Done!")
