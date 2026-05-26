import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

EXCEL_FILE = r"E:\Internship\PocketFM\storm_literary_agency_scraped.xlsx"

def update_publisher_and_agent():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return
        
    df = pd.read_excel(EXCEL_FILE)
    
    # Force set publisher and agent across all rows
    df["Publisher"] = "Storm Literary Agency"
    df["Name of agent"] = "Victoria Selvaggio"
    
    print("--- Saving Excel ---")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        apply_styling(EXCEL_FILE)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("ALL DONE!")

if __name__ == '__main__':
    update_publisher_and_agent()
