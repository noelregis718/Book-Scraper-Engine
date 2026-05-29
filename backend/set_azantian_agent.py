import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from classify_azantian_final import apply_azantian_style

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Azantian_LitAgency_Combined_Formatted.xlsx")

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
            
    if "Publisher" in df.columns:
        df["Publisher"] = "Azantian Literary Agency"
        
    if "Name of agent" in df.columns:
        df["Name of agent"] = "Jennifer Azantian"

    print(f"Saving {EXCEL_FILE} with updated Publisher and Agent names...")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        apply_azantian_style(EXCEL_FILE)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    print("ALL DONE!")

if __name__ == '__main__':
    main()
