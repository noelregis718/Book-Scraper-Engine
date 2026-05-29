import pandas as pd
import os

EXCEL_FILE = r"E:\Internship\PocketFM\MarsalLyon_Merged_Formatted.xlsx"

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
            
    # Set the values for Publisher and Name of agent
    df['Publisher'] = "Marsal Lyon Literary Agency"
    df['Name of agent'] = "Marsal and Kevan Lyon"

    print(f"Saving {EXCEL_FILE} with updated Publisher and Agent names...")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    print("ALL DONE!")

if __name__ == '__main__':
    main()
