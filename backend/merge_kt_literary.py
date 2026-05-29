import pandas as pd
import os

INPUT_EXCEL = r"E:\Internship\PocketFM\KT_Literary_Agents_Page_Books.xlsx"
OUTPUT_EXCEL = r"E:\Internship\PocketFM\KT_Literary_Merged_Formatted.xlsx"

FINAL_COLUMNS = [
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
    if not os.path.exists(INPUT_EXCEL):
        print(f"Error: {INPUT_EXCEL} not found!")
        return

    print(f"Loading {INPUT_EXCEL}...")
    xls = pd.ExcelFile(INPUT_EXCEL)
    
    dfs = []
    for sheet_name in xls.sheet_names:
        df_sheet = pd.read_excel(xls, sheet_name)
        print(f"Loaded sheet '{sheet_name}' with {len(df_sheet)} rows.")
        dfs.append(df_sheet)
        
    # Merge both sheets without deleting any rows
    df_merged = pd.concat(dfs, ignore_index=True)
    print(f"Total merged rows: {len(df_merged)}")
    
    # Create the final formatted dataframe
    final_df = pd.DataFrame(columns=FINAL_COLUMNS)
    
    for _, row in df_merged.iterrows():
        # Get values safely
        book_title = row.get('Book Title')
        author = row.get('Author')
        agent = row.get('Agent', 'N/A')
        
        # If both title and author are completely empty, skip
        if pd.isna(book_title) and pd.isna(author):
            continue
            
        new_row = {
            "Name of Series": book_title,
            "Author Name": author,
            "Publisher": "KT Literary Agency",
            "GoodReads series link": "N/A",
            "Number of PRIMARY books in the series": "N/A",
            "Rating (out of 5) of Primary Book 1": "N/A",
            "Ratings (#) of Primary Book 1": "N/A",
            "Synopsis (if available)": "N/A",
            "Romantasy = Yes or No?": "N/A",
            "Romantasy Sub-Genre of series": "",
            "Name of agent": agent if pd.notna(agent) else "N/A"
        }
        final_df = pd.concat([final_df, pd.DataFrame([new_row])], ignore_index=True)
        
    print(f"Saving formatted file to {OUTPUT_EXCEL} with {len(final_df)} rows...")
    final_df.to_excel(OUTPUT_EXCEL, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(OUTPUT_EXCEL)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    print("ALL DONE!")

if __name__ == '__main__':
    main()
