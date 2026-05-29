import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from style_romaunce import style_romaunce

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Romaunce_Books_Complete.xlsx")

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
            
    agent_col = "Name of agent"
    
    if agent_col in df.columns:
        df[agent_col] = "Antonia Tingle"
    else:
        print(f"Column '{agent_col}' not found.")
        return

    print(f"Saving {EXCEL_FILE} with Agent Name updated...")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        style_romaunce(EXCEL_FILE)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    print("ALL DONE!")

if __name__ == '__main__':
    main()
