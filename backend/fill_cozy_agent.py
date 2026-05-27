import pandas as pd
import os

EXCEL_FILE = r"E:\Internship\PocketFM\CozyRomantasy_Merged.xlsx"

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    print("Setting 'Name of agent' to 'KD Fraser' for all rows...")
    df['Name of agent'] = 'KD Fraser'
    
    print("Saving file...")
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
    print("Done!")

if __name__ == '__main__':
    main()
