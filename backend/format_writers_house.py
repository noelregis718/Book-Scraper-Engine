import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = r"E:\Internship\PocketFM\WritersHouse_Adult_Bestsellers_Complete (1).xlsx"
OUTPUT_FILE = r"E:\Internship\PocketFM\WritersHouse_Merged.xlsx"

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
    "Name of agent"
]

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found!")
        return

    print(f"Loading {INPUT_FILE}...")
    df_input = pd.read_excel(INPUT_FILE, sheet_name="Adult Bestsellers")
    
    new_rows = []
    
    for _, row in df_input.iterrows():
        title = str(row.get('Book Title', '')).strip()
        author = str(row.get('Author', '')).strip()
        
        if not title or title.lower() == 'nan':
            continue
            
        new_rows.append({
            "Name of Series": title,
            "Author Name": author,
            "Publisher": "Writers House",
            "GoodReads series link": "",
            "Number of PRIMARY books in the series": "",
            "Rating (out of 5) of Primary Book 1": "",
            "Ratings (#) of Primary Book 1": "",
            "Synopsis (if available)": "",
            "Romantasy = Yes or No?": "",
            "Romantasy Sub-Genre of series": "",
            "Name of agent": ""
        })
        
    final_df = pd.DataFrame(new_rows)
    final_df = final_df.reindex(columns=ELEVEN_COLUMN_HEADERS)
    
    print(f"Total rows before deduplication: {len(final_df)}")
    
    # Drop duplicates to ensure a clean list
    final_df = final_df.drop_duplicates(subset=["Name of Series", "Author Name"], keep='first')
    
    print(f"Total rows after deduplication: {len(final_df)}")
    
    print(f"Saving merged Excel to {OUTPUT_FILE}...")
    final_df.to_excel(OUTPUT_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(OUTPUT_FILE)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")

    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", OUTPUT_FILE], shell=True)
    print("ALL DONE!")

if __name__ == '__main__':
    main()
