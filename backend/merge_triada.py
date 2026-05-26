import pandas as pd
import os
import sys

EXCEL_FILE = r"E:\Internship\PocketFM\Triada_Upcoming_Books (2).xlsx"
OUTPUT_FILE = r"E:\Internship\PocketFM\Triada_Merged.xlsx"

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

def load_sheet(xls, sheet_name, skiprows):
    df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=skiprows)
    return df

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"File not found: {EXCEL_FILE}")
        return

    print("Loading sheets...")
    xls = pd.ExcelFile(EXCEL_FILE)
    
    # Based on our inspection:
    # 'All Titles': row index 2 has headers (skiprows=2)
    # 'Romantasy & Fantasy': row index 1 has headers (skiprows=1)
    # 'Recent Releases': row index 2 has headers (skiprows=2)
    # 'All Romantasy (Both Pages)': row index 2 has headers (skiprows=2)
    
    df1 = load_sheet(xls, 'All Titles', 2)
    df2 = load_sheet(xls, 'Romantasy & Fantasy', 1)
    df3 = load_sheet(xls, 'Recent Releases', 2)
    df4 = load_sheet(xls, 'All Romantasy (Both Pages)', 2)
    
    all_dfs = [df1, df2, df3, df4]
    
    merged_rows = []
    
    for df in all_dfs:
        for _, row in df.iterrows():
            title = str(row.get('Title', '')).strip()
            author = str(row.get('Author(s)', '')).strip()
            
            if not title or title.lower() == 'nan':
                continue
                
            merged_rows.append({
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
            
    final_df = pd.DataFrame(merged_rows)
    
    # Ensure 11 columns
    final_df = final_df.reindex(columns=ELEVEN_COLUMN_HEADERS)
    
    print(f"Total rows before deduplication: {len(final_df)}")
    
    # Drop duplicates
    final_df = final_df.drop_duplicates(subset=["Name of Series", "Author Name"], keep='first')
    
    print(f"Total rows after deduplication: {len(final_df)}")
    
    print(f"Saving merged Excel to {OUTPUT_FILE}...")
    final_df.to_excel(OUTPUT_FILE, index=False)
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
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
