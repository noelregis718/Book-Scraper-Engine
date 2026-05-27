import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\D4EO_Merged.xlsx"

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    agent_col = "Name of agent"
    publisher_col = "Publisher"
    
    if agent_col not in df.columns:
        df[agent_col] = "Robert (Bob) G. Diforio"
    else:
        for idx in range(len(df)):
            df.at[idx, agent_col] = "Robert (Bob) G. Diforio"
            
    if publisher_col not in df.columns:
        df[publisher_col] = "D4EO Literary Agency"
    else:
        for idx in range(len(df)):
            df.at[idx, publisher_col] = "D4EO Literary Agency"
            
    print(f"Saving {EXCEL_FILE} with publisher and agent names for all rows...")
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
