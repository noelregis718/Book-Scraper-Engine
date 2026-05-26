import pandas as pd
import os

EXCEL_FILE = r"E:\Internship\PocketFM\new_books_master_list_perez_literary_scraped.xlsx"

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    # Fill columns
    df['Publisher'] = 'Perez Literary'
    df['Name of agent'] = 'Kristina Perez'
    
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
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
