import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

FILE1 = r"E:\Internship\PocketFM\books_and_authors_from_image.xlsx"
FILE2 = r"E:\Internship\PocketFM\books_and_authors_from_image_backup.xlsx"

def merge_and_dedup():
    print("Loading both sheets...")
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    
    if os.path.exists(FILE1):
        df1 = pd.read_excel(FILE1)
        
    if os.path.exists(FILE2):
        df2 = pd.read_excel(FILE2)
        
    # Merge both sheets
    merged_df = pd.concat([df1, df2], ignore_index=True)
    
    original_len = len(merged_df)
    print(f"Total rows before deduplication: {original_len}")
    
    # Remove duplicates based on 'Name of Series'
    # Keeping 'first' keeps the most fully-scraped version if they were added chronologically, or we can just sort
    # Actually, the ones appended later might have more info? The 3-book scraper has '1' primary books and 'N/A' if missing,
    # The original aggressive scraper has the actual metrics. 
    # Let's sort so rows with actual numbers come first
    # A simple way to prioritize rows with real data is to sort by 'Rating (out of 5) of Primary Book 1' (so 'N/A' goes to bottom if descending)
    
    merged_df['Rating_Sort'] = merged_df['Rating (out of 5) of Primary Book 1'].replace('N/A', 0)
    merged_df['Rating_Sort'] = pd.to_numeric(merged_df['Rating_Sort'], errors='coerce').fillna(0)
    
    merged_df = merged_df.sort_values(by='Rating_Sort', ascending=False)
    
    merged_df = merged_df.drop_duplicates(subset=['Name of Series'], keep='first')
    
    # Drop the temporary sort column
    merged_df = merged_df.drop(columns=['Rating_Sort'])
    
    final_len = len(merged_df)
    print(f"Total unique books after deduplication: {final_len}")
    
    # Save to the main file
    print(f"Saving merged sheet to {FILE1}...")
    merged_df.to_excel(FILE1, index=False)
    
    # Apply styling
    try:
        from apply_jra_style import apply_styling
        apply_styling(FILE1)
        print("Styling applied.")
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    # Remove the backup to avoid confusion
    if os.path.exists(FILE2):
        os.remove(FILE2)
        print(f"Removed backup file: {FILE2}")
        
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", FILE1], shell=True)
    print("All done!")

if __name__ == '__main__':
    merge_and_dedup()
