import pandas as pd
import os
import sys

MERGED_FILE = r"E:\Internship\PocketFM\Triada_Merged.xlsx"
BACKLIST_FILE = r"E:\Internship\PocketFM\Triada_Backlist_Titles.xlsx"

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
    if not os.path.exists(MERGED_FILE):
        print(f"Error: {MERGED_FILE} not found!")
        return
        
    if not os.path.exists(BACKLIST_FILE):
        print(f"Error: {BACKLIST_FILE} not found!")
        return

    print("Loading existing merged file...")
    merged_df = pd.read_excel(MERGED_FILE)
    
    print("Loading backlist titles...")
    backlist_df = pd.read_excel(BACKLIST_FILE, sheet_name="Backlist Titles", skiprows=2)
    
    new_rows = []
    
    for _, row in backlist_df.iterrows():
        title = str(row.get('Title', '')).strip()
        author = str(row.get('Author(s)', '')).strip()
        
        if not title or title.lower() == 'nan':
            continue
            
        new_rows.append({
            "Name of Series": title,
            "Author Name": author,
            "Publisher": "Triada US Literary Agency",
            "GoodReads series link": "",
            "Number of PRIMARY books in the series": "",
            "Rating (out of 5) of Primary Book 1": "",
            "Ratings (#) of Primary Book 1": "",
            "Synopsis (if available)": "",
            "Romantasy = Yes or No?": "",
            "Romantasy Sub-Genre of series": "",
            "Name of agent": ""
        })
        
    new_df = pd.DataFrame(new_rows)
    new_df = new_df.reindex(columns=ELEVEN_COLUMN_HEADERS)
    
    print(f"Total existing rows: {len(merged_df)}")
    print(f"Total new backlist rows: {len(new_df)}")
    
    final_df = pd.concat([merged_df, new_df], ignore_index=True)
    
    print(f"Total rows before deduplication: {len(final_df)}")
    
    # Drop duplicates
    final_df = final_df.drop_duplicates(subset=["Name of Series", "Author Name"], keep='first')
    
    print(f"Total rows after deduplication: {len(final_df)}")
    
    print(f"Saving fully merged Excel to {MERGED_FILE}...")
    final_df.to_excel(MERGED_FILE, index=False)
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from apply_jra_style import apply_styling
        apply_styling(MERGED_FILE)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")

    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", MERGED_FILE], shell=True)
    print("ALL DONE!")

if __name__ == '__main__':
    main()
