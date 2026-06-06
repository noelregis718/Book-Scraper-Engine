import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\books_scraped_merged.xlsx"

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
            
    pub_col = "Publisher"
    agent_col = "Name of agent"

    if pub_col not in df.columns:
        df[pub_col] = ""
    if agent_col not in df.columns:
        df[agent_col] = ""

    # Fill all rows with the requested values
    df[pub_col] = "Dystel, Goderich & Bourret"
    df[agent_col] = "Michaela Whatnall"

    print(f"Saving {EXCEL_FILE}...")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("ALL DONE!")

if __name__ == '__main__':
    main()
