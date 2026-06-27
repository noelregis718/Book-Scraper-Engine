import pandas as pd
import os
import glob
from collections import defaultdict, Counter
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
from apply_jra_style import apply_styling

def run():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tracker_path = os.path.join(base_dir, 'Publishers_Tracker.xlsx')
    
    print("Loading Publishers_Tracker.xlsx...")
    df_tracker = pd.read_excel(tracker_path)
    
    # Dictionaries to store aggregation data
    # pub_name (lowercase) -> data
    pub_authors = defaultdict(set)
    pub_titles = defaultdict(set)
    pub_genres = defaultdict(list)
    
    # 1. Parse individual Amazon Keyword files
    keyword_files = glob.glob(os.path.join(base_dir, 'Amazon Keyword - *.xlsx'))
    print(f"Scanning {len(keyword_files)} keyword files for metrics...")
    
    for fpath in keyword_files:
        genre_name = os.path.basename(fpath).replace('Amazon Keyword - ', '').replace('.xlsx', '').strip()
        try:
            df = pd.read_excel(fpath)
            pub_col = next((c for c in df.columns if str(c).lower() == 'publisher'), None)
            author_col = next((c for c in df.columns if 'author' in str(c).lower()), None)
            title_col = next((c for c in df.columns if 'title' in str(c).lower()), None)
            
            if pub_col:
                for idx, row in df.iterrows():
                    pub = str(row[pub_col]).strip()
                    if pub and pub.lower() not in ['nan', 'none']:
                        pub_key = pub.lower()
                        # Add Genre
                        pub_genres[pub_key].append(genre_name)
                        # Add Author
                        if author_col and pd.notna(row[author_col]):
                            pub_authors[pub_key].add(str(row[author_col]).strip().lower())
                        # Add Title
                        if title_col and pd.notna(row[title_col]):
                            pub_titles[pub_key].add(str(row[title_col]).strip().lower())
                            
        except Exception as e:
            print(f"Error reading {fpath}: {e}")

    # 2. Parse the Combined File (to ensure we don't miss anything)
    combined_file = os.path.join(base_dir, 'Romantasy Combined_Amazon Keyword searches_Claude Mapping.xlsx')
    print("Scanning combined Romantasy mapping file...")
    try:
        xl = pd.ExcelFile(combined_file)
        for sheet in xl.sheet_names:
            if sheet in ['Publisher Band Definitions', 'Checks', 'Enrichment Summary', 'Publishers Bands']:
                continue
            df = xl.parse(sheet)
            pub_col = next((c for c in df.columns if str(c).lower() == 'publisher'), None)
            author_col = next((c for c in df.columns if 'author' in str(c).lower()), None)
            title_col = next((c for c in df.columns if 'title' in str(c).lower()), None)
            
            if pub_col:
                for idx, row in df.iterrows():
                    pub = str(row[pub_col]).strip()
                    if pub and pub.lower() not in ['nan', 'none']:
                        pub_key = pub.lower()
                        pub_genres[pub_key].append(sheet)
                        if author_col and pd.notna(row[author_col]):
                            pub_authors[pub_key].add(str(row[author_col]).strip().lower())
                        if title_col and pd.notna(row[title_col]):
                            pub_titles[pub_key].add(str(row[title_col]).strip().lower())
    except Exception as e:
        print(f"Error reading {combined_file}: {e}")

    # 3. Apply to Tracker
    print("Writing aggregated metrics to tracker...")
    
    authors_col_name = "Number of authors in that publishing house"
    titles_col_name = "Number of titles published per year"
    genres_col_name = "Genres they specialise in"
    rev_col_name = "Revenue of these publishing houses"
    year_col_name = "Year of establishment of these"
    
    for idx, row in df_tracker.iterrows():
        pub_name = str(row['Publisher Name']).strip()
        pub_key = pub_name.lower()
        
        # Populate Internal Data
        if pub_key in pub_authors and len(pub_authors[pub_key]) > 0:
            df_tracker.at[idx, authors_col_name] = len(pub_authors[pub_key])
            
        if pub_key in pub_titles and len(pub_titles[pub_key]) > 0:
            df_tracker.at[idx, titles_col_name] = f"{len(pub_titles[pub_key])} (In Dataset)"
            
        if pub_key in pub_genres and len(pub_genres[pub_key]) > 0:
            most_common = Counter(pub_genres[pub_key]).most_common(2)
            genre_str = ", ".join([g[0] for g in most_common])
            df_tracker.at[idx, genres_col_name] = genre_str
            
        # Populate External Corporate Data defaults for Self-Pub/Junk
        cat = str(row.get('Category', ''))
        if cat in ["Self-Published", "Unknown (Junk)"]:
            df_tracker.at[idx, rev_col_name] = "N/A"
            df_tracker.at[idx, year_col_name] = "N/A"
            
    # Fill remaining NaNs to clean up
    df_tracker.fillna("", inplace=True)
    
    print("Saving updated tracker...")
    df_tracker.to_excel(tracker_path, index=False)
    
    try:
        apply_styling(tracker_path)
        print("Success! Metrics aggregated and styled.")
    except Exception as e:
        print(f"Error styling: {e}")

if __name__ == '__main__':
    run()
