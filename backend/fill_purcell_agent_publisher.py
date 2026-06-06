import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\books_authors_latest_batch.xlsx"

def fill_publisher_agent():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: Could not find {EXCEL_FILE}")
        return
        
    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    # Fill in the columns for all rows
    if "Publisher" not in df.columns:
        df["Publisher"] = "The Purcell Agency"
    else:
        df["Publisher"] = "The Purcell Agency"
        
    if "Name of agent" not in df.columns:
        df["Name of agent"] = "Tina Purcell Schwartz"
    else:
        df["Name of agent"] = "Tina Purcell Schwartz"
        
    df.to_excel(EXCEL_FILE, index=False)
    print("Columns filled successfully.")
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
        print("Styling applied.")
    except Exception as e:
        print(f"Styling error: {e}")
        
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("All done!")

if __name__ == '__main__':
    fill_publisher_agent()
