import pandas as pd
import os

def compare_excel_sheets(old_path, new_path):
    print(f"Reading old file: {old_path}")
    old_df = pd.read_excel(old_path)
    
    print(f"Reading new file: {new_path}")
    new_df = pd.read_excel(new_path)
    
    # Identify relevant columns
    # Based on previous check, they have 'Title', 'Subgenre', and 'Sub Genre'
    # We'll use 'Title' and 'Subgenre' (standardizing names if needed)
    
    def get_clean_col(df, possible_names):
        for name in possible_names:
            if name in df.columns:
                return name
        return None

    title_col_old = get_clean_col(old_df, ['Title', 'title'])
    subgenre_col_old = get_clean_col(old_df, ['Subgenre', 'Sub Genre', 'subgenre'])
    
    title_col_new = get_clean_col(new_df, ['Title', 'title'])
    subgenre_col_new = get_clean_col(new_df, ['Subgenre', 'Sub Genre', 'subgenre'])

    if not title_col_old or not title_col_new:
        print("Error: Could not find 'Title' column in one or both files.")
        return

    # Clean data: drop rows where Title is NaN
    old_df = old_df.dropna(subset=[title_col_old])
    new_df = new_df.dropna(subset=[title_col_new])

    # Convert to sets for quick comparison
    old_titles = set(old_df[title_col_old].astype(str).str.strip().str.lower())
    new_titles = set(new_df[title_col_new].astype(str).str.strip().str.lower())

    missing_titles = old_titles - new_titles

    print("\n--- Title Comparison Results ---")
    print(f"Old file unique titles: {len(old_titles)}")
    print(f"New file unique titles: {len(new_titles)}")
    
    if not missing_titles:
        print("SUCCESS: All titles from the old sheet are present in the new sheet.")
    else:
        print(f"WARNING: Found {len(missing_titles)} titles in the old sheet that are MISSING in the new sheet.")
        print("First 10 missing titles:")
        for t in list(missing_titles)[:10]:
            print(f" - {t}")

    # Sub-genre comparison
    if subgenre_col_old and subgenre_col_new:
        print("\n--- Sub-genre Comparison Results ---")
        # Create pairs of (Title, Subgenre)
        old_pairs = set(zip(
            old_df[title_col_old].astype(str).str.strip().str.lower(),
            old_df[subgenre_col_old].astype(str).str.strip().str.lower()
        ))
        new_pairs = set(zip(
            new_df[title_col_new].astype(str).str.strip().str.lower(),
            new_df[subgenre_col_new].astype(str).str.strip().str.lower()
        ))

        missing_pairs = old_pairs - new_pairs
        
        if not missing_pairs:
            print("SUCCESS: All Title/Sub-genre combinations from the old sheet are present in the new sheet.")
        else:
            print(f"WARNING: Found {len(missing_pairs)} Title/Sub-genre combinations in the old sheet that are MISSING in the new sheet.")
            print("First 10 missing pairs (Title | Subgenre):")
            for t, s in list(missing_pairs)[:10]:
                print(f" - {t} | {s}")
    else:
        print("\nSkipping sub-genre comparison as columns were not found consistently.")

if __name__ == "__main__":
    old_file = "Horror - Amazon Keyword Crawl.xlsx"
    new_file = "Horror_-_Amazon_Keyword_Crawl (3).xlsx"
    
    if os.path.exists(old_file) and os.path.exists(new_file):
        compare_excel_sheets(old_file, new_file)
    else:
        print(f"File missing. Old exists: {os.path.exists(old_file)}, New exists: {os.path.exists(new_file)}")
