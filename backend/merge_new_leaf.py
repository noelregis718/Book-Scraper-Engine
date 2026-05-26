import pandas as pd
import os
import sys

# Standard 11 column headers
ELEVEN_COLUMN_HEADERS = [
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
    "Name of agent",
]

def merge_sheets():
    file1 = r"E:\Internship\PocketFM\books_collection_with_authors.xlsx"
    file2 = r"E:\Internship\PocketFM\NewLeafLiterary_Authors_Books.xlsx"
    out_file = r"E:\Internship\PocketFM\New_Leaf_Literary_Merged.xlsx"
    
    print(f"Loading {file1}...")
    df1 = pd.read_excel(file1)
    # Ensure standard names before merge
    if "Book Name" in df1.columns and "Author Name" in df1.columns:
        df1 = df1.rename(columns={"Book Name": "Name of Series"})
        
    print(f"Loading {file2}...")
    df2 = pd.read_excel(file2)
    if "Book Name" in df2.columns and "Author Name" in df2.columns:
        df2 = df2.rename(columns={"Book Name": "Name of Series"})
        
    print("Merging dataframes...")
    merged_df = pd.concat([df1, df2], ignore_index=True)
    
    # Drop duplicates just in case there's overlap between the two sheets
    # so we don't end up with redundant rows. The user said "dont lose out on any data"
    # dropping exact duplicates is standard.
    merged_df = merged_df.drop_duplicates(subset=["Name of Series", "Author Name"])
    
    print(f"Total unique rows after merge: {len(merged_df)}")
    
    # Add missing columns
    for col in ELEVEN_COLUMN_HEADERS:
        if col not in merged_df.columns:
            if col == "Publisher":
                merged_df[col] = "New Leaf Literary"
            else:
                merged_df[col] = ""
                
    # Reorder to exact 11 columns, preserving any extra columns at the end if they exist (they shouldn't)
    final_cols = ELEVEN_COLUMN_HEADERS + [c for c in merged_df.columns if c not in ELEVEN_COLUMN_HEADERS]
    merged_df = merged_df[final_cols]
    
    # Fill NA
    merged_df = merged_df.fillna("")
    
    print(f"Saving merged sheet to {out_file}...")
    merged_df.to_excel(out_file, index=False)
    
    try:
        sys.path.append(r"E:\Internship\PocketFM\backend")
        from apply_jra_style import apply_styling
        apply_styling(out_file)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    import subprocess
    subprocess.Popen(["start", out_file], shell=True)
    print("ALL DONE!")

if __name__ == '__main__':
    merge_sheets()
