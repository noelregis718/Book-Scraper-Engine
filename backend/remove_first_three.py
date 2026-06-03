import pandas as pd
import os

EXCEL_FILE = r"E:\Internship\PocketFM\corvisiero_merged.xlsx"

def remove_first_three():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    # Remove the first 3 rows (index 0, 1, 2)
    df = df.iloc[3:].reset_index(drop=True)
    
    print(f"Saving {EXCEL_FILE} with first 3 rows removed...")
    df.to_excel(EXCEL_FILE, index=False)
    print("Done!")

if __name__ == '__main__':
    remove_first_three()
