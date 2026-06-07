import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def append_middle_grade():
    mg_file = r'E:\Internship\PocketFM\deborah_harris_middle_grade_books_authors.xlsx'
    out_file = r'E:\Internship\PocketFM\deborah_harris_merged.xlsx'
    
    if not os.path.exists(mg_file):
        print(f"File not found: {mg_file}")
        return

    print("Loading excel files...")
    mg_df = pd.read_excel(mg_file)
    main_df = pd.read_excel(out_file)

    # Standardize column names
    if 'Book Name' in mg_df.columns:
        mg_df = mg_df.rename(columns={'Book Name': 'Name of Series'})

    # Keep only Name of Series and Author Name
    cols_to_keep = ['Name of Series', 'Author Name']
    mg_df = mg_df[[c for c in cols_to_keep if c in mg_df.columns]]

    # Fill in the rest of the 11 columns with blanks
    for col in main_df.columns:
        if col not in mg_df.columns:
            mg_df[col] = ""
            
    # Match column order
    mg_df = mg_df[main_df.columns]

    print(f"Appending {len(mg_df)} new middle grade books...")
    main_df = pd.concat([main_df, mg_df], ignore_index=True)
    
    # Drop exact duplicates just in case
    main_df = main_df.drop_duplicates(subset=['Name of Series', 'Author Name'])

    main_df.to_excel(out_file, index=False)
    print(f"Merged successfully!")

    try:
        from style_books_authors import apply_styling
        apply_styling(out_file)
    except Exception as e:
        print(f"Failed to style: {e}")

if __name__ == "__main__":
    append_middle_grade()
